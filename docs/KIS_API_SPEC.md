# KIS Open API — Domestic Stock REST 스펙 (kis_client 구현 근거)

> 본 문서는 5개 병렬 리서치 결과를 종합한 단일 정본(canonical) 구현 스펙이다. 구현 대상 파일: `app/brokers/kis/kis_client.py`.
> TR ID는 공식 KIS GitHub `koreainvestment/open-trading-api`의 **현행(2025) 샘플**을 1차 근거로 한다. 레거시 TR ID는 `## 불일치/저신뢰 경고`에 별도 명시.

## 공통 기반 (Base / Auth / Envelope)

| 항목 | 값 |
|------|-----|
| Base URL (실전 prod) | `https://openapi.koreainvestment.com:9443` |
| Base URL (모의 paper) | `https://openapivts.koreainvestment.com:29443` |
| OAuth 토큰 발급 | `POST /oauth2/tokenP` (body: `grant_type=client_credentials`, `appkey`, `appsecret`) → `access_token`, `expires_in`(~86400s) |
| Hashkey | `POST /uapi/hashkey` (주문 JSON body 그대로 POST → 응답의 `HASH` 필드를 `hashkey` 헤더로 사용). **선택 사항** |
| 토큰 재사용 | 6시간 내 재요청 시 동일 토큰 반환 |

토큰 발급은 `tr_id`를 사용하지 않는다. 모의/실전 모두 동일 경로 `/oauth2/tokenP`를 쓰며, base URL과 endpoint별 TR ID로만 환경을 구분한다.

---

## 1. 현재가 시세 (Stock Current Price Quote) [v1_국내주식-008]

**HTTP**: `GET /uapi/domestic-stock/v1/quotations/inquire-price`

### tr_id

| 환경 | TR ID |
|------|-------|
| 모의 (paper) | `FHKST01010100` |
| 실전 (prod) | `FHKST01010100` |

> 시세(`FH…`) TR은 paper/prod가 **동일**하다. (`T/J/C` 접두만 V-prefix 변환되며 `F`는 변환 대상이 아님)

### 필수 헤더

| 헤더 | 값 |
|------|-----|
| Content-Type | `application/json` |
| authorization | `Bearer {access_token}` |
| appkey | `{KIS_APP_KEY}` |
| appsecret | `{KIS_APP_SECRET}` |
| tr_id | `FHKST01010100` |
| custtype | `P` (개인/법인=P, 제휴사=B) |
| tr_cont | `""` (단건 조회 시 빈 문자열) |

> 시세는 GET 조회이므로 hashkey 불필요.

### 요청 필드

| name | 위치 | 의미 | 예시 |
|------|------|------|------|
| FID_COND_MRKT_DIV_CODE | query | 조건 시장 분류 코드. J=KRX, NX=NXT, UN=통합 | `J` |
| FID_INPUT_ISCD | query | 입력 종목코드(6자리). ETN은 앞에 `Q` | `005930` |

### 응답 필드

| name | container | 의미 |
|------|-----------|------|
| **stck_prpr** | output | **주식 현재가 (현재가 PRIMARY 필드 — 문자열, int/float 캐스팅 필요)** |
| prdy_vrss | output | 전일 대비 |
| prdy_vrss_sign | output | 전일 대비 부호 (1 상한, 2 상승, 3 보합, 4 하한, 5 하락) |
| prdy_ctrt | output | 전일 대비율(%) |
| stck_oprc | output | 시가 |
| stck_hgpr | output | 고가 |
| stck_lwpr | output | 저가 |
| stck_sdpr | output | 기준가(전일 종가) |
| acml_vol | output | 누적 거래량 |
| acml_tr_pbmn | output | 누적 거래 대금 |
| stck_shrn_iscd | output | 단축 종목코드 |
| per | output | PER |
| pbr | output | PBR |
| w52_hgpr | output | 52주 최고가 |
| w52_lwpr | output | 52주 최저가 |

> 응답은 단일 객체 `output` 컨테이너. (output1/output2 아님)

---

## 2. 주식잔고조회 (Domestic Stock Balance / Holdings Inquiry) [v1_국내주식-006]

**HTTP**: `GET /uapi/domestic-stock/v1/trading/inquire-balance`

### tr_id

| 환경 | TR ID |
|------|-------|
| 모의 (paper) | `VTTC8434R` |
| 실전 (prod) | `TTTC8434R` |

