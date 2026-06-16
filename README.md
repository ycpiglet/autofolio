# Autofolio

**Autofolio** — 한국투자증권(KIS) Open API 기반 **에이전트 자동매매 OS (Agentic Quant Portfolio OS)**.

멀티에이전트(자산팀·퀀트팀·거버넌스)가 협업하고, Streamlit UI + Telegram 봇으로 어디서든 관제·명령.

| | |
|---|---|
| **브로커** | 한국투자증권(KIS) Open API |
| **에이전트** | 40개 (개발·자산·퀀트·거버넌스) |
| **언어** | Python 3.10+ |
| **DB** | SQLite |
| **UI** | Streamlit |
| **알림** | Telegram 봇 (`/status /pnl /positions /conditions /engine /propose`) |
| **CI** | GitHub Actions (pytest + check_agent_docs) |

---

## 한국어

이 저장소의 운영 정본은 `AGENTS.md`입니다. 도구별 안내는 `CLAUDE.md`,
`GEMINI.md`, `CURSOR.md`를 보조로 보되 충돌하면 `AGENTS.md`와
`agents/lead_engineer/`의 최신 기록을 우선합니다.

다음 세션을 이어받을 때는 `agents/project/NEXT-SESSION-POINTER.yml`,
`agents/project/`, `agents/lead_engineer/STATUS.md`,
`agents/lead_engineer/tasks/BACKLOG.md`를 먼저 확인합니다.

## English

The repository operating protocol is `AGENTS.md`. Tool-specific files such as
`CLAUDE.md`, `GEMINI.md`, and `CURSOR.md` are companion guidance; when they
conflict, follow `AGENTS.md` and the latest records under
`agents/lead_engineer/`.

To resume work, start with `agents/project/NEXT-SESSION-POINTER.yml`,
`agents/project/`, `agents/lead_engineer/STATUS.md`, and
`agents/lead_engineer/tasks/BACKLOG.md`.

---

## 빠른 시작

```powershell
# 1. 환경 설정
.venv\Scripts\Activate.ps1          # 또는 python -m venv .venv
pip install -r requirements.txt

# 2. 자격증명
copy .env.example .env              # .env 편집: KIS_PAPER_APP_KEY 등

# 3. DB 초기화
python scripts/init_db.py

# 4. 앱 실행 (신 멀티페이지 셸)
run_ui.bat                           # 또는 streamlit run app/ui/autofolio_app.py
```

> **구 MVP 단일화면**: `streamlit run app/ui/streamlit_app.py` (레거시·참조용)

---

## 주요 스크립트

| 스크립트 | 설명 |
|---|---|
| `scripts/kis_token_smoke.py` | KIS 토큰 발급 연결 검증 (paper+prod) |
| `scripts/kis_paper_order_smoke.py` | paper 전용 주문 생애주기 스모크 (정규장 사람 실행) |
| `scripts/run_paper_engine.py` | 모의투자 자동 실행 스케줄러 (`--dry-run` 지원) |
| `scripts/run_retro.py` | 멀티에이전트 회고 워크플로 |
| `scripts/run_daily_summary.py` | 일일 요약 리포트 |
| `scripts/tail_events.py` | `logs/events.jsonl` 실시간 모니터링 |
| `scripts/auto_merge.py <PR>` | 자율 PR 머지 게이트 |
| `scripts/report_upstream_bug.py` | upstream 버그 자동 Issue 생성 |

---

## 운영 모드 (자율성 레벨)

| 레벨 | 이름 | 동작 |
|---|---|---|
| L0 | 관찰 | 정보 표시만 |
| L1 | 자문 | 제안 생성, 건건이 사람 승인 |
| L2 | 반자동 | 사전 플레이북 내 조건 자동 대기 |
| L3 | 감독형 자동 | 예산/가드레일 내 자율 실행 (서킷브레이커 필수) |
| L4 | 완전자동 | 하드리밋 내 완전 자율 |

---

## 안전 기본값

- `KIS_ENV=mock` (기본) — 실주문 없음
- 자동매매 기본값 OFF
- 킬스위치 1버튼 전체 중단
- 화이트리스트 종목만 거래
- 서킷브레이커 (일손실 한도 초과 시 자동 정지)
- mock → paper(모의) → prod 단계 승급

---

## 테스트

```powershell
pytest                          # 128개 테스트
python scripts/check_agent_docs.py   # 0 error 게이트
```

---

## 면책

이 프로젝트는 개인 학습·자동화 도구이며 투자 권유·수익 보장이 아닙니다.  
실전 자동매매 전에 반드시 모의투자와 소액 수동 테스트를 거치세요.
