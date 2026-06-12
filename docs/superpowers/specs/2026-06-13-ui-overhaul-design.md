# Autofolio UI/UX 대개편 — 디자인 스펙 (Phase 0 산출)

> 권위 문서: `.claude/plans/glimmering-waddling-spring.md` (마스터 플랜)
> 작성: 2026-06-13T01:33:29+09:00
> 상태: Phase 0 완료 — Phase 1 대기

---

## 1. 배경 및 Owner 결정

Autofolio 현 Streamlit UI(8화면+로그인)는 기능적으로 완성됐으나 시각 위계·일관성·체감 품질이 부족하다(페인포인트 26건 식별). Owner는 다음 4가지를 결정했다:

| 결정 항목 | 선택 |
|-----------|------|
| 스택 | **프론트엔드 분리** — Next.js 16(App Router)+TS + FastAPI 백엔드화, **스트랭글러 패턴**(Streamlit 병행 유지) |
| 디자인 톤 | **토스류 미니멀 라이트** (화이트/연그레이, 카드+여백, 큰 CTA, Pretendard) |
| 범위 | **전체 8화면 페이즈드** — 로그인부터 순차 이행 |
| 로그인 역할 | **제품의 얼굴** (브랜드+본인인증+게스트 데모 쇼케이스) |

핵심 자산: `app/ui/backend.py`(~20개 함수, streamlit 무의존)가 사실상의 API 계약. FastAPI 레이어는 현재 없음(신설).

---

## 2. 아키텍처

### 2.1 디렉토리 구조

```
autofolio/
  app/services/   # 공유 서비스 레이어 — Streamlit과 FastAPI API가 공동 소비
  app/api/        # FastAPI (routers/schemas/serializers, 세션 쿠키 인증, SSE)
  app/ui/         # 기존 Streamlit — backend.py는 재수출 shim으로 유지, Phase 5에 은퇴
  web/            # Next.js 16 + TS + Tailwind v4 + shadcn/ui + TanStack Query/Table
                  #   + lightweight-charts(시계열) + Recharts(구성비/Sankey) + Pretendard self-host
```

### 2.2 인증

- **방식**: FastAPI 단일 발급 httpOnly 서명 쿠키 세션(`itsdangerous`, 키는 `.autofolio/api_session.key`)
- **로컬 계정**: 기존 vault PBKDF2 재사용 → 양 UI(Streamlit + Next.js) 계정 호환
- **Google OIDC**: Authlib 백엔드 주도 (Auth.js 불채용 — 프론트 무자격증명 원칙)
- **게스트 세션**: `role=guest` + `data_source=demo` 고정

### 2.3 실시간 데이터

- **초기(Phase 1~3)**: TanStack Query 폴링
- **Phase 4**: SSE 단일 엔드포인트 `/api/stream/events` (price/orderbook/fill/engine)
- **엔진 이벤트 브리지**: `logs/events.jsonl` tail 크로스 프로세스
- **KIS WS**: `kis_ws_client.py`를 API 허브가 단일 소유

---

## 3. 안전 불변식 (전 Phase 공통)

다음 규칙은 예외 없이 모든 Phase에 적용한다:

1. **직접 주문 엔드포인트 금지**: `POST /trade/orders` 엔드포인트 **만들지 않음** — 주문 경로는 `run-once → OrderFlow → SafetyChecker` 유일
2. **state-changing 게이트**: 모든 상태 변경 엔드포인트에 `require_owner`(guest 403) + CSRF 헤더 필수
3. **조건 저장 서버사이드 2단계**: 공시 게이트 + 컴플라이언스 검토를 서버사이드로 이전 (`trade.py` 뷰 로직 lift)
4. **킬스위치/심볼모드 DB-backed 통일**: 세션 전용 → DB-backed 통일 (기존 갭 수정, Streamlit도 동일 PR 적용)
5. **KIS 키 백엔드 전용**: `brokers_public()` 필터, `NEXT_PUBLIC_` 시크릿 금지, API는 127.0.0.1 바인드, Next rewrites 프록시로 same-origin

---

## 4. 디자인 시스템

### 4.1 디자인 토큰

| 토큰 | 값 |
|------|----|
| 페이지 배경 | `#F2F4F6` |
| 서피스(카드) | `#FFFFFF` |
| 텍스트 기본 | `#191F28` |
| 브랜드 | `#3182F6` (토스 블루) |
| KR 손익 상승(빨강) | `#F04452` |
| KR 손익 하락(파랑) | `#3182F6` |
| 손익 방향 토글 | `html[data-pnl="western"]` 속성 토글 |
| radius | 8px ~ 20px (컴포넌트별) |
| 그림자 | 소프트 2겹 그림자 |

**구현**: Tailwind v4 CSS-first `@theme` 블록으로 선언.

### 4.2 타이포그래피