### 필수 헤더

| 헤더 | 값 |
|------|-----|
| content-type | `application/json; charset=utf-8` |
| authorization | `Bearer {access_token}` |
| appkey | `{KIS_APP_KEY}` |
| appsecret | `{KIS_APP_SECRET}` |
| tr_id | `TTTC8434R` (prod) / `VTTC8434R` (paper) |
| custtype | `P` |
| tr_cont | `""` 첫 호출, 연속조회 시 `N` |

> GET 조회이므로 hashkey 불필요.

### 요청 필드

| name | 위치 | 의미 | 예시 |
|------|------|------|------|
| CANO | query | 종합계좌번호 (8-2 계좌의 앞 8자리) | `12345678` |
| ACNT_PRDT_CD | query | 계좌상품코드 (뒤 2자리) | `01` |
| AFHR_FLPR_YN | query | 시간외단일가·거래소여부. N=기본, Y=시간외단일가, X=NXT | `N` |
| OFL_YN | query | 오프라인여부 (공란) | `""` |
| INQR_DVSN | query | 조회구분. 01=대출일별, 02=종목별 | `01` |
| UNPR_DVSN | query | 단가구분 (01) | `01` |
| FUND_STTL_ICLD_YN | query | 펀드결제분포함여부. N=제외, Y=포함 | `N` |
| FNCG_AMT_AUTO_RDPT_YN | query | 융자금액자동상환여부 | `N` |
| PRCS_DVSN | query | 처리구분. 00=전일매매포함, 01=미포함 | `00` |
| CTX_AREA_FK100 | query | 연속조회검색조건100 (첫 호출 공란, 연속 시 응답값 echo) | `""` |
| CTX_AREA_NK100 | query | 연속조회키100 (첫 호출 공란, 연속 시 응답값 echo) | `""` |

### 응답 필드

| name | container | 의미 |
|------|-----------|------|
| rt_cd | root | 성공실패여부 (0=성공) |
| msg_cd | root | 응답코드 |
| msg1 | root | 응답메시지 |
| ctx_area_fk100 | root | 연속조회검색조건100 (다음 페이지 CTX_AREA_FK100로 feed) |
| ctx_area_nk100 | root | 연속조회키100 (다음 페이지 CTX_AREA_NK100로 feed) |
| **pdno** | output1 | **상품번호(종목코드)** |
| prdt_name | output1 | 상품명(종목명) |
| **hldg_qty** | output1 | **보유수량** |
| ord_psbl_qty | output1 | 주문가능수량 |
| **pchs_avg_pric** | output1 | **매입평균가격** |
| pchs_amt | output1 | 매입금액 |
| **prpr** | output1 | **현재가** |
| **evlu_amt** | output1 | **평가금액(시장가치)** |
| **evlu_pfls_amt** | output1 | **평가손익금액** |
| evlu_pfls_rt | output1 | 평가손익율(%) |
| evlu_erng_rt | output1 | 평가수익율(%) |
| fltt_rt | output1 | 등락율(%) |
| bfdy_cprs_icdc | output1 | 전일대비증감 |
| bfdy_buy_qty | output1 | 전일매수수량 |
| thdt_buyqty | output1 | 금일매수수량 |
| loan_dt | output1 | 대출일자 |
| loan_amt | output1 | 대출금액 |
| expd_dt | output1 | 만기일자 |
| stck_loan_unpr | output1 | 주식대출단가 |
| dnca_tot_amt | output2 | 예수금총금액 |
| nxdy_excc_amt | output2 | 익일정산금액 |
| prvs_rcdl_excc_amt | output2 | 가수도정산금액 |
| scts_evlu_amt | output2 | 유가평가금액 |
| tot_evlu_amt | output2 | 총평가금액 |
| nass_amt | output2 | 순자산금액 |
| pchs_amt_smtl_amt | output2 | 매입금액합계금액 |
| evlu_amt_smtl_amt | output2 | 평가금액합계금액 |
| evlu_pfls_smtl_amt | output2 | 평가손익합계금액 |
| tot_loan_amt | output2 | 총대출금액 |
| bfdy_tot_asst_evlu_amt | output2 | 전일총자산평가금액 |
| asst_icdc_amt | output2 | 자산증감액 |
| asst_icdc_erng_rt | output2 | 자산증감수익율(%) |

