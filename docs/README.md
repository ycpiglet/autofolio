# Autofolio 문서 (docs)

Autofolio = **에이전트 팀이 운용하는 개인용 멀티에셋 자동매매 OS** (KIS 기반, Quantamental + Agentic).

## 문서 맵

| 문서 | 내용 | 상태 |
|---|---|---|
| [ORG_PLAN.md](ORG_PLAN.md) | **조직 기획서** — 4축 조직(개발/자산/퀀트/거버넌스), Quantamental 의사결정 워크플로, AI 시장 정렬 | 기획 확정 |
| [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md) | **제품·시스템 설계서** — 운영 모드(L0–L4), 증권앱 기능셋, 과거/미래 분석, 멀티채널 연동(Telegram/Discord/KakaoTalk/Notion/Google), SSO·계정연동, 보안, 아키텍처, 로드맵 | 기획 확정 |
| [UI_SPEC.md](UI_SPEC.md) | **UI 설계서 (UI-First)** — 화면별 와이어프레임, SSO·연동 마법사, 운영모드 UI, mock-first 빌드 순서 | 기획 확정 |
| [EXTERNAL_APP_API_OWNER_MANUAL.md](EXTERNAL_APP_API_OWNER_MANUAL.md) | **외부 앱/API Owner 준비 매뉴얼** — Telegram/Kakao/Google/X/Naver/Discord/Notion/Slack 연동 전 회원가입·개발자 콘솔·API key·OAuth·검수·secret 준비물 | 운영 매뉴얼 |
| [AGENT_TEAMS.md](AGENT_TEAMS.md) | **구현된 팀 상세** — ①개발팀(17, agent_runtime 이식) + ②자산운용팀(15) 에이전트·스킬 | 구현 완료 |
| [BACKLOG.md](BACKLOG.md) | **할 일 목록·백로그** — 완료 현황 + 우선순위(P1.1b 실 KIS·거버넌스·퀀트·연동·자동모드) | 운영 중 |
| [../MVP_SPEC.md](../MVP_SPEC.md) | 원 기술 명세서 (요구사항·아키텍처·안전정책) | 초안 |
| [../README.md](../README.md) | 프로젝트 개요·빠른 시작 | — |

## 빠르게 보기
- **"전체 그림이 궁금"** → ORG_PLAN §1 (4축) + PRODUCT_BLUEPRINT §1 비전.
- **"auto 모드가 뭐야"** → PRODUCT_BLUEPRINT §2 (자율성 레벨 L0–L4).
- **"어떤 기능이 들어가"** → PRODUCT_BLUEPRINT §3·§4 (앱 패리티 + 분석 탭).
- **"폰에서 어떻게 써"** → PRODUCT_BLUEPRINT §5 (멀티채널 + 명령어).
- **"지금 뭐가 만들어졌나"** → ORG_PLAN §6 (구현 상태 매트릭스).

## 구현 상태 한눈에
```
① 개발팀        ✅ agent_runtime 16종 이식 + kis-api(전용) = 17 에이전트 · 엔진 KIS 연동 TODO
② 자산운용팀    ✅ 구현 완료 (15 에이전트 + 15 스킬)
③ 퀀트 리서치팀  📐 설계 완료 · 구현 대기
④ 거버넌스/Ops   🔄 P2: Devils-Advocate 에이전트 + IC 워크플로·결정로그 구현 · 나머지(성과/실행/컴플라이언스) 대기
에이전트 실연결   ✅ P2: Anthropic API 구동(.claude/agents 페르소나+스킬) · 키 없으면 데모 스텁
제품(모드·앱기능·연동·분석)  📐 설계 완료 · 단계별(P1~P4) 구현 대기
UI(화면·로그인·연동)         ✅ P1.0a/b/c + P1.1a(라이브 백엔드·키 불필요) 검증 완료 · ⏳ P1.1b 실 KIS 대기
```
