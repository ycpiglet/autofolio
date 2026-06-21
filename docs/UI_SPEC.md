# Autofolio UI 설계서 (UI_SPEC) — UI-First

> 상태: **기획 확정 · UI 최우선 구현 대상**
> 연계: [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md)(모드·기능·연동·아키텍처) · [ORG_PLAN.md](ORG_PLAN.md)(에이전트) · [README.md](README.md). 본 문서는 *화면·UX·구현 순서*를 정의한다.

---

## UI 차세대 이행 안내 (2026-06-17 갱신)

현재 운영 UI는 **Next.js 16 + FastAPI**다. 기존 Streamlit 8화면은 TASK-049에서 은퇴했고,
코드는 `archive/streamlit_ui/`에 보존한다. 이 문서의 아래 Streamlit 설계 내용은 제품
초기 설계 기록으로 남기며, 신규 UI 구현의 기준은 Next.js 앱과 아래 이행 스펙이다.

**차세대 Next.js 이행 설계**는 별도 스펙 문서를 참조:
[`docs/superpowers/specs/2026-06-13-ui-overhaul-design.md`](superpowers/specs/2026-06-13-ui-overhaul-design.md)

이행 방식: Owner 결정 — Next.js 16 + FastAPI 분리, 토스류 미니멀 라이트, 5단계 페이즈드.

**Phase 5 retirement 완료** (2026-06-17): `app/services/backend.py`가 백엔드 어댑터 원본이며,
Streamlit `app/ui/views`와 진입점은 archive로 이동했다. AppTest 스위트는 제거하고
`web/e2e/demo-walkthrough.spec.ts`가 8개 주요 Next.js 화면 순회를 검증한다.

---

## 1. 원칙 — UI-First, Mock-First
- UI를 **백엔드와 분리**해 **mock 데이터**로 먼저 완성한다. 실제 배포 앱처럼 동작·탐색 가능 → 이후 어댑터로 실데이터를 끼운다.
- 사용자친화 최우선: 적은 클릭, 명확한 상태 배지, 한국어 카피, 모바일 친화, 실수 방지(확인 모달·빈 상태·로딩).
- 현재 구현: **Next.js + FastAPI** 기반. 아래 Streamlit 설계는 archive된 레거시 기록이다.

## 2. 기술 스택 (무료·Python)
| 용도 | 선택 | 비고 |
|---|---|---|
| 프레임워크 | **Next.js 16 + FastAPI** | Streamlit 은퇴 완료 |
| 로그인 SSO | `st.login()`(OIDC·Google) + `streamlit-oauth`(Kakao/Naver) | BLUEPRINT §5.5 |
| 차트 | `plotly` / `st.line_chart`·`st.area_chart` | 캔들·자산곡선 |
| 표 | `st.dataframe`(정렬·필터) | 보유·내역 |
| 실시간 갱신 | `streamlit-autorefresh` / `st.fragment` | 시세·대시보드 |
| 상태 | `st.session_state` | 로그인·모드·mock store |
| 시크릿 | `secrets.toml` / `.env` | 토큰·자격증명 |

## 3. 정보구조 / 내비게이션
사이드바(좌) + 멀티페이지. 상단 **항상 노출**: 모드 배지(L0–L4) · 자동매매 ON/OFF · 🔴 킬스위치.

```
[사이드바]                         [상단바]  모드:L1 ⬩ 자동:OFF ⬩ 🔴 KILL
─ 🏠 홈 (대시보드)
─ 💼 포트폴리오
─ 🧾 매매 / 주문
─ 📒 내역 · 손익
─ 📊 분석 (과거 / 미래)
─ 🤖 에이전트 (팀 · 챗)
─ 🔔 알림
─ ⚙️ 설정 · 연동
```

## 4. 화면별 와이어프레임 (mock)
각 화면 = 레이아웃 + 구성요소 + (🔌 추후 백엔드 연결지점).

### 0) 로그인 (SSO)
```
        Autofolio
   ─────────────────────
   [  G   Google로 시작  ]
   [ 🟡  카카오로 시작   ]
   [ 🟢  네이버로 시작   ]
   ──────────────────
   게스트(데모)로 둘러보기 →
```
🔌 `st.login()`(Google) / `streamlit-oauth`(Kakao·Naver). 데모 = mock 세션.