> `output1` = 종목별 보유 잔고 배열, `output2` = 계좌 요약 단일 객체.
> 페이지당 한도: 실전 최대 50행, 모의 최대 20행 (초과분은 연속조회).

---

## 3. 현금주문 매수 (Cash BUY) [주식주문(현금)]

**HTTP**: `POST /uapi/domestic-stock/v1/trading/order-cash`

### tr_id

| 환경 | TR ID |
|------|-------|
| 모의 (paper) | `VTTC0012U` |
| 실전 (prod) | `TTTC0012U` |

### 필수 헤더

| 헤더 | 값 |
|------|-----|
| content-type | `application/json; charset=utf-8` |
| authorization | `Bearer {access_token}` |
| appkey | `{KIS_APP_KEY}` |
| appsecret | `{KIS_APP_SECRET}` |
| tr_id | `TTTC0012U` (prod) / `VTTC0012U` (paper) |
| custtype | `P` |
| tr_cont | `""` |
| hashkey | 선택(OPTIONAL) — 공식 샘플은 미사용 |

### 요청 필드

| name | 위치 | 의미 | 예시 |
|------|------|------|------|
| CANO | body | 종합계좌번호 (앞 8자리) | `12345678` |
| ACNT_PRDT_CD | body | 계좌상품코드 (뒤 2자리) | `01` |
| PDNO | body | 상품번호(종목코드, 6자리; ETN 7자리) | `005930` |
| ORD_DVSN | body | 주문구분 (00=지정가, 01=시장가; 아래 코드표 참조) | `00` |
| ORD_QTY | body | 주문수량 (**문자열**) | `1` |
| ORD_UNPR | body | 주문단가 (**문자열**; 시장가는 `"0"`) | `70000` |
| EXCG_ID_DVSN_CD | body | 거래소ID구분코드 (KRX/NXT/SOR). 현행 스키마 필수 | `KRX` |
| SLL_TYPE | body | 매도유형 — 매수 시 공란 | `""` |
| CNDT_PRIC | body | 조건가격 (스탑지정가용, 선택) | `""` |

### 응답 필드

| name | container | 의미 |
|------|-----------|------|
| rt_cd | root | 성공실패여부 ('0'=성공) |
| msg_cd | root | 응답코드 |
| msg1 | root | 응답메시지 |
| KRX_FWDG_ORD_ORGNO | output | 한국거래소전송주문조직번호 (정정/취소 시 ODNO와 함께 필요) |
| **ODNO** | output | **주문번호 (정정/취소 시 ORGN_ODNO로 사용)** |
| ORD_TMD | output | 주문시각 (HHMMSS) |

### ORD_DVSN 코드

| 코드 | 의미 |
|------|------|
| **00** | **지정가 (limit)** |
| **01** | **시장가 (market) → ORD_UNPR="0"** |
| 02 | 조건부지정가 |
| 03 | 최유리지정가 |
| 04 | 최우선지정가 |
| 05 | 장전시간외 |
| 06 | 장후시간외 |
| 07 | 시간외단일가 |

---

## 4. 현금주문 매도 (Cash SELL) [주식주문(현금)]

**HTTP**: `POST /uapi/domestic-stock/v1/trading/order-cash` (매수와 동일 경로/메서드/body 구조)

### tr_id

| 환경 | TR ID |
|------|-------|
| 모의 (paper) | `VTTC0011U` |
| 실전 (prod) | `TTTC0011U` |

### 필수 헤더

매수와 동일. `tr_id`만 `TTTC0011U` (prod) / `VTTC0011U` (paper).

### 요청 필드

매수와 동일하되 매도 전용 필드 사용:

| name | 위치 | 의미 | 예시 |
|------|------|------|------|
| CANO | body | 종합계좌번호 | `12345678` |
| ACNT_PRDT_CD | body | 계좌상품코드 | `01` |
| PDNO | body | 상품번호(종목코드) | `005930` |
| ORD_DVSN | body | 주문구분 (00=지정가, 01=시장가) | `00` |
| ORD_QTY | body | 주문수량 (문자열) | `1` |
| ORD_UNPR | body | 주문단가 (문자열; 시장가 `"0"`) | `70000` |
| EXCG_ID_DVSN_CD | body | 거래소ID구분코드 (KRX/NXT/SOR) | `KRX` |
| SLL_TYPE | body | 매도유형 — 01=일반매도, 02=임의매매, 05=대차매도 | `01` |
| CNDT_PRIC | body | 조건가격 (선택) | `""` |

