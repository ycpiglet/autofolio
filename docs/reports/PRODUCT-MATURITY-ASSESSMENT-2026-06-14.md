# Autofolio — 프로덕트 성숙도 평가 (2026-06-14)

> **평가자**: Lead Engineer
> **평가일**: 2026-06-14
> **대상 브랜치**: `feat/v1-migration-pilot`
> **평가 범위**: UI 레이어 (Streamlit), 백엔드 서비스·리포지토리, 테스트 커버리지, 아키텍처 위험도

---

## 1. 평가 요약 (Executive Summary)

### 현재 단계

**Late Alpha / Pre-Beta** — 핵심 거래 루프는 가동 가능한 상태이나, 프로덕션 진입 전 반드시 해소해야 할 안전 버그 3건과 다수의 UX 미완성 항목이 잔존한다.

### 종합 판정

| 영역 | 점수 | 한 줄 판정 |
|------|------|-----------|
| UI 성숙도 | **6.5 / 10** | 주요 화면 기능은 작동하나 크리티컬 핸들러 누락 3건 |
| 백엔드 성숙도 | **5.5 / 10** | 알림 평가 루프 미연결, 컴플라이언스 fail-open 등 구조적 결함 |
| 테스트 커버리지 | **~50%** | 목표(60%+) 미달, 안전 경로 경계 조건 공백 |
| 아키텍처 위험도 | **중간-높음** | UTC/KST 혼용, TOCTOU 레이스, WAL 미적용 |

### Top 3 즉시 조치 사항

1. **TASK-051 완료** — `trading.py` LLM 키워드 컴플라이언스 fail-open 패치 (안전 버그)
2. **TASK-050 완료** — `repositories.py` UTC/KST 타임스탬프 불일치 수정 (데이터 무결성)
3. **TASK-052 완료** — 알림 평가 루프 엔진 연결 (핵심 기능 공백)

---

## 2. 평가 지표 레이더 (Metrics Radar)

### 종합 점수 테이블

| 평가 차원 | 점수 | 가중치 | 가중 점수 | 비고 |
|-----------|------|--------|----------|------|
| UI 완성도 (기능 구현율) | 6.5 | 20% | 1.30 | 크리티컬 버그 3건 포함 |
| 백엔드 안정성 | 5.5 | 25% | 1.38 | 알림 루프 미연결 |
| 테스트 커버리지 | 5.0 | 20% | 1.00 | 50% / 목표 60%+ |
| 안전·컴플라이언스 | 5.0 | 20% | 1.00 | fail-open, circuit breaker 오류 |
| 아키텍처 견고성 | 6.0 | 15% | 0.90 | DB 레이스, WAL 미적용 |
| **종합 (가중 평균)** | **5.58** | 100% | **5.58** | **Beta 진입 기준: 7.0 이상** |

### 영역별 미니 레이더 (텍스트 표현)

```
UI 성숙도       ████████░░  6.5
백엔드 성숙도   ██████░░░░  5.5
테스트 커버리지 █████░░░░░  5.0 (50%)
안전·컴플라이언스 █████░░░░░ 5.0
아키텍처 견고성 ██████░░░░  6.0
─────────────────────────────────
Beta 기준선     ███████░░░  7.0
```

---

## 3. UI 성숙도 상세

### 3.1 뷰별 점수 요약

| 뷰 파일 | 점수 | 상태 | 주요 결함 |
|---------|------|------|-----------|
| `app/views/login.py` | 7.0 | 양호 | 비밀번호 재설정 없음, OIDC 이름 추출 없음, 세션 만료 경고 없음 |
| `app/views/home.py` | 7.0 | **⚠ 크리티컬** | 제안 승인/거부 버튼 핸들러 없음 (코스메틱만) |
| `app/views/portfolio.py` | 7.5 | 경고 | `allocation_gap()` 백엔드 모드 AttributeError → 사일런트 목 폴백, 비중 컬럼 미표시 |
| `app/views/trade.py` | 8.0 | 양호 | 오픈 조건 주문 취소 없음, 데모 모드 주문 버튼 no-op |
| `app/views/analysis.py` | 6.5 | 경고 | `_intraday_section()` try/except 없음 (탭 크래시), 백테스트 벤치마크 오버레이 없음 |
| `app/views/alerts.py` | 5.5 | **⚠ 크리티컬** | 알림 채널 토글·규칙 멀티셀렉트 저장 핸들러 완전 누락 |
| `app/views/settings.py` | 7.5 | 경고 | 리스크 입력 필드 5개 중 2개만 저장 버튼에 반영 |
| `app/views/agents.py` | 7.0 | 경고 | 단발성 채팅만 (스트리밍 없음), 에이전트 트리 항상 목 데이터 |
| `app/views/history.py` | 6.0 | **⚠ 크리티컬** | 라인 41 조기 `return` — 라이브 모드에서 PnL/배당 탭 완전 숨겨짐 |

