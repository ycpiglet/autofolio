---
type: task
id: TASK-016
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 중
est_hours: 4
est_tokens: 50000
tags: [kis, fundamental, research]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-016 KIS 기업 재무정보 (PER·PBR·EPS·시가총액)

작업 ID: TASK-016
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00
완료 시각: 2026-06-12T08:53:20+09:00

## 배경 및 목적

Research Agent가 종목을 분석할 때 PER·PBR·EPS·시가총액 등 기본 재무 지표를 KIS에서 직접 수신하면 외부 API 의존 없이 밸류에이션 근거를 확보할 수 있다. `inquire-price` 응답에 per, pbr, eps, hts_avls 필드가 포함되어 있으나 현재 파싱되지 않고 있다.

## 구현 범위

- `inquire-price` 응답의 미파싱 필드 추출: per, pbr, eps, hts_avls(시가총액)
- `inquire-finance-ratio` 엔드포인트 별도 호출 구현
- `KisClient.get_fundamental(symbol)` 메서드로 통합 제공
- Research Agent 프롬프트/컨텍스트 빌더에 재무 데이터 주입 경로 추가
- 분석 화면 종목 상세 패널에 재무 지표 표시

## 완료 기준

- [x] `get_fundamental()` 구현 및 단위 테스트
- [x] per/pbr/eps/hts_avls 파싱 검증 (실제 응답 샘플 기반)
- [x] Research Agent 컨텍스트 빌더 연결 확인

## 완료 기록

- 원 요청: KIS에서 PER/PBR/EPS/시가총액 등 기본 재무 지표를 받아 Research Agent와 분석 화면에서 사용할 수 있게 한다.
- 공식 정본 확인:
  - `inquire-price` 응답에 `per`, `pbr`, `eps`, `hts_avls`, `lstn_stcn` 필드가 포함된다.
  - 공식 `finance_ratio` 샘플은 특정 종목 단건 조회가 아니라 시장/분류별 ranking API(`/uapi/domestic-stock/v1/ranking/finance-ratio`, `FHPST01750000`)다.
- 실제 작업:
  - `KisClient.get_fundamental(symbol)` 추가. `inquire-price`에서 `price`, `per`, `pbr`, `eps`, `market_cap`, `listed_shares`를 정규화.
  - `KisClient.get_finance_ratio_rank()` 추가. 공식 `finance-ratio` ranking 응답을 정규화하고, `get_fundamental()`에서 해당 종목이 결과에 있으면 `finance_ratio` 보조 지표로 포함.
  - `backend.fundamental(symbol)` 추가.
  - `backend.propose()`가 가능한 경우 fundamental data를 ResearchAgent에 전달.
  - `ResearchAgent.propose_price_condition(..., fundamental=...)`와 `fundamental_context()` 추가.
  - 분석 화면에 종목별 재무 지표 metric 패널 추가.
  - `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md` 갱신.
- 변경 파일:
  - `app/brokers/kis/kis_client.py`
  - `app/ui/backend.py`
  - `app/ui/views/analysis.py`
  - `app/agents/research_agent.py`
  - `tests/unit/test_kis_fundamental.py`
  - `tests/unit/test_backend_fundamental.py`
  - `tests/unit/test_factory_and_research.py`
  - `tests/unit/test_analysis_intraday_view.py`
  - `docs/KIS_API_SPEC.md`
  - `docs/references/kis/PROJECT-MAPPING.md`
  - `docs/BACKLOG.md`
- 검증:
  - `python -m py_compile app\brokers\kis\kis_client.py app\ui\backend.py app\ui\views\analysis.py app\agents\research_agent.py tests\unit\test_kis_fundamental.py tests\unit\test_backend_fundamental.py tests\unit\test_factory_and_research.py tests\unit\test_analysis_intraday_view.py` — 통과
  - `pytest tests\unit\test_kis_fundamental.py tests\unit\test_backend_fundamental.py tests\unit\test_factory_and_research.py tests\unit\test_analysis_intraday_view.py` — 16 passed
  - `pytest tests\unit\test_kis_fundamental.py tests\unit\test_backend_fundamental.py tests\unit\test_factory_and_research.py tests\unit\test_analysis_intraday_view.py tests\unit\test_kis_disclosures.py tests\unit\test_backend_disclosures.py` — 25 passed
  - `pytest tests` — 374 passed
  - `python scripts\validate_task_schema.py` — OK
  - `python scripts\generate_views.py --check` — OK
  - `python scripts\check_agent_docs.py` — OK, 0 errors / 124 warnings