### 응답 필드

매수와 동일 (`rt_cd`, `msg_cd`, `msg1` / `KRX_FWDG_ORD_ORGNO`, **`ODNO`**, `ORD_TMD` in `output`).

---

## 5. 주문정정취소 (Order Revise / Cancel)

**HTTP**: `POST /uapi/domestic-stock/v1/trading/order-rvsecncl`

### tr_id

| 환경 | TR ID |
|------|-------|
| 모의 (paper) | `VTTC0013U` |
| 실전 (prod) | `TTTC0013U` |

### 필수 헤더

| 헤더 | 값 |
|------|-----|
| content-type | `application/json; charset=utf-8` |
| authorization | `Bearer {access_token}` |
| appkey | `{KIS_APP_KEY}` |
| appsecret | `{KIS_APP_SECRET}` |
| tr_id | `TTTC0013U` (prod) / `VTTC0013U` (paper) |
| custtype | `P` (선택) |
| hashkey | 선택(OPTIONAL) |

### 요청 필드

| name | 위치 | 의미 | 예시 |
|------|------|------|------|
| CANO | body | 종합계좌번호 (앞 8자리) | `12345678` |
| ACNT_PRDT_CD | body | 계좌상품코드 (뒤 2자리) | `01` |
| KRX_FWDG_ORD_ORGNO | body | 한국거래소전송주문조직번호 (원주문 응답의 값) | `06010` |
| ORGN_ODNO | body | 원주문번호 (주문 시 받은 ODNO) | `0000117057` |
| ORD_DVSN | body | 주문구분 (취소는 원주문 구분 mirror) | `00` |
| RVSE_CNCL_DVSN_CD | body | 정정취소구분코드 — 01=정정, 02=취소 | `02` |
| ORD_QTY | body | 주문수량 (전량 시 `0` 가능) | `0` |
| ORD_UNPR | body | 주문단가 (취소는 `0`, 정정은 신규가) | `0` |
| QTY_ALL_ORD_YN | body | 잔량전부주문여부 — Y=전량, N=일부 | `Y` |
| EXCG_ID_DVSN_CD | body | 거래소ID구분코드 (KRX/NXT/SOR). 현행 스키마 필수 | `KRX` |
| CNDT_PRIC | body | 조건가격 (선택) | `""` |

### 응답 필드

| name | container | 의미 |
|------|-----------|------|
| rt_cd | root | 성공실패여부 (0=성공) |
| msg_cd | root | 응답코드 |
| msg1 | root | 응답메시지 |
| KRX_FWDG_ORD_ORGNO | output | 한국거래소전송주문조직번호 (echo) |
| **ODNO** | output | **정정/취소 주문에 새로 부여된 주문번호** |
| ORD_TMD | output | 주문시각 (HHMMSS) |

> **CRITICAL 워크플로**: 공식 문서는 정정/취소 호출 **전에 반드시 `inquire-psbl-rvsecncl`(주식정정취소가능주문조회)를 호출하여 `output > psbl_qty`(정정취소가능수량)를 확인**하도록 요구한다. 이미 체결완료된 주문은 정정/취소 불가. POST body 키는 모두 대문자.

---

## 6. 체결조회 (Order Fill-Status Inquiry)

체결 여부 확인은 두 endpoint 조합으로 한다. 미체결 주문의 정정취소가능수량은 `inquire-psbl-rvsecncl`, 명시적 체결/미체결 내역은 `inquire-daily-ccld`.

### 6-a. 주식정정취소가능주문조회 (Revisable/Cancelable Order Inquiry)

**HTTP**: `GET /uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl`

| 환경 | TR ID |
|------|-------|
| 모의 (paper) | **N/A** (paper 미지원 — 저신뢰. 경고 섹션 참조) |
| 실전 (prod) | `TTTC0084R` |

필수 헤더: `authorization`, `appkey`, `appsecret`, `tr_id=TTTC0084R`, `content-type: application/json; charset=utf-8`, `tr_cont`(페이지네이션).

**요청 필드**