**UI 평균: 6.5 / 10**

### 3.2 크리티컬 버그 상세

#### BUG-UI-01: `home.py` — 제안 승인/거부 버튼 핸들러 없음
- **영향**: IC 제안이 들어와도 승인·거부 불가 → 자동 거래 사이클 완전 차단
- **위치**: `app/views/home.py` (승인/거부 버튼 렌더링 블록)
- **조치**: `st.button("승인")` / `st.button("거부")` 각각에 `proposal_service.approve()` / `proposal_service.reject()` 핸들러 연결 필요

#### BUG-UI-02: `alerts.py` — 알림 설정 저장 핸들러 완전 누락
- **영향**: 사용자가 알림 채널(카카오/이메일/슬랙)·규칙을 설정해도 재시작 시 초기화됨
- **위치**: `app/views/alerts.py` (채널 토글 섹션, 규칙 멀티셀렉트 섹션)
- **조치**: 저장 버튼 + `alert_service.save_preferences()` 연결 필요

#### BUG-UI-03: `history.py` — 조기 `return`으로 PnL/배당 탭 미표시
- **영향**: 라이브 모드에서 수익률·배당 이력 완전 조회 불가
- **위치**: `app/views/history.py`, 라인 41
- **조치**: 조기 `return` 제거 또는 조건 분기 수정

### 3.3 중간 등급 결함 (High)

| 결함 | 위치 | 영향 |
|------|------|------|
| `allocation_gap()` AttributeError → 목 폴백 | `app/views/portfolio.py` | 백엔드 모드에서 포트폴리오 비중 분석 신뢰 불가 |
| `_intraday_section()` try/except 없음 | `app/views/analysis.py` | KIS API 오류 시 분석 탭 전체 크래시 |
| 리스크 파라미터 3개 미저장 | `app/views/settings.py` | 손절선·포지션 한도 설정 반영 안 됨 |

---

## 4. 백엔드 성숙도 상세

### 4.1 모듈별 점수 요약

| 모듈 | 점수 | 주요 이슈 |
|------|------|-----------|
| `app/services/live_trading_engine.py` | 7.0 | 전체적으로 양호 |
| `app/services/order_flow.py` | 6.0 | TOCTOU 레이스, 블로킹 sleep, 부분 체결 미처리 |
| `app/services/condition_evaluator.py` | 7.0 | 슬리피지 밴드 없음, 복합 트리거 미지원 |
| `app/services/safety_checker.py` | 6.0 | 일일 PnL 서킷 브레이커 로직 오류, 휴일 캘린더 없음, 포지션 집중도 체크 없음 |
| `app/services/duplicate_guard.py` | 6.0 | 조건별 중복 방지 (심볼별 아님) |
| `app/services/trading_window.py` | 8.0 | 휴일 캘린더 없음 |
| `app/repositories/repositories.py` | 6.0 | WAL 미적용, FK 미강제, 비원자적 카운터, **UTC/KST 불일치 (TASK-050)** |
| `app/services/auth_service.py` | 5.0 | 자동 등록, 잠금 없음, 볼트 read-modify-write 레이스 |
| `app/services/connections.py` | 5.0 | 볼트 레이스, 브로커 환경변수 검증 없음 |
| `app/services/alerts.py` | 4.0 | **알림 평가 루프 엔진 연결 완전 누락 (TASK-052)** |
| `app/services/errors.py` | 4.0 | 미사용 예외 클래스, 에러 코드 없음 |
| `app/services/logger.py` | 7.0 | 로그 로테이션 없음, 상대 경로 |
| `app/services/trading.py` | 5.0 | **LLM 키워드 컴플라이언스 fail-open (TASK-051)** |