| 항목 | 값 |
|------|----|
| 폰트 패밀리 | Pretendard Variable self-host (`next/font/local`) |
| body | 15px |
| KPI 수치 | 26px · 700 · `tabular-nums` |
| 한글 제목 | `word-break: keep-all` |

### 4.3 코어 컴포넌트 목록 (~20개)

**안전 계열 (우선)**:
- `KillSwitchButton` — 라벨 "자동매매 중단"
- `ModeBadge` — L0~L4 + 한국어 레이블
- `EnvBadge` — 데모/목/모의/실전 통합
- `AutoTradingToggle` — ON 시 `ConfirmModal` 강제
- `CircuitBreakerBanner`

**레이아웃**:
- `AppShell`
- `SidebarNav` — 3그룹 8메뉴
- `TopStatusBar` — 새로고침 버튼 삭제, `StatusCluster` + 킬 상시 표시

**도메인**:
- `KpiCard`
- `PnlText`
- `DataTable`
- `HoldingsTable`
- `EquityChart`
- `CandleChart`
- `AllocationChart`
- `OrderBookLadder`
- `OrderForm`
- `ProposalCard`
- `AgentMessage`
- `EmptyState`
- `ConfirmModal`
- `StatusBadge`
- `SecretField`

### 4.4 로그인 화면 스펙

**데스크톱 레이아웃**: 55:45 좌우 스플릿

**좌 브랜드존 (55%)**:
- 헤드라인: `"투자는 에이전트 팀에게, 결정은 나에게."`
- 실컴포넌트 데모 프리뷰 카드 (홈 대시보드 미리보기)
- 안전 스트립: "🛡️ 모의투자 기본 · 자동매매 기본 OFF · 킬스위치 상시"

**우 인증존 (45%)**:
- Google CTA (1순위)
- ID/PW 로컬 로그인 (2순위)
- 게스트 데모 카드: "로그인 없이 둘러보기" (3순위)
- **Kakao/Naver 비활성 스텁 제거** (Minimum Features 원칙)

**모션**: fade-rise 240ms, 곡선 draw-in 1회, `prefers-reduced-motion` 대응

---

## 5. Phase 정의 및 완료 기준

### Phase 0 — 서비스 추출 + 디자인 스펙 (동작 변화 없음)

**목표**: 아키텍처 준비. 기존 Streamlit 동작 무변화.

**작업**:
- `app/ui/backend.py` → `app/services/{context,system,portfolio,market,trading,analysis,alerts,auth_service,connections,agents}.py` 도메인 분할
- `app/ui/backend.py`는 재수출 shim 유지 (기존 525 테스트·Streamlit 무변경)
- `app/ui/views/trade.py` 컴플라이언스/공시 게이트 로직 → `services/trading.py` lift
- `auth.py`/`store.py`/`ic.py`/`agents_runtime.py` 비-Streamlit 코어 lift
- `_ctx()` 초기화 락 추가 (`app/services/context.py`)

**완료 기준**: 전체 pytest green, Streamlit 화면 무변화.

**Phase 0 실행 결과 (중요 — 구현 실제 형태)**:

> services 레이어는 전환기 **역방향 파사드**로 구현됨:
>
> - **구현은 `app/ui/backend.py`에 잔류**, `app/services/*`가 재수출 래퍼
> - **이유**: 기존 테스트의 `patch("app.ui.backend.*")` 경로 의존. 진짜 이동은 Phase 5(AppTest 은퇴 시점)로 연기.
> - `store`/`ic`/`agents_runtime`은 진짜 이동 + shim (비-Streamlit 코어라 경로 의존 없음)
> - `auth`는 별도 `app/services/auth_service.py`로 분리
> - **trade 게이트 로직**: `services/trading.py`의 `save_condition_with_gates()` + `GateResult`로 실이동. Phase 3에서 HTTP 422/409+ack_token으로 매핑 예정.

---

### Phase 1 — FastAPI 기초 + 인증 + 읽기 API / web 스캐폴드 + 셸 + 로그인

**목표**: FastAPI 기초 레이어 + Next.js 스캐폴드 + 로그인 화면 완성.

**백엔드 작업**:
- `app/api/` (main/deps/security/serializers/schemas/routers)
- 세션 인증 (local + guest, OIDC는 Phase 1b)
- 읽기 엔드포인트: `auth/*`, `engine/status`, `portfolio/holdings|kpis|asset-curve|allocation-gap`, `market/indices|watchlist`, `trade/fills/recent`
- DataFrame 직렬화: `df_records()` 단일 헬퍼, 한국어 컬럼 키 유지 + `TableResponse{columns,rows}`
- 의존성: `fastapi`, `uvicorn[standard]`, `httpx`, `itsdangerous`

**프론트 작업**:
- `web/` 스캐폴드 (`create-next-app` + `shadcn init`)
- 토큰/globals.css, AppShell·SidebarNav·TopStatusBar·안전 배지/버튼·ConfirmModal
- 로그인 화면 완성 (§4.4 스펙)
- `lib/{api,format,query}.ts`, Next rewrites 프록시

