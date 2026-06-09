# STATUS — Autofolio (lead_engineer)

> agent_runtime 프레임워크의 start protocol이 읽는 canonical 운영 상태 보드.
> 시각: `python scripts/now.py`

## Autofolio 컨텍스트 (프레임워크에 제공하는 "맥락")
- **무엇**: Autofolio = 한국투자증권(KIS) 기반 개인용 국장 자동매매 OS ("Agentic Quant Portfolio OS").
- **성격**: 다수 고객 SaaS가 아니라 1인 소유자의 개인 자산운용 시스템.
- **스택**: Python · Streamlit(`app/ui`) · SQLite(`app/database`) · KIS Open API(`app/brokers/kis`) · Mock 브로커 · pytest.
- **두 조직**: 이 agent_runtime 프레임워크 = **개발팀**(소프트웨어 제작/운영). `.claude/agents/asset-team` + 거버넌스 = **자산운용팀**(투자 리서치·제안). 개발팀은 투자 결정을 하지 않고, 자산팀은 코드를 머지하지 않는다.
- **안전 제1원칙(MVP_SPEC §6.6)**: 자동매매 기본 OFF · mock 우선 · 화이트리스트 전용 · 킬스위치 · 실거래는 사람 명시 승인.
- **문서/라이브 백로그**: `docs/`(ORG_PLAN · PRODUCT_BLUEPRINT · UI_SPEC · AGENT_TEAMS · BACKLOG). 제품 백로그는 `docs/BACKLOG.md`.

## 캐노니컬 운영 참조
- TASK 레지스트리: `tasks/INDEX.md` · 열린 작업 보드: `tasks/BACKLOG.md`(generate_views 생성)
- 리뷰: `reviews/` (사이클 완료 시 생성) · 사이클: `CYCLE-*.md` (미생성)
- 회고/감사: `compound_log.md` · `AUDIT-LOG.md`
- **프레임워크↔Autofolio 분리·업데이트 런북**: `docs/AGENT_RUNTIME_INTEGRATION.md` (틀=agent_runtime 정본 / 맥락=호스트 추가 파일 / 시임=AGENTS.md·roles.yml `unmanaged`)

## 현재 상태 (2026-06-09T15:37 갱신)
- agent_runtime v0.1.5 전체 이식 + **분리 운영**(시임 `AGENTS.md`·`roles.yml` = `sync.unmanaged`, `docs/AGENT_RUNTIME_INTEGRATION.md`) 완료. check_agent_docs **0 error**, pytest(tests/) **26 passed**(+KisClient 17).
- 업스트림 기여: agent_runtime **Issue #1**(통합보고+전수감사 코멘트) + **PR #2**(task.schema.json·AGENTS §13–14) OPEN. 누락 모듈(orchestrator_safety_gate·pipeline) 의도 로직은 업스트림 담당.
- 작업물 커밋: 브랜치 **`feat/agent-runtime-integration`**(commit 4586fe2, 288파일) + KIS 스모크(94e37b5). **P1.1b 코어는 미커밋**. main 미병합·미푸시.
- **KIS (P1.1b 코어 완료)**: paper·prod 키 `.env` 입력 + 토큰 발급 검증 완료. `kis_client.py` **5메서드 실구현**(현행 TR ID·rt_cd envelope·레이트리밋 재시도, 근거 `docs/KIS_API_SPEC.md`) — 단위테스트 17, **라이브 paper 읽기검증(현재가·잔고) 통과**. 환경별 자격증명/URL 해석은 `settings.resolve_settings()`로 중앙화(라이브 인증 실패 버그 동시 수정).

## 활성 작업 (다음 세션 시작점)
- **P1.1b 거의 완료** → `docs/BACKLOG.md §다음 1`. 이번 세션 추가: (1) `kis_client` 5메서드+테스트+라이브 paper 읽기검증, (2) `kis_paper_order_smoke.py`(paper 전용 주문 생애주기, 사람이 직접 실행), (3) `backend.holdings_df()` 라이브 어댑터 + 포트폴리오 화면 보유표 라이브 분기(데모 렌더 회귀검증). pytest **29 passed**.
- **P1.1b 잔여**: (a) **1주 수동 실주문** — 사람 승인 게이트(에이전트 자동발주는 안전분류기도 차단). 정규장에 `! python scripts/kis_paper_order_smoke.py`로 paper 검증 후 실전. (b) 홈 KPI/자산곡선·분석(백테스트·기여도) 라이브화는 이력DB·에이전트·백테스트 엔진 의존 → 후속. (c) 엔진 market-fallback 의미 보정(KIS 주문=접수/PENDING).
- **커밋 상태**: `01eb310`(kis_client+settings 코어) 커밋됨. step2/3 산출물(`backend.holdings_df`·`portfolio.py`·`kis_paper_order_smoke.py`·`test_backend_holdings.py`)은 이어서 커밋.
- 환경 메모: dev Python 에 `pandas`·`streamlit` 설치 완료(2.3.3/1.58.0, 선언 의존성). UI AppTest 가능.
- **자율 머지 거버넌스(신규, provisional)**: 업스트림이 `auto_merge.py`(스크립트)는 실었으나 그 근거 `AGENTS.md §3.5`·`MEETING/EVIDENCE-2026-06-01`은 **미커밋**(2026-06-09 확인). 호스트가 잠정 정본 [MERGE-POLICY.md](MERGE-POLICY.md) + `AGENTS.md` 오버레이 §15 로 정의(코드 정본 `auto_merge.py`). **우선순위=업스트림 우선**: 업스트림 §3.5 출현 시 `scripts/check_merge_policy_precedence.py`(검증 완료)가 감지·강제, 절차는 `docs/AGENT_RUNTIME_INTEGRATION.md §3.1`. 충돌 회피 위해 공통부는 공유 본문(§0–§12)에 안 박고 ②/오버레이로 격리. ⚠ 실제 자율 머지는 하네스 안전분류기(별개 층)가 여전히 게이트.
- 운영 사이클(CYCLE/REVIEW)은 아직 미시작 — 첫 실작업 사이클에서 생성.