**백엔드 평균: 5.5 / 10**

### 4.2 안전 버그 상세 (Active Tasks)

#### TASK-050: `repositories.py` UTC/KST 타임스탬프 불일치
- **심각도**: High (데이터 무결성)
- **위치**: `app/repositories/repositories.py`
- **상세**: DB 저장 타임스탬프와 KST 거래 로그 간 시간대 불일치 → 거래 기록 정합성 손상, 심야 거래 집계 오류 가능
- **상태**: 구현 준비 완료 (Ready)

#### TASK-051: `trading.py` LLM 컴플라이언스 fail-open
- **심각도**: Critical (안전·규정)
- **위치**: `app/services/trading.py`
- **상세**: LLM 키워드 컴플라이언스 체크 실패 시 오류를 무시하고 거래를 진행 (fail-open). 규정 위반 주문이 통과될 수 있음
- **상태**: 구현 준비 완료 (Ready)

#### TASK-052: 알림 평가 루프 미연결
- **심각도**: High (핵심 기능 공백)
- **위치**: `app/services/alerts.py`, `app/services/live_trading_engine.py`
- **상세**: `alerts.py` 서비스의 알림 평가 루프가 엔진에 연결되지 않아 거래 이벤트에 대한 알림이 전혀 발송되지 않음
- **상태**: 구현 준비 완료 (Ready)

### 4.3 구조적 결함 (High)

| 결함 | 위치 | 위험 |
|------|------|------|
| `safety_checker.py` 일일 PnL 서킷 브레이커 로직 오류 | `app/services/safety_checker.py` | 손실 한도 초과 시 거래 차단 실패 가능 |
| `order_flow.py` TOCTOU 레이스 | `app/services/order_flow.py` | 동시 주문 시 중복 체결 위험 |
| `auth_service.py` 자동 등록 + 잠금 없음 | `app/services/auth_service.py` | 무차별 대입 공격 취약 |
| `duplicate_guard.py` 심볼 단위 미작동 | `app/services/duplicate_guard.py` | 동일 종목 다중 조건 중복 주문 가능 |
| `repositories.py` WAL 미적용 | `app/repositories/repositories.py` | 거래 중 동시 읽기 성능 저하 및 락 경쟁 |

---

## 5. 테스트 커버리지 현황

### 5.1 현황 요약

| 항목 | 현재 값 | 목표 |
|------|--------|------|
| 통과 유닛 테스트 수 | **432건** | 500건+ |
| 추정 라인 커버리지 | **~50%** | **60%+** |
| 안전 경로 커버리지 | **낮음** | 90%+ |
| 크리티컬 버그 회귀 테스트 | **없음** | 필수 |

### 5.2 커버리지 공백 (High Risk)

#### 카테고리별 누락 테스트

| 카테고리 | 누락 항목 수 | 대표 누락 케이스 |
|----------|------------|----------------|
| 경계 조건 (Boundary) | ~12건 | 주문 수량 최소/최대, PnL 서킷 브레이커 임계값 정확 |
| KIS API 오류 모드 | ~8건 | 타임아웃, 429 레이트 리밋, 토큰 만료, 부분 체결 |
| 리포지토리 오류 시뮬레이션 | ~6건 | DB 잠금, 중복 키, 마이그레이션 롤백 |
| 안전 경로 조합 | ~10건 | 서킷 브레이커 + 중복 방지 동시 발화, 컴플라이언스 fail-open |
| **합계** | **~36건** | — |

### 5.3 고위험 테스트 공백 상세

```
안전 경로 조합 시나리오 (미구현):
  1. 일일 PnL 손실 한도 -5% 정확히 도달 시 서킷 브레이커 발동 여부
  2. LLM 컴플라이언스 서비스 예외 → fail-open 경로 재현
  3. duplicate_guard + 동일 심볼 다중 조건 동시 트리거
  4. 알림 루프 비연결 상태에서 거래 이벤트 발생 시 사일런트 실패 여부
  5. UTC→KST 자정 경계에서 일별 집계 정합성
```