### 1) 홈 / 대시보드
```
┌ 총자산 ───────┐ ┌ 일손익 ─┐ ┌ 누적손익 ┐ ┌ 현금 ┐
│ ₩12,340,000  │ │ +1.2%▲ │ │ +8.4%   │ │ 18%  │
└──────────────┘ └────────┘ └─────────┘ └──────┘
[ 자산곡선 차트 ································· ]
┌ 오늘의 제안(승인대기) ──┐ ┌ 최근 체결 ┐ ┌ 알림 ┐
│ • TIGER미국S&P 매수 ✅❌ │ │ 삼성전자… │ │ …   │
└─────────────────────────┘ └──────────┘ └─────┘
```
🔌 포트폴리오·엔진·제안큐·로그.

### 2) 포트폴리오
도넛(자산배분) + 보유표(종목·수량·평단·현재가·평가손익·비중) + **목표 대비 갭 바**. 🔌 `database`·`engine`.

### 3) 매매 / 주문
주문 패널(종목검색·매수/매도·지정/시장·수량·금액) + **목표가 조건 등록**(자동매매) + 미체결 목록. 라이브 주문은 *모드·게이트 통과 여부* 배지로 표시. 🔌 `engine`·`brokers`·`risk`.

### 4) 내역 · 손익
탭: 체결내역 / 일·월 손익 / 수수료·세금 / 배당. 기간·종목 필터, 내보내기(Notion·Sheets). 🔌 `repositories`.

### 5) 분석 (과거 / 미래)
```
[ 과거 ]  [ 미래 ]
과거 → 거래저널 · 손익기여(Attribution) · 회고(/retro) · 백테스트 · 습관진단
미래 → 시나리오 · 몬테카를로 · 리밸런싱 플랜 · 예측 시그널 · What-if
```
🔌 ③퀀트·④거버넌스(회고)·agents.

### 6) 에이전트 (팀 · 챗)
좌: 팀 트리(개발 · 자산[한국/미국/글로벌] · 퀀트 · 거버넌스). 우: **채팅 패널** — 에이전트 선택 후 자연어 대화(`/ask`), IC 소집(`/ic`). 🔌 agent layer.

### 7) 알림
알림 피드 + 채널 토글(Telegram/Kakao/Discord/Notion/Email) + 알림 규칙(가격·체결·리스크). 🔌 notification bus.

### 8) 설정 · 연동 (핵심)
```
[ 계정(SSO) ] [ 알림채널 ] [ 증권계좌 ] [ 운영모드 ] [ 리스크 ]

계정(SSO):  Google ✅연결   ·  Kakao  연결   ·  Naver  연결
알림채널:   Telegram[봇토큰__]  Kakao[나에게 연결]  Notion[토큰__]
            Discord[웹훅__]     Email[__]            (각 ✅ 상태배지)
증권계좌:   [ + 계좌 추가 ]                          (다계좌·다ID 지원)
            ┌ 별칭         증권사 환경  상태 ───────────────────┐
            │ 내KIS(실전)  KIS    실전  ✅  [기본][전환][수정][삭제] │
            │ 모의계좌      KIS    모의  ✅  [전환][수정][삭제]        │
            └─────────────────────────────────────────────┘
            추가폼: ID·App Key·Secret·계좌번호 → [연동하기] → 잔고조회 테스트 → ✅
            ⚠️ 소셜로그인 아님 · 자격증명 암호화 보관 · 1원인증 불필요(§5.8)
운영모드:   종목별  L0─L1─L2─L3─L4  슬라이더  +  전역 기본값
리스크:     일일예산 · 주문한도 · 종목상한 · 서킷브레이커 손실% · 거래시간
```
🔌 BLUEPRINT §5.5–§5.8 · `config` · Secrets Vault. 모든 연동(SNS·채널·증권 다계좌)은 **플랫폼 계정 하나**로 묶여 관리(§5.7).

## 5. 운영 모드 & 안전 UI
- 상단바 상시: 모드 배지 · 자동 ON/OFF · **킬스위치(빨강, 1클릭)**.
- L3+ 전환 시 **확인 모달**(예산·한도·서킷브레이커 고지). 서킷브레이커 발동 = 전역 경고 배너 + 자동 정지 상태.

## 6. 디자인 가이드 (쉽고 친근)
- 카드형 KPI · 상태 배지(연결=초록 / 주의=노랑 / 위험=빨강) · 넉넉한 여백.
- 손익 색(상승=빨강 / 하락=파랑, 한국 관습) 토글 제공.
- 빈 상태·로딩 스켈레톤·확인 모달로 실수 방지. 한국어 친근한 카피.
- 모바일 폭 대응(`st.columns` 반응형).

### 6.1 포트폴리오 탭 시각 분석 규칙