| name | 위치 | 의미 | 예시 |
|------|------|------|------|
| CANO | query | 종합계좌번호 | `12345678` |
| ACNT_PRDT_CD | query | 계좌상품코드 | `01` |
| INQR_DVSN_1 | query | 조회구분1 — 0=주문, 1=종목 | `0` |
| INQR_DVSN_2 | query | 조회구분2 — 0=전체, 1=매도, 2=매수 | `0` |
| CTX_AREA_FK100 | query | 연속조회검색조건100 | `""` |
| CTX_AREA_NK100 | query | 연속조회키100 | `""` |

**응답 필드 (주요)**

| name | container | 의미 |
|------|-----------|------|
| ord_gno_brno | output | 주문채번지점번호 (= 취소 호출의 KRX_FWDG_ORD_ORGNO) |
| odno | output | 주문번호 (= 취소 호출의 ORGN_ODNO) |
| orgn_odno | output | 원주문번호 |
| pdno | output | 상품번호(종목코드) |
| ord_qty | output | 주문수량 |
| ord_unpr | output | 주문단가 |
| tot_ccld_qty | output | 총체결수량 |
| **psbl_qty** | output | **정정취소가능수량 (= 주문 - 체결 - 취소). 취소 전 확인 필수 필드** |
| sll_buy_dvsn_cd | output | 매도매수구분 (01=매도, 02=매수) |
| ord_dvsn_cd | output | 주문구분코드 (= 취소 호출의 ORD_DVSN) |
| excg_id_dvsn_cd | output | 거래소ID구분코드 (= 취소 호출의 EXCG_ID_DVSN_CD) |
| ctx_area_fk100 | root | 연속조회검색조건100 |
| ctx_area_nk100 | root | 연속조회키100 (header tr_cont ∈ {M,F} → 다음 페이지 존재) |

> 이 endpoint는 **미체결(정정취소가능) 주문만** 나열한다. 명시적 ccld_yn 플래그는 없으며, 주문/종목 단위 체결 확정은 `inquire-daily-ccld`로 확인.

### 6-b. 주식일별주문체결조회 (Daily Order/Fill Inquiry)

**HTTP**: `GET /uapi/domestic-stock/v1/trading/inquire-daily-ccld`

| 환경 | TR ID (3개월 이내) | TR ID (3개월 이전) |
|------|--------------------|--------------------|
| 모의 (paper) | `VTTC0081R` | `VTSC9215R` |
| 실전 (prod) | `TTTC0081R` | `CTSC9215R` |

> paper 지원. 호출당 최대 레코드: 실전 100, 모의 15.

필수 헤더: `authorization`, `appkey`, `appsecret`, `tr_id`(위 표), `content-type: application/json; charset=utf-8`, `tr_cont`(페이지네이션).

**요청 필드**

| name | 위치 | 의미 | 예시 |
|------|------|------|------|
| CANO | query | 종합계좌번호 | `12345678` |
| ACNT_PRDT_CD | query | 계좌상품코드 | `01` |
| INQR_STRT_DT | query | 조회시작일자 (YYYYMMDD) | `20260609` |
| INQR_END_DT | query | 조회종료일자 (YYYYMMDD) | `20260609` |
| SLL_BUY_DVSN_CD | query | 매도매수구분 — 00=전체, 01=매도, 02=매수 | `00` |
| INQR_DVSN | query | 조회구분 — 00=역순, 01=정순 | `00` |
| PDNO | query | 상품번호(종목코드; 공란=전체) | `005930` |
| CCLD_DVSN | query | 체결구분 — 00=전체, 01=체결, 02=미체결 | `00` |
| ORD_GNO_BRNO | query | 주문채번지점번호 (선택) | `""` |
| ODNO | query | 주문번호 (조회할 주문; 공란=전체) | `0000117057` |
| INQR_DVSN_3 | query | 조회구분3 — 00=전체/01=현금/02=신용 등 | `00` |
| INQR_DVSN_1 | query | 조회구분1 (선택; ''=전체, 1=ELW, 2=프리보드) | `""` |
| EXCG_ID_DVSN_CD | query | 거래소ID구분코드 (KRX/NXT/SOR/ALL; 기본 KRX) | `KRX` |
| CTX_AREA_FK100 | query | 연속조회검색조건100 | `""` |
| CTX_AREA_NK100 | query | 연속조회키100 | `""` |

**응답 필드 (주요)**

