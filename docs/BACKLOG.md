# Autofolio 할 일 목록 · 백로그

> 현황 스냅샷 + 우선순위 백로그. 로드맵 근거: [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md) §8(P0–P4) · [ORG_PLAN.md](ORG_PLAN.md) §6–7 · [UI_SPEC.md](UI_SPEC.md) §7.
> 갱신: 2026-06-09

---

## ✅ 완료 (현재까지)

- **리브랜딩** — pamc/kis_autotrading_mvp → **Autofolio** (README·MVP_SPEC·git remote).
- **자산운용팀** — leadership 4 + korea 4 + us 3 + global 4 = **15 에이전트 + 15 스킬** + governance(devils-advocate).
- **개발팀** — `agent_runtime` **16역할**(프레임워크 정본 `agents/<role>/SKILL.md`) + Autofolio 전용 `kis-api-engineer`(`agents/kis_api_engineer/SKILL.md`로 정본화) = **17역할**. 타프로젝트 스택(Supabase/Vercel) 정리, 비엔지니어 포함 Autofolio 컨텍스트 주입. 앱 `agents_runtime`은 정본 `agents/` + `.claude/agents`(자산·거버넌스)를 읽는다.
- **에이전트 실연결 (P2)** — `agents_runtime.py`가 `.claude/agents` 페르소나+스킬을 **Anthropic API**로 구동(키 없으면 스텁).
- **투자위원회(IC) (P2)** — 전문가→Devil's Advocate→리스크→PM→CIO→**결정 로그**(`.autofolio/decisions/`).
- **UI (P1.0a/b/c + P1.1a)** — 8화면 Streamlit 셸, 로그인(ID/PW·게스트·OIDC 게이트), **연동 마법사**(SSO/채널/증권 다계좌, Fernet vault), 운영모드 L0–L4·킬스위치, **라이브 백엔드**(Mock 브로커+SQLite, 키 불필요: 화이트리스트·시세·조건·엔진·주문로그).
- **운영·리포팅 프로토콜** — `AGENTS.md`·`CLAUDE.md`·`scripts/now.py` 도입(agent_runtime 규약 이식·적응): BRIEF(Bottom Line→Signal→Insight→Decision)·PLAN·Plan→Work→Review→Compound·Reversibility Gate(R1/R2/R3).
- **agent_runtime v0.1.5 프레임워크 전체 이식** — 공식 설치(`agent_runtime.yml`/lock, sync apply=150) · `agents/`(roles.yml+16역할)·`scripts/`(~70+providers/claude·codex·openai)·`docs/agent_bootstrap`·`specs/agent_loop`·루트 규약 5종 · 의존성(openai·PyYAML) · roles.yml Autofolio 튜닝(웹앱 경로 제거).
- **운영 문서 초기화 + 검증 GREEN** — `agents/lead_engineer/`에 STATUS·AUDIT-LOG·compound_log·tasks(INDEX·BACKLOG+VIEW-*) seed, `schemas/task.schema.json`, AGENTS §13/§14 추가 → `python scripts/check_agent_docs.py` **0 error**(경고만). dev역할 중복 제거 후 앱 **33 에이전트** 정상 로드, `tests/` **9 passed**, `schemas` 테스트 **12 passed**, 프레임워크 스크립트 테스트 **480/517 pass**.
- **프레임워크↔Autofolio 분리 운영** — agent_runtime 업데이트가 Autofolio 튜닝을 덮어쓰지 않도록 **계층 분리**. 분기 실측 결과 시임은 정확히 2파일(`AGENTS.md`·`agents/roles.yml`) → `agent_runtime.yml`의 `sync.unmanaged`로 호스트 소유 선언(`sync --check` **conflicts 2→0**, `--apply` 전체차단 해소). 통합/링크 문서 **`docs/AGENT_RUNTIME_INTEGRATION.md`**(계층 모델·분기 원장·업데이트 런북·업스트림 결함) 신설, AGENTS 오버레이는 `<!-- AUTOFOLIO-OVERLAY -->` 마커로 표시. 호스트 추가 파일(맥락)은 본래 sync 비대상이라 항상 안전.

---

## 🎯 다음 (우선순위)