---

## 6. 아키텍처 위험도

### 6.1 현재 아키텍처 상태

```
[현재]  Streamlit (app/views/) ──▶ Services (app/services/) ──▶ SQLite (WAL 미적용)
                                       │
                                       └──▶ KIS API (연결 레이스 존재)
                                       └──▶ LLM 컴플라이언스 (fail-open)
                                       └──▶ 알림 루프 (엔진 미연결)

[목표]  Next.js + FastAPI ──▶ Services (동일) ──▶ PostgreSQL 또는 SQLite WAL
        Phase 0: 완료 (shared service layer 추출)
        Phase 1-5: 진행 예정
```

### 6.2 Top 위험 목록

| 우선순위 | 위험 | 위치 | 완화 방법 |
|----------|------|------|----------|
| P0 | 컴플라이언스 fail-open | `trading.py` | fail-closed 전환 (TASK-051) |
| P0 | 알림 루프 미연결 | `alerts.py`, `live_trading_engine.py` | 엔진 연결 (TASK-052) |
| P1 | UTC/KST 불일치 | `repositories.py` | 일관된 KST 또는 UTC 정규화 (TASK-050) |
| P1 | 서킷 브레이커 오류 | `safety_checker.py` | 로직 수정 + 단위 테스트 경계값 추가 |
| P1 | TOCTOU 레이스 (주문) | `order_flow.py` | DB-레벨 원자적 업데이트 또는 락 적용 |
| P2 | 볼트 read-modify-write | `auth_service.py`, `connections.py` | 낙관적 잠금 또는 트랜잭션 |
| P2 | WAL 미적용 | `repositories.py` | `PRAGMA journal_mode=WAL` 적용 |
| P3 | 휴일 캘린더 없음 | `trading_window.py`, `safety_checker.py` | 공공 API 또는 정적 파일 적용 |

### 6.3 마이그레이션 현황

| 단계 | 내용 | 상태 |
|------|------|------|
| Phase 0 | 공유 서비스 레이어 추출 | **완료** |
| Phase 1 | FastAPI 백엔드 스캐폴딩 | 대기 |
| Phase 2 | Next.js 프론트엔드 마이그레이션 | 대기 |
| Phase 3 | KIS API 어댑터 이식 | 대기 |
| Phase 4 | 안전·컴플라이언스 레이어 재검증 | 대기 |
| Phase 5 | E2E 검증 및 스테이징 | 대기 |

### 6.4 프로덕션 진입 현황

- **실거래 실행 이력**: 없음
- **프로덕션 전환 승인 조건**: R3 Owner 승인 필수
- **현재 상태**: 실거래 전환 불가 (TASK-050, 051, 052 미완료)

---

## 7. 개선 우선순위 매트릭스

### Priority × Impact Matrix