| name | container | 의미 |
|------|-----------|------|
| ord_dt | output1 | 주문일자 |
| **odno** | output1 | **주문번호 (내 주문과 매칭)** |
| orgn_odno | output1 | 원주문번호 |
| pdno | output1 | 상품번호(종목코드) |
| ord_qty | output1 | 주문수량 |
| ord_unpr | output1 | 주문단가 |
| **tot_ccld_qty** | output1 | **총체결수량 (ord_qty와 같으면 완전체결)** |
| tot_ccld_amt | output1 | 총체결금액 |
| avg_prvs | output1 | 평균체결가 |
| **rmn_qty** | output1 | **잔여(미체결)수량 — 0이면 완전체결, >0이면 미체결 잔량** |
| cncl_yn | output1 | 취소여부 (Y=취소됨) |
| cnc_cfrm_qty | output1 | 취소확인수량 |
| rjct_qty | output1 | 거부수량 |
| sll_buy_dvsn_cd | output1 | 매도매수구분 (01=매도, 02=매수) |
| ord_dvsn_name | output1 | 주문구분명 |
| ord_gno_brno | output1 | 주문채번지점번호 |
| tot_ord_qty | output2 | 총주문수량 (합계) |
| tot_ccld_qty | output2 | 총체결수량 (합계) |
| ctx_area_fk100 | root | 연속조회검색조건100 |
| ctx_area_nk100 | root | 연속조회키100 (header tr_cont ∈ {M,F} → 다음 페이지) |

> **체결 판정**: 명시적 `ccld_yn` boolean 없음. (a) `rmn_qty`(잔여수량)==0 → 완전체결, 또는 (b) `tot_ccld_qty` == `ord_qty`, (c) `cncl_yn`==Y → 취소로 판정한다.

---

## 구현 주의사항

### 1) hashkey 사용
- hashkey는 **선택 사항**. 공식 `kis_auth.py`의 `_url_fetch`에서 `set_order_hash_key` 호출이 주석 처리되어 있어, 주문 POST도 기본적으로 hashkey **없이** 전송된다.
- 주석 원문: "현재는 hash key 필수 사항 아님, 생략가능, API 호출과정에서 변조 우려를 하는 경우 사용".
- 구현 권장: 기본은 hashkey 미사용. 변조 방지가 필요하면 주문 JSON body를 `POST /uapi/hashkey`에 보내 응답 `HASH`를 `hashkey` 헤더로 첨부하는 옵션을 둔다.
- GET 조회(시세/잔고/체결)는 hashkey 대상이 아니다.

### 2) paper vs prod TR ID 스위칭 (KIS_ENV)
- `KIS_ENV`로 base URL과 TR ID를 동시에 전환한다.
  - prod → base `:9443`, TR ID 원본(`T…`/`C…`).
  - paper → base `:29443`, TR ID는 선두 `T`/`J`/`C`를 `V`로 치환 (예: `TTTC0012U` → `VTTC0012U`, `CTSC9215R` → `VTSC9215R`).
- **예외**: 시세 `FH…` TR(`FHKST01010100`)은 paper/prod 동일 — V 치환 금지.
- 구현 시 `ptr_id[0] in ('T','J','C') and is_paper` 조건에서만 `'V' + ptr_id[1:]`로 변환하는 헬퍼를 두면 공식 동작과 일치한다.

### 3) 응답 envelope 처리 (rt_cd / msg1)
- 모든 응답 root에 `rt_cd`, `msg_cd`, `msg1`가 있다.
- `rt_cd == "0"` → 성공. 그 외에는 `BrokerError`를 발생시키고 `msg_cd` + `msg1`(한국어 메시지)을 메시지에 포함한다.
- 가격/수량 등 숫자 필드는 문자열로 오므로 사용 시 `int`/`float`로 캐스팅한다. (주문 전송 시 `ORD_QTY`/`ORD_UNPR`는 반대로 반드시 문자열)
- 단일 객체 응답은 `output`, 배열/요약 응답은 `output1`/`output2` 컨테이너를 사용한다.