### 1. P1.1b — 실 KIS 연동 + 포트폴리오 모델  ★진행중 (코어 구현·검증 완료, 2026-06-09)
> 사용자: **실전·모의계좌 개설 + API 신청 완료(2026-06-09)**. 키 발급·입력 완료.
- [x] **자격증명 입력**: paper·prod App Key/Secret/계좌번호 `.env` 입력 완료. `KIS_PAPER_BASE_URL`(vts:29443)·`KIS_PROD_BASE_URL`(:9443)·`KIS_TOKEN_PATH=/oauth2/tokenP` 명시. 환경별 해석은 `settings.resolve_settings()` 단일 지점.
- [x] **토큰 스모크 스크립트**: `scripts/kis_token_smoke.py`(paper+prod, 토큰 발급만이라 실전도 안전). **paper·prod 둘 다 발급 검증 완료**(올바른 엔드포인트), `resolve_settings()` 공유로 리팩터.
- [x] **`app/brokers/kis/kis_client.py` 5메서드 구현** — `get_current_price`·`get_positions`·`place_order`·`cancel_order`·`get_order_status`. 현행(2025) TR ID(매수 `TTTC0012U`/매도 `TTTC0011U`/취소 `TTTC0013U`/잔고 `TTTC8434R`/체결 `TTTC0081R`, paper `T/J/C→V` 치환·시세 `F`예외), rt_cd envelope·레이트리밋(EGW00201) 재시도. 근거 정본: **`docs/KIS_API_SPEC.md`**(공식 GitHub 교차검증). 단위테스트 17개. **라이브 paper 읽기검증(현재가·잔고) 완료**.
- [x] **환경별 base_url/token_path 자동 해석**(`KIS_ENV`→기본 URL + 환경별 키) — `resolve_settings()`. (이전: `settings.py`가 generic 키만 읽어 라이브 인증 실패하던 버그 동시 수정.)
- [~] **포트폴리오/손익 라이브화**: `backend.positions()`·`backend.holdings_df()`(positions+현재가+화이트리스트명 → 평가금액/평가손익/손익률/비중, mock과 동일 스키마) 어댑터. **포트폴리오 화면 보유종목 표 라이브 분기 완료**(`data_source==backend` 시 실 KIS, 실패 시 데모 폴백; 데모 렌더 AppTest 회귀검증). 홈 KPI·자산곡선·제안, 분석(백테스트·기여도)은 이력DB·에이전트·백테스트 엔진 의존이라 **후속**.
- [ ] 안전(MVP_SPEC §10/오류표): paper 검증 후에만 **1주 수동** 실주문(사람 승인 게이트). **paper 전용 주문 생애주기 스모크 `scripts/kis_paper_order_smoke.py`**(prod 하드가드·미체결가·자동취소) 추가 — 사람이 정규장에 `! python scripts/kis_paper_order_smoke.py`로 직접 실행. 자동 실주문 금지(에이전트 발주는 안전분류기도 차단).
- [ ] (후속) 엔진 market-fallback 의미 보정: KIS 주문은 접수(PENDING) 응답이라 `_fallback_to_market`의 즉시-FILLED 가정과 어긋남 → 시장가도 체결 폴링 경유하도록.

### 2. 거버넌스(④) 마무리
- [x] **`/retro` 워크플로** — `scripts/run_retro.py` (Performance Analyst→DA→Risk→Forward Actions, DB 주문로그 기반, 멀티에이전트, dry-run 지원, `.autofolio/retro/RETRO_*.md` 저장). (2026-06-10)
- [x] **IC 결정 → 매매 조건 자동 연결** — `agents.py` IC 결정문 파싱(`extract_condition_from_ic`) → 사람 확인 버튼 → `backend.add_condition(created_by="IC", auto_enabled=False)`. (2026-06-10)
- [ ] `execution-trader`, `compliance-officer` 에이전트.
- [ ] performance-analyst 에이전트 전용 SKILL.md + UI 탭.

### 3. 퀀트 리서치팀(③)
- [ ] `quant-researcher`·`backtest-engineer`·`data-engineer`·`optimization-quant` 에이전트 + 스킬.
- [ ] 백테스트 모듈 + **look-ahead/과최적화/생존편향 방어**(point-in-time).
- [ ] 분석 화면의 백테스트 탭을 실데이터로.

---

## 📋 백로그 (그룹별)

### 연동 · 알림 (멀티채널)
- [ ] Telegram 명령봇(`/status`·`/pnl`·`/approve`·`/kill`·`/ask`·`/ic`) — 기존 `notification/telegram_notifier.py` 확장.
- [ ] Kakao "나에게 보내기"(Kakao Login + talk_message), Notion 저널, Discord 채널/embed, Email 리포트.
- [ ] 알림 규칙·일일/주간 요약 리포트.
- [ ] SSO 실연결: Google OIDC(`st.login`) + Kakao/Naver(`streamlit-oauth`), 채널 OAuth 토큰.

### 자동 모드 · 안전
- [x] **스케줄러/데몬** — `scripts/run_paper_engine.py` (paper-only, 거래시간 가드, --dry-run, --interval, Telegram 알림 연동). (2026-06-10)
- [x] **L2 자동매매 토글 DB 연결** — settings.py auto_enabled 토글 → DB 즉시 반영, 리스크 한도 DB 저장. (2026-06-10)
- [ ] L3 감독형 자동 + 서킷브레이커 실집행.
- [ ] 종목별 모드(L0–L4) 실제 엔진 반영(현재 session_state만).