포트폴리오 첫 화면은 텍스트 진단보다 시각 분석을 우선한다.

- 상단 KPI 카드는 클릭 시 하단 주제를 전환한다. 총자산/현금은 요약, 평가손익/일간손익/월간수익률은 성과, 보유종목은 보유 탭으로 이동한다.
- 첫 화면 핵심 그래프는 `자산 추이`, `목표 배분 도넛`, `자산군 노출`, `섹터/지역/전략 노출`, `보유 집중도`, `성과 기여/손실 기여`로 둔다.
- 자산 추이는 선 차트 단독이 아니라 현재값, 기간 변화, 변화율, 고점, 저점을 함께 보여줘 차트의 의도를 먼저 설명한다.
- 숫자는 모노스페이스 대신 Pretendard + `tabular-nums`를 사용한다. 자릿수 정렬은 유지하되 금융 앱의 일반 UI 질감과 맞춘다.
- 강조는 부분 영문 토큰이 아니라 의미 단위로 한다. 예: `SK하이닉스`의 `SK`만 강조하지 않고, 숫자/금액/비율 및 `ETF`, `현금`, `채권`, `주식` 같은 자산 키워드를 일관되게 강조한다.
- 도움말은 컨테이너 안 absolute tooltip이 아니라 viewport 기준 fixed tooltip으로 띄워 사이드바나 스크롤 컨테이너에 잘리지 않게 한다.

## 7. UI-First 빌드 순서
- **P1.0a 스캐폴드** ✅ — 멀티페이지·내비·테마·`session_state` + **mock 데이터 레이어**. (검증: AppTest 10/10, 서버 200)
- **P1.0b 화면** ✅ — 8화면 + 손익 색 토글·빈 상태·로딩·킬 확인 다이얼로그·새로고침·종목별 모드.
- **P1.0c 로그인·연동** ✅ — **로컬 ID/PW(해시·가입겸로그인) + Google OIDC(`st.login`, secrets 설정 시) + 게스트**, 연동 마법사가 **암호화 vault**에 다계좌/채널 실제 저장, KIS 토큰 테스트 호출. (검증: 유닛 6 + AppTest 10 = 16/16)
- **P1.1 실데이터 연결** 🔄 *진행중*
  - **P1.1a ✅** — `backend.py` 어댑터(**Mock 브로커 + SQLite, 증권 키 불필요**) + 데이터 소스 토글(데모/라이브). 매매·내역·에이전트를 라이브 연결: 화이트리스트·시세·목표가 조건·엔진 1회 실행·주문로그·리서치 제안. (검증: 백엔드 유닛 7 + AppTest 13 = 20/20, 서버 200)
  - **P1.1b ⏳** — 실 KIS(증권계좌·API 키 발급 후) + 포트폴리오/손익 백엔드 모델 + 홈/포트폴리오/분석 라이브화.

> 핵심: **인터페이스(화면) ↔ 데이터(어댑터) 분리.** 그래야 UI를 먼저·독립적으로 완성하고 실제 배포 앱처럼 다듬을 수 있다.

## 8. 폴더 구조 제안
```
app/
├── api/                    # FastAPI backend
├── services/backend.py     # 실 백엔드 어댑터(Mock 브로커+SQLite, 키 불필요)
├── services/               # 도메인 서비스 레이어
└── ui/                     # vault/auth/state 등 일부 레거시 유틸만 잔존
web/
└── src/app/                # Next.js 8개 주요 화면 + 온보딩/로그인
archive/streamlit_ui/       # 은퇴한 Streamlit 진입점과 views 보존
```
> 실행: `run_ui.bat` 또는 `run_api.bat` + `run_frontend.bat`.
> 시크릿: `.streamlit/secrets.toml`(gitignore) — 양식은 `.streamlit/secrets.toml.example`. 자격증명은 `.autofolio/`(gitignore)에 Fernet 암호화 저장.

## 9. Sources
- [Streamlit auth/OIDC](https://docs.streamlit.io/develop/concepts/connections/authentication) · [st.login](https://docs.streamlit.io/develop/api-reference/user/st.login) · [Google OIDC 튜토리얼](https://docs.streamlit.io/develop/tutorials/authentication/google)
- [Kakao Message API](https://developers.kakao.com/docs/latest/en/kakaotalk-message/common) · [PyKakao 나에게 보내기](https://wooiljeong.github.io/python/pykakao-message/)
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) · [Notion API with Python](https://www.pynotion.com/getting-started-with-python/)