**실행 스크립트**: `scripts/run_api.py`, `run_api.bat`, `run_frontend.bat`

**완료 기준**: 게스트/ID·PW 로그인 → `/home`(빈 셸) 도달, Playwright `login.spec.ts` 통과, API pytest(contract+gate guest 403) green, CI coverage ≥50%

---

### Phase 2 — 홈 + 포트폴리오 (읽기 화면)

**목표**: 주요 읽기 화면 구현.

**작업**:
- `KpiCard`·`PnlText`·`EquityChart`·`ProposalCard`·`DataTable`·`HoldingsTable`·`AllocationChart` 구현
- 홈/포트폴리오 페이지
- 데모 스코프 서버 강제 (폴백 금지 — 에러는 에러로 표시)
- 백엔드 추가 읽기: `market/price|order-book|fundamental|intraday|sectors|disclosures`, `trade/conditions GET`, `trade/orders/*` 읽기, `analysis/*` 읽기

**완료 기준**: 홈/포트폴리오 화면 Playwright 통과, Streamlit 동일 데이터 스팟체크 통과

---

### Phase 3 — 매매 + 내역 + 설정 (state-changing + 안전 게이트) ⚠ 최고 리스크

**목표**: state-changing 엔드포인트 + 안전 게이트 전체 이행. Owner 승인 게이트 필수.

**작업**:
- `engine/kill-switch`(DB-backed)·`auto-trading`·`run-once`(single-flight 락+409)
- `trade/conditions POST` (공시 422/컴플라이언스 CAUTION 409+ack_token 2단계)
- `settings/*`
- `OrderForm`·`OrderBookLadder`·`SecretField`·설정 5탭
- 킬스위치/심볼모드 DB-통일을 Streamlit에도 동일 PR 적용

**완료 기준**: 게이트 테스트(guest 403 전수, kill 409, 공시 차단) + paper 환경 수동 검증

---

### Phase 4 — 에이전트/IC + 알림 + SSE

**목표**: 에이전트 실시간 통합.

**작업**:
- `agents/list|ask`, `agents/ic/run`(백그라운드 잡+SSE 진행)
- `/api/stream/events` 허브 (events.jsonl tail + KIS WS opt-in + 데모 ticker)
- `AgentMessage`·IC 트랜스크립트·알림 피드
- 사전 스파이크: IC 장기실행 SSE 재접속 복원

**완료 기준**: 에이전트 ask/IC run Playwright 통과, SSE 재접속 테스트 통과

---

### Phase 5 — 분석 화면 + 패리티 감사 + Streamlit 은퇴

**목표**: 완전 이행 완료. Streamlit 은퇴.

**작업**:
- `CandleChart`·Sankey·백테스트/VaR/시나리오 폼
- 8화면 Streamlit 대비 패리티 체크리스트
- `app/ui/views` 아카이브, AppTest 스위트 제거
- docker-compose에서 streamlit 서비스 정리
- `app/services/*`에 진짜 구현 이동 (Phase 0 역방향 파사드 해소)

**완료 기준**: 8화면 패리티 체크리스트 100%, Streamlit 서비스 제거, CI green

---

## 6. 검증 전략 (전 Phase 공통)

1. **Python**: `python -m pytest tests/ -q` — 기존 525 + 신규 API 테스트, CI coverage ≥50%
2. **프론트**: `npm run lint && npm run build` + Playwright (`login.spec.ts`, `demo-walkthrough.spec.ts`, 킬스위치 모달 시나리오, 시각 회귀 스냅샷)
3. **실행 검증**: `run_api.bat` + `run_frontend.bat` → localhost:3000 수동/Playwright 확인
4. **패리티 체크**: Phase별 Streamlit 동일 화면 데이터 일치 스팟체크

---

## 7. 주요 파일 참조

| 파일 | 역할 |
|------|------|
| `app/ui/backend.py` | 계약 원본 (Phase 5까지 shim 유지) |
| `app/services/trading.py` | trade 게이트 로직 이동 대상 (Phase 0 완료) |
| `app/risk/safety_checker.py` | 안전 계약 |
| `app/ui/views/trade.py` | lift 대상 뷰 로직 |
| `app/ui/auth.py`, `app/ui/vault.py`, `app/ui/store.py` | 인증/vault/상태 |
| `app/brokers/kis/kis_ws_client.py` | 실시간 WS |
| `app/common/logger.py` | events.jsonl 구조화 로깅 |
| `app/ui/theme.py` | 포맷 규칙 (→ `web/lib/format.ts`로 이식) |
| `docs/PRODUCT_BLUEPRINT.md` | 비전 권위 §2·§7 |
| `docs/UI_SPEC.md` | UI 설계서 |