| 우선순위 | 항목 | 영향도 | 난이도 | 담당 태스크 | 상태 |
|----------|------|--------|--------|------------|------|
| **Critical** | LLM 컴플라이언스 fail-closed 전환 | 안전·규정 | 중 | TASK-051 | **완료** |
| **Critical** | 알림 루프 엔진 연결 | 핵심 기능 | 중 | TASK-052 | **완료** |
| **Critical** | `history.py` 조기 return 제거 | UX 차단 | 낮 | TASK-058 | **완료** |
| **Critical** | `home.py` 제안 핸들러 연결 | 핵심 워크플로 | 중 | TASK-055 | **완료** |
| **High** | UTC/KST 타임스탬프 정규화 | 데이터 무결성 | 중 | TASK-050 | **완료** |
| **High** | 서킷 브레이커 로직 수정 | 안전 | 중 | TASK-063 | **완료** |
| **High** | `alerts.py` UI 저장 핸들러 추가 | 기능 완성 | 낮 | TASK-054 | **완료** |
| **High** | `analysis.py` try/except 추가 | 안정성 | 낮 | TASK-067 | **완료** |
| **High** | 안전 경로 테스트 36건 추가 | 품질 | 높 | TASK-066 | 대기 |
| **High** | KPI 하드코딩(일손익률/누적손익률) 수정 | 기능 정확성 | 낮 | TASK-057 | **완료** |
| **High** | logout() 세션 초기화 완전화 (security) | 보안 | 낮 | TASK-059 | **완료** |
| **Medium** | `order_flow.py` TOCTOU 수정 | 안전 | 높 | TASK-064 | **완료** |
| **Medium** | 볼트 레이스 해소 (`auth`, `connections`) | 보안 | 중 | — | 대기 |
| **Medium** | `portfolio.py` 비중 컬럼 표시 | UX | 낮 | TASK-056 | **완료** |
| **Medium** | WAL 적용 | 성능 | 낮 | TASK-060 | 대기 |
| **Medium** | `duplicate_guard` 심볼 단위 전환 | 정확성 | 중 | — | 대기 |
| **Medium** | 가격 알림 엔진 평가 루프 구현 | 기능 | 중 | TASK-061 | 대기 |
| **Medium** | KRX 휴장일 캘린더 연동 | 안전 | 중 | TASK-062 | 대기 |
| **Low** | 로그 로테이션 추가 | 운영 | 낮 | TASK-065 | 대기 |
| **Low** | `errors.py` 에러 코드 체계 | 유지보수 | 낮 | — | 대기 |
| **Low** | `agents.py` 스트리밍 + 실제 트리 | UX | 높 | — | 대기 |

---

## 8. 프로덕션 진입 체크리스트

아래 항목이 **전부 완료**되어야 실거래 전환을 R3 Owner에게 요청할 수 있다.

### 8.1 블로커 (차단 항목) — 전부 미완료 시 전환 금지

- [x] **TASK-050** — `repositories.py` UTC/KST 불일치 해소 및 마이그레이션 스크립트 검증 *(완료)*
- [x] **TASK-051** — `trading.py` 컴플라이언스 fail-closed 전환 및 회귀 테스트 통과 *(완료)*
- [x] **TASK-052** — 알림 평가 루프 엔진 연결 및 E2E 알림 발송 검증 *(완료)*
- [x] **TASK-063** — `safety_checker.py` 일일 PnL 서킷 브레이커 로직 수정 + 경계값 테스트 *(완료)*
- [x] **TASK-055** — `home.py` 제안 승인/거부 핸들러 연결 *(완료)*
- [x] **TASK-058** — `history.py` 라이브 모드 조기 `return` 제거 *(완료)*
- [x] **TASK-054** — `alerts.py` UI 저장 핸들러 구현 *(완료)*

### 8.2 품질 게이트 (전환 전 달성 필수)

- [ ] 유닛 테스트 커버리지 ≥ 60%
- [ ] 안전 경로(서킷 브레이커, 컴플라이언스, 중복 방지) 조합 테스트 100% 통과
- [ ] KIS API 오류 모드 8종 시뮬레이션 통과
- [ ] 스테이징 환경 48시간 무중단 실행

### 8.3 거버넌스

- [ ] R3 Owner 검토 및 서명
- [ ] 컴플라이언스 오피서 최종 안전 체크리스트 확인
- [ ] 데모 모드 → 실거래 전환 절차 문서 작성
- [ ] 비상 정지 절차 및 복구 런북 작성

### 8.4 운영 준비

- [ ] 로그 로테이션 설정
- [ ] 실거래용 볼트 자격증명 교체
- [ ] 휴일 캘린더 데이터 로드
- [ ] 모니터링·알람 대시보드 검증

---

## 9. 지표 기준 정의

### 9.1 점수 산정 방식

각 뷰·모듈 점수는 아래 4개 차원의 가중 평균으로 산정한다.

| 차원 | 가중치 | 설명 |
|------|--------|------|
| 기능 완성도 | 35% | 설계 스펙 대비 구현된 기능 비율 |
| 버그 부재 | 30% | 크리티컬 버그 −2점, High 버그 −1점 |
| 코드 품질 | 20% | 오류 처리, 로깅, 타입 힌트, 테스트 존재 여부 |
| 안전·규정 | 15% | 거래 안전 요구사항 충족 여부 |

### 9.2 10점 만점 기준