### 분석 (과거/미래)
- [ ] 과거: 트레이드 저널·손익 기여(attribution)·습관 진단(거버넌스/퀀트 연계).
- [ ] 미래: 시나리오·몬테카를로·예측 시그널·What-if·리밸런싱 플랜 실데이터.

### 개발팀 활용 (이식 에이전트)
- [ ] PR/코드리뷰 워크플로에 `independent-auditor`·`qa`·`lead-engineer` 연결.
- [ ] 요구→스펙 흐름에 `requirements-interviewer`·`research-agent` 활용.
- [~] **자율 머지 거버넌스**: 호스트 잠정 정본 `agents/lead_engineer/MERGE-POLICY.md`(+ `AGENTS.md` §15, `scripts/check_merge_policy_precedence.py`) 작성 — `auto_merge.py` 게이트 정본화·Autofolio R3 surface·업스트림 우선 교체 규칙. **업스트림 보고 필요**: `auto_merge.py`가 참조하는 `AGENTS.md §3.5`+`MEETING/EVIDENCE-2026-06-01`이 업스트림 미커밋(스크립트만 배포된 자기-불일치, §14 누락과 동류) → Issue 등록 후 §3.5 템플릿화되면 precedence swap.

### 기술부채 · 정리
- [x] 이식 비엔지니어 에이전트(ceo/owner/scribe 등 9종) Autofolio 맥락 튜닝 완료.
- [x] **엔진 market-fallback PENDING 보정** — `_poll_fill()` 헬퍼로 KIS 실브로커 PENDING 처리. (2026-06-10)
- [x] **구조화 로깅** — `get_structured_logger/log_event`, `logs/events.jsonl`, `scripts/tail_events.py`. (2026-06-10)
- [x] **GitHub Actions CI** — `.github/workflows/test.yml` (pytest + check_agent_docs). (2026-06-10)
- [ ] MVP_SPEC §5 구조도 업데이트.
- [ ] L3 서킷브레이커·일일예산 실집행.
- [ ] 테스트 커버리지 확대(리스크·backend 어댑터 AppTest).
- [ ] 기존 MVP UI(`streamlit_app.py`)와 신규 셸 통합 또는 역할 정리.
- [x] ~~Full agent_runtime 스캐폴딩 이식~~ ✅ 프레임워크 전체 설치(공식 sync, 150파일).
- [x] **중복 정리 완료** — dev 16역할은 프레임워크 정본 `agents/<role>/SKILL.md` 단일 소스, `kis-api-engineer`는 `agents/kis_api_engineer/SKILL.md`로 승격. 앱 `agents_runtime`이 정본 `agents/`(프론트매터 無, 폴더=이름) + `.claude/agents`(자산·거버넌스) 양쪽을 읽도록 확장, 중복 `.claude/agents/dev-team/` 제거(교차링크 경고 145→107).
- [x] **운영 스캐폴딩 1차 생성** — STATUS·AUDIT-LOG·compound_log·tasks(INDEX·BACKLOG)·`schemas/task.schema.json` 완료. CYCLE/reviews/reports는 첫 실작업 사이클에서 생성(미완).
- [ ] agent_runtime 스크립트 활용/검증: `subagent_dispatch`·providers(claude/codex/openai) 디스패치 스모크(키 필요). ⚠ `agent_orchestrator`는 상위 v0.1.5 템플릿에 `orchestrator_safety_gate.py`가 누락되어 import 불가 — 업스트림 보고/패치 필요.
- [ ] 프레임워크 자체 테스트(`pytest scripts`) 36 fail/1 error — 대부분 agent_runtime 고유 TASK 코퍼스·로컬 스케줄 데몬·호스트 경로 의존(Autofolio 회귀 아님). 기본 `pytest`는 `tests/`로 스코프(`pytest.ini`). 선별 그린화는 선택.
- [x] **업스트림 통합 핸드오프 전달 + PR** — 이식 전 경위·충돌·결과 종합 보고서 `docs/agent_runtime_handoff_report.md`(육하원칙, 핵심3/부속5/타임라인/부록) → agent_runtime **Issue [#1](https://github.com/ycpiglet/agent_runtime/issues/1)**(라벨 bug/enhancement/documentation) + **전수감사 보강 코멘트**(누락 모듈 2종·온보딩 pip vs clone·훅/스킬 설계·CI 미검증 근본원인). 안전한 결함 2건은 **PR [#2](https://github.com/ycpiglet/agent_runtime/pull/2)**(`schemas/task.schema.json` 동봉 + AGENTS §13–§14; 레포 테스트 94 passed·스키마 12 passed). 분석/재설계/반영은 업스트림 자유 판단(입력 형식).

---

## 진행 표기
`[ ]` 대기 · `[~]` 진행중 · `[x]` 완료 — 사이클마다 갱신. RETRO/Review의 Forward Actions TASK는 이 백로그로 합류한다(프레임워크 reviews/ + compound_log 규약, `agents/lead_engineer/`).