### 4) 잔고/체결 페이지네이션
- 첫 호출: 요청 헤더 `tr_cont=""`, `CTX_AREA_FK100=""`, `CTX_AREA_NK100=""`.
- 응답 헤더 `tr_cont`가 `M` 또는 `F` → 다음 페이지 존재. `D`/`E`/공백 → 마지막 페이지.
- 다음 호출: 요청 헤더 `tr_cont="N"`, 그리고 응답 body의 `ctx_area_fk100`/`ctx_area_nk100`을 각각 `CTX_AREA_FK100`/`CTX_AREA_NK100`에 echo.
- 페이지당 한도: 잔고 — 실전 50행/모의 20행; 일별체결 — 실전 100/모의 15. 한도 초과분은 연속조회로 수집해 합친다.

---

## 출처

- https://github.com/koreainvestment/open-trading-api — 공식 KIS Open API GitHub 레포
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/kis_auth.py — `_url_fetch`(GET/POST, 헤더 구성, T/J/C→V paper 치환, hashkey 주석 처리), `/oauth2/tokenP`, `/uapi/hashkey`, APIResp `rt_cd/msg_cd/msg1` envelope
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_user/kis_auth.py — hashkey OPTIONAL(`set_order_hash_key` 존재하나 호출 주석), base 도메인
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_user/domestic_stock/domestic_stock_functions.py — 통합 TR ID 교차검증 (inquire_price FHKST01010100; order_cash TTTC0012U/TTTC0011U + VTTC0012U/VTTC0011U; order_rvsecncl TTTC0013U/VTTC0013U; inquire_balance TTTC8434R/VTTC8434R; inquire_daily_ccld TTTC0081R/VTTC0081R + CTSC9215R/VTSC9215R)
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_price/inquire_price.py — inquire-price API_URL, FHKST01010100(real=demo), FID_COND_MRKT_DIV_CODE/FID_INPUT_ISCD, output 컨테이너
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_price/chk_inquire_price.py — COLUMN_MAPPING (stck_prpr=주식 현재가 등 전체 필드)
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_balance/inquire_balance.py — inquire-balance API_URL, TTTC8434R(real)/VTTC8434R(demo)
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_balance/chk_inquire_balance.py — 잔고 응답 필드(output1/output2) COLUMN_MAPPING
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/order_cash/order_cash.py — order-cash 현행 정본: real buy=TTTC0012U/sell=TTTC0011U, demo buy=VTTC0012U/sell=VTTC0011U, POST postFlag=True, output 반환
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/order_cash/chk_order_cash.py — output 필드(KRX_FWDG_ORD_ORGNO, ODNO=주문번호, ORD_TMD) COLUMN_MAPPING
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/order_rvsecncl/order_rvsecncl.py — order-rvsecncl 현행: TTTC0013U(real)/VTTC0013U(demo), EXCG_ID_DVSN_CD/RVSE_CNCL_DVSN_CD(01정정/02취소)/QTY_ALL_ORD_YN, 사전 inquire-psbl-rvsecncl(psbl_qty) 확인 요구
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_psbl_rvsecncl/inquire_psbl_rvsecncl.py — inquire-psbl-rvsecncl: TTTC0084R, 파라미터 CANO/ACNT_PRDT_CD/INQR_DVSN_1/INQR_DVSN_2/CTX_AREA_FK100/NK100
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_psbl_rvsecncl/chk_inquire_psbl_rvsecncl.py — COLUMN_MAPPING (psbl_qty=가능수량, tot_ccld_qty=총체결수량 등)
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_daily_ccld/inquire_daily_ccld.py — inquire-daily-ccld: TTTC0081R/VTTC0081R(이내), CTSC9215R/VTSC9215R(이전), ODNO/CCLD_DVSN/SLL_BUY_DVSN_CD
- https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_daily_ccld/chk_inquire_daily_ccld.py — COLUMN_MAPPING (tot_ccld_qty=총체결수량, rmn_qty=잔여수량, cncl_yn=취소여부)
- https://github.com/koreainvestment/open-trading-api/blob/main/legacy/Sample01/kis_domstk.py — 레거시/구 TR ID (order-cash TTTC0802U/TTTC0801U, order-rvsecncl TTTC0803U/VTTC0803U, inquire-psbl-rvsecncl TTTC8036R, inquire-daily-ccld TTTC8001R/CTSC9115R)
- https://apiportal.koreainvestment.com/apiservice — 공식 KIS API 포털 (JS 렌더링으로 정적 스크래핑 불가, GitHub 현행 샘플을 권위 교차근거로 사용)
- 로컬 교차검증: `C:\Users\ycpig\autofolio\scripts\kis_token_smoke.py` (DEFAULT_BASE prod :9443 / paper :29443, DEFAULT_TOKEN_PATH `/oauth2/tokenP`), `C:\Users\ycpig\autofolio\app\brokers\kis\kis_auth.py`

