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

## 현재 상태
- agent_runtime v0.1.5 프레임워크 전체 이식 완료 + 의존성(openai·PyYAML) + roles.yml Autofolio 튜닝 + 운영 문서 초기화(STATUS·INDEX·AUDIT-LOG·compound_log·BACKLOG).
- 운영 사이클(CYCLE/REVIEW)은 아직 미시작 — 첫 실작업 사이클에서 생성.

## 활성 작업
- 없음(설정 완료 단계). 다음 우선순위는 `docs/BACKLOG.md` §다음 참조.