| 점수 | 의미 |
|------|------|
| 9-10 | 프로덕션 수준: 버그 없음, 풀 기능, 테스트 완비 |
| 7-8 | Beta 수준: 마이너 결함만 존재, 핵심 경로 테스트 완비 |
| 5-6 | Alpha 수준: 크리티컬 버그 존재, 기능 공백 다수 |
| 3-4 | Pre-Alpha: 뼈대만 존재, 주요 기능 미구현 |
| 1-2 | 스텁/플레이스홀더 |

### 9.3 현재 단계 정의

| 단계 | 정의 | 현재 여부 |
|------|------|----------|
| Late Alpha | 핵심 루프 동작, 안전 버그 활성, 미완성 기능 다수 | **현재** |
| Pre-Beta | 안전 버그 해소, 기능 완성도 80%+, 커버리지 60%+ | 다음 목표 |
| Beta | 스테이징 48h 통과, Owner 승인 대기 | 2단계 후 |
| Production | R3 Owner 승인, 실거래 개시 | 최종 목표 |

### 9.4 평가 한계 및 전제

- 본 평가는 코드 정적 분석 및 구조 검토 기반이며, 실거래 시뮬레이션은 포함하지 않는다.
- 테스트 커버리지는 실행 기반 측정이 아닌 파일 분석 추정치이며 ±5%p 오차가 있을 수 있다.
- KIS API 실제 응답 기반 통합 테스트는 별도 평가 범위다.
- 마이그레이션(Streamlit→Next.js/FastAPI) 완료 후 해당 레이어에 대한 재평가가 필요하다.

---

## 10. 개선 이행 현황 (2026-06-14 기준)

### 10.1 TASK-053~067 완료 현황

| TASK | 설명 | 상태 |
|------|------|------|
| TASK-053 | 제품 성숙도 평가 지표 문서 등록 | **완료** |
| TASK-054 | fix: 알림 채널 토글/규칙 설정 미저장 (alerts.py) | **완료** |
| TASK-055 | fix: 홈 화면 IC 제안 승인/거부 버튼 no-op | **완료** |
| TASK-056 | fix: backend.allocation_gap() 미구현 → mock fallback | **완료** |
| TASK-057 | fix: 일손익률/누적손익률 KPI 0.0 하드코딩 | **완료** |
| TASK-058 | fix: history.py 라이브 모드 조기 return으로 탭 미렌더 | **완료** |
| TASK-059 | fix: logout() 미완전 세션 상태 초기화 (security) | **완료** |
| TASK-060 | SQLite WAL 모드 + FK 제약 적용 | 대기 |
| TASK-061 | feat: 가격 알림 엔진 평가 루프 구현 | 대기 |
| TASK-062 | feat: KRX 휴장일 캘린더 연동 (safety) | 대기 |
| TASK-063 | fix: 서킷브레이커 일손실 기준 로직 오류 (안전 버그) | **완료** |
| TASK-064 | fix: 주문 조건 TOCTOU 레이스 — 중복 주문 위험 (Critical) | **완료** |
| TASK-065 | feat: 로그 로테이션 + 절대 경로 (ops) | 대기 |
| TASK-066 | feat: 테스트 커버리지 60%+ — 누락 35개 케이스 구현 | 대기 |
| TASK-067 | fix: 분석 탭 _intraday_section try/except 누락 크래시 | **완료** |

**완료: 11건 / 대기: 5건 (TASK-060, 061, 062, 065, 066)**

### 10.2 다음 평가 사이클

| 이벤트 | 예정일 | 담당 | 추적 |
|--------|--------|------|------|
| 반기 재평가 (Semi-Annual Re-Assessment) | 2026-12-14 | Lead Engineer | [TASK-069](TASK-069-product-maturity-reassessment-2026-12.md) |

재평가 시 점검 항목: TASK-060·061·062·065·066 완료 여부, 테스트 커버리지 실측, 아키텍처 마이그레이션 진행률, 신규 버그 유입 여부.

---

*생성: Lead Engineer · 2026-06-14 · `feat/v1-migration-pilot` 브랜치 기준*
*TASK-053 완료(등록): 2026-06-14T14:54:50+09:00*
*다음 반기 재평가: 2026-12-14 → TASK-069*