---

## 불일치/저신뢰 경고

구현자는 아래 항목을 코드 작성 전 반드시 재확인할 것.

### A. order-cash TR ID — 현행 vs 레거시 (★중요)
- **현행(권장)**: 매수 `TTTC0012U`/`VTTC0012U`, 매도 `TTTC0011U`/`VTTC0011U`. 공식 GitHub 현행 샘플(`order_cash.py`, 2025-09-17) 기준. `EXCG_ID_DVSN_CD` 필수화와 함께 TR ID가 변경됨.
- **레거시(폴백 후보)**: 매수 `TTTC0802U`/`VTTC0802U`, 매도 `TTTC0801U`/`VTTC0801U`. 다수 튜토리얼/서드파티 라이브러리(예: wikidocs.net/239581)가 여전히 인용하며, 아직 동작할 수 있음.
- **조치**: 신규 코드는 현행 TR ID로 구현하고, 레거시 ID를 주석/설정으로 문서화해 fallback 가능하게 둘 것. 모의/실전 양쪽에서 실제 호출로 검증 권장.

### B. order-rvsecncl TR ID — 현행 vs 레거시
- **현행**: `TTTC0013U`/`VTTC0013U` (2025 샘플).
- **레거시**: `TTTC0803U`/`VTTC0803U` (작업 프롬프트가 예상한 값이지만 **deprecated**).
- 또한 레거시에는 `EXCG_ID_DVSN_CD`가 없었음(NXT/SOR 대체거래소 지원과 함께 추가). 현행 스키마에 맞춰 필드 포함할 것.

### C. inquire-psbl-rvsecncl — paper(모의) 지원 불확실 (저신뢰)
- 현행/레거시 샘플 모두 `V` 접두 paper TR ID가 정의돼 있지 않음. 일부 계좌에서 모의 미지원 가능.
- **조치**: 모의환경 체결조회는 `inquire-daily-ccld`(VTTC0081R, paper 명확 지원)를 1차로 쓰고, `inquire-psbl-rvsecncl`의 모의 동작은 별도 검증 후 사용. 정정/취소 사전조회가 모의에서 실패하면 daily-ccld의 `rmn_qty`로 대체 판정.
- 레거시 TR ID도 상이: 현행 `TTTC0084R` vs 레거시 `TTTC8036R`.

### D. inquire-daily-ccld — 3개월 이전 TR ID 표기 불일치
- 코드(권위)에는 `CTSC9215R`(real)/`VTSC9215R`(demo)로 할당되나, **docstring 텍스트에는 `CTSC9115R`로 표기**됨. **코드 값(`CTSC9215R`)이 정본**, `CTSC9115R`은 레거시.
- 3개월 이내 TR도 레거시(`TTTC8001R`) → 현행(`TTTC0081R`) 변경됨.

### E. inquire-daily-ccld 응답 필드 — chk 파일 중복 키
- `chk_inquire_daily_ccld.py` COLUMN_MAPPING에 **중복 키**가 있어 두 번째 블록이 `tot_ccld_amt`/`pchs_avg_pric` 라벨을 재매핑함. **첫 번째(primary) 정의를 신뢰**할 것.
- 명시적 체결 boolean(`ccld_yn`) 없음 → `rmn_qty`/`tot_ccld_qty`/`cncl_yn` 조합으로 판정(위 6-b 참조).

### F. 시세 inquire-price 변형 endpoint
- 동일 시세에 신규 변형 `inquire-price-2`(`/uapi/domestic-stock/v1/quotations/inquire-price-2`)가 존재하나, 정본 현재가 endpoint는 `inquire-price`/`FHKST01010100`. 추가 필드가 필요할 때만 변형 검토.

### G. 포털 문서 직접 스크래핑 불가
- `apiportal.koreainvestment.com` 페이지는 JS 렌더링이라 필드 표를 기계적으로 읽지 못함. 본 스펙의 필드 정의는 공식 GitHub `examples_llm/*/chk_*.py`의 COLUMN_MAPPING을 권위 근거로 삼았다. 운영 투입 전 포털 문서와 1회 대조 권장.