# agent_runtime 통합 가이드 — 프레임워크(틀) ↔ Autofolio(맥락) 분리 운영

> **목적**: `agent_runtime`(재사용 프레임워크 = "틀")의 업데이트가 Autofolio 고유 튜닝("맥락·상황·목적·비전")을 **덮어쓰지 않도록 계층을 분리**하고, "이 프레임워크를 Autofolio가 *어떻게* 활용하는가"를 한 곳에 링크한다.
> 이 문서 자체는 **호스트 소유**(템플릿 아님) — `sync` 가 건드리지 않는다.
> **관계·전략 정본**(플랫폼↔제품, 채택 원칙)은 [`AGENT_RUNTIME_RELATIONSHIP.md`](AGENT_RUNTIME_RELATIONSHIP.md). 이 문서는 그 *기술 절차* 편이다.
> 갱신: 2026-06-09

---

## 1. 계층 모델 (3 layers)

| 계층 | 무엇 | 위치(예) | 소유 | `sync` 동작 |
|---|---|---|---|---|
| **① 프레임워크(틀)** | agent_runtime 템플릿 150파일 | `AGENTS.md`* · `CLAUDE/GEMINI/CURSOR.md` · `scripts/**` · `agents/<role>/SKILL.md` · `agents/lead_engineer/{SKILL,TOKEN-BUDGET,GOTCHAS,...}` · `docs/agent_bootstrap/**` · `specs/**` | 업스트림 | 정본 그대로. `sync --apply` 로 업데이트 수신. **직접 편집 금지** |
| **② Autofolio 오버레이(맥락)** | 호스트가 *새로 추가*한 모든 파일 | `docs/{ORG_PLAN,PRODUCT_BLUEPRINT,UI_SPEC,AGENT_TEAMS,BACKLOG}.md` · `MVP_SPEC.md` · `app/**` · `.claude/agents/{asset-team,governance}/**` · `agents/kis_api_engineer/SKILL.md` · `agents/lead_engineer/{STATUS,AUDIT-LOG,compound_log,tasks/**}` · `schemas/task.schema.json` · `pytest.ini` · **이 문서** | Autofolio | **안 봄**(템플릿에 없는 경로). 항상 안전 |
| **③ 시임(seam)** | 편집이 불가피한 템플릿 파일 | `AGENTS.md`, `agents/roles.yml` | Autofolio(분기) | `agent_runtime.yml` 의 `sync.unmanaged` 로 선언 → **건너뜀**. 업스트림 변경은 §4 절차로 수동 반영 |

\* `AGENTS.md` 는 원래 ①이지만 현재 ③(시임)으로 분리되어 있다(§3 참조).

### 작동 원리 (코드 근거: `agent_runtime/sync.py`)
- `sync` 는 **템플릿에 존재하는 파일만** 관리한다. 호스트가 새로 만든 파일은 애초에 비교 대상이 아니다 → **②는 자동으로 안전**.
- 편집한 템플릿 파일은 lock 다이제스트(`agent_runtime.lock.json`)와 불일치 → 기본 **conflict**. `sync.allow_silent_overwrite: false` 라 **절대 조용히 덮어쓰지 않는다**.
- 단, conflict 가 하나라도 있으면 `sync --apply` 는 **0건 적용 후 중단**(all-or-nothing). 그래서 시임 파일은 `unmanaged` 로 빼서 다른 148파일 업데이트를 막지 않게 한다 → **③**.

---

## 2. "맥락"(②)이 사는 곳 — Autofolio 소스

프레임워크는 **틀만** 제공하고, 상황·목적·비전·역할매핑은 아래 호스트 파일이 제공한다(전부 sync-안전):

- **제품/조직 기획**: `docs/ORG_PLAN.md` · `docs/PRODUCT_BLUEPRINT.md` · `docs/UI_SPEC.md` · `docs/AGENT_TEAMS.md` · `docs/BACKLOG.md` · `MVP_SPEC.md` · `README.md`
- **운영 상태/컨텍스트**: `agents/lead_engineer/STATUS.md`(§Autofolio 컨텍스트) · `AUDIT-LOG.md` · `compound_log.md` · `tasks/INDEX.md`
- **자산운용팀(투자 리서치·제안)**: `.claude/agents/asset-team/**` · `.claude/agents/governance/**`
- **Autofolio 전용 개발 역할**: `agents/kis_api_engineer/SKILL.md`
- **앱/연결부**: `app/**` — 특히 `app/ui/agents_runtime.py` 가 정본 `agents/<role>/SKILL.md`(개발팀) + `.claude/agents`(자산·거버넌스) 페르소나를 로딩해 Anthropic API 로 구동 · `schemas/task.schema.json` · `pytest.ini`

> 즉 "agent_runtime 이 어떻게 활용되는가"의 실연결부는 **`app/ui/agents_runtime.py`** 와 **`agents/roles.yml`**(역할↔스킬↔경로 매핑)이고, 그 둘이 프레임워크의 역할 정본(`agents/<role>/SKILL.md`)을 Autofolio 맥락에 연결한다.

---

## 3. 시임(③) 분기 원장 (Divergence Ledger)

업데이트 시 충돌·재조정 대상은 **이 둘뿐**. (`agent_runtime sync --check` 로 언제든 재확인.)

| 파일 | 분기 내용 | 이유 | 업스트림 변경 시 재조정 |
|---|---|---|---|
| **`AGENTS.md`** | `<!-- AUTOFOLIO-OVERLAY -->` 블록으로 **§13 Handoff · §14 Token Budget**(`TOKEN-BUDGET.md` 링크) 추가 | 업스트림 템플릿 `AGENTS.md` 엔 §14 가 없는데, 업스트림 검사기 `scripts/check_agent_docs.py::check_token_budget` 가 §14 의 `TOKEN-BUDGET.md` 참조를 **요구**(없으면 ERROR) — **업스트림 자체 불일치**(자기 검사기가 요구하는 걸 자기 템플릿이 누락) | 업스트림이 §14 를 추가하면 → 오버레이 블록 제거, pristine 복귀, `unmanaged` 에서 제외. 그 전엔 §0–§12 본문 변경만 수동 병합 |
| **`agents/roles.yml`** | 16역할 레지스트리를 Autofolio 경로/맥락으로 튜닝(웹앱 스택 경로 제거, Streamlit/SQLite/KIS 경로로 교체) | `roles.yml` 은 **프로젝트 역할 레지스트리** — 본질적으로 호스트 소유(어떤 역할을, 어떤 파일 경로로 둘지) | 업스트림이 역할 스키마(필드)를 바꾸면 `check_agent_docs` 가 신호. 새 필드만 수동 반영 |

**원칙**: 이 표에 없는 템플릿 파일은 편집하지 않는다. 새 편집이 불가피하면 먼저 이 표에 등록하고 `agent_runtime.yml` 의 `unmanaged` 에 추가한다.

### 3.1 자율 머지 거버넌스 — 우선순위(업스트림 우선, 충돌 회피)

업스트림 v0.1.5 는 자율 머지/심의 **스크립트**(`auto_merge.py` 등)는 실어 보냈으나, 그것이 참조하는 **거버넌스 §3.5(자율 머지 규칙)·`MEETING/EVIDENCE-2026-06-01`** 은 레포에 미커밋(2026-06-09 확인). 그래서 호스트가 잠정 정본 [agents/lead_engineer/MERGE-POLICY.md](../agents/lead_engineer/MERGE-POLICY.md)(오버레이 ②) + `AGENTS.md` 오버레이 §15(포인터)로 둔다.

**설계상 충돌 회피**: 공통 규칙을 **공유 본문(`AGENTS.md §0–§12`)에 넣지 않고** 호스트 전용 파일(②)·오버레이 포인터로 격리한다. ② 는 sync 비대상이라 업스트림과 **병렬 진화·자동충돌 없음**. 업스트림 §3.5 가 §0–§12 에 추가돼도 우리 §15(오버레이)·MERGE-POLICY 와 텍스트 충돌이 없다.

**우선순위(업스트림 완성 시 강제 반영)**: 설치된 업스트림 템플릿 `AGENTS.md` 가 §3.5 를 얻으면 →
1. 업스트림 §3.5 **전부 채택(정본)**, 2. `MERGE-POLICY.md` 는 **Autofolio R3 surface 애드덤만 잔존(조금)**, 3. `AGENTS.md` 오버레이 §15 제거→한 줄 포인터, 4. 본 §3.1 "반영 완료"로 갱신.
**감지/강제**: `python scripts/check_merge_policy_precedence.py`(업스트림 §3.5 발견 시 non-zero). §4 런북 4-bis 단계로 돌린다.

**✅ 반영 완료 (v0.3.0, issue #103)**: 업스트림 v0.3.0 `AGENTS.md`가 **§6 Autonomous Delivery Lane**을 정본으로 보유 → 호스트 AGENTS.md를 업스트림 v0.3.0 본문(590L) 베이스로 재구성하고, autofolio 오버레이를 §15 Handoff·§16 Token Budget·**§17 Autofolio R3 Surface**(=Autonomous Delivery Lane의 R3 보정, MERGE-POLICY 애드덤)·§18 Upstream Bug Reporting으로 재번호. 업스트림이 흡수한 **구 §18 Live Work Continuity는 제거**(업스트림 §1.5 Live Work Pointer + §8.5 Measured Improvement Loop + §8.6 Repeated Request API가 대체). `check_merge_policy_precedence` OK. `agents/roles.yml`은 업스트림 신규 스키마 필드 0 → 현행 유지(host 소유 레지스트리).

---

## 4. 업데이트 런북

```powershell
# 0) 새 버전 지정: agent_runtime.yml 의 upstream.ref 갱신 후 패키지 업그레이드
#    pip install --upgrade "agent_runtime @ git+https://github.com/ycpiglet/agent_runtime.git@<새ref>"

# 1) 점검 — conflicts=0 이어야 안전(시임 2파일은 unmanaged 라 안 잡힘)
.\.venv\Scripts\agent_runtime.exe sync --check --root .

# 2) 미리보기 — 업스트림이 바꾼 파일 diff
.\.venv\Scripts\agent_runtime.exe sync --diff  --root .

# 3) 적용 — ②(호스트 추가)·③(unmanaged)은 손대지 않고 ①만 업데이트
.\.venv\Scripts\agent_runtime.exe sync --apply --root .

# 4) 시임 점검 — unmanaged 라 sync 가 안 보므로, 정본 템플릿과 우리 파일을 직접 비교
.\.venv\Scripts\python.exe -c "import agent_runtime,os,difflib; from pathlib import Path; tp=Path(os.path.dirname(agent_runtime.__file__))/'templates'/'project'; [print('=== '+r+' ==='+chr(10)+((chr(10).join(difflib.unified_diff((tp/r).read_text(encoding='utf-8').splitlines(),Path(r).read_text(encoding='utf-8').splitlines(),'upstream/'+r,'host/'+r,lineterm=''))) or '(차이 없음)')) for r in ['AGENTS.md','agents/roles.yml']]"

# 4-bis) 자율 머지 거버넌스 우선순위 점검 (§3.1) — 업스트림이 §3.5 를 얻었으면 교체 강제
.\.venv\Scripts\python.exe scripts/check_merge_policy_precedence.py

# 5) 검증
.\.venv\Scripts\python.exe scripts/check_agent_docs.py   # 0 error 유지
.\.venv\Scripts\python.exe -m pytest -q                  # tests/ green
```

4단계에서 업스트림이 시임 파일을 바꿨다면, 그 변경을 **수동으로** 우리 파일에 병합한다(오버레이 블록·Autofolio 튜닝은 보존). 보존이 핵심이므로 자동 적용하지 않는다.

---

## 5. 시임을 줄이는 방향 (업스트림 개선 제안)

분기는 적을수록 좋다. 다음 업스트림 결함을 보고/패치하면 시임/마찰이 준다:
- **`AGENTS.md` §14 누락** — 업스트림 검사기가 요구하는 `TOKEN-BUDGET.md` §14 참조를 업스트림 `AGENTS.md` 가 안 가짐. 업스트림에 §14 추가되면 `AGENTS.md` 시임 해제 가능.
- **`scripts/orchestrator_safety_gate.py` 누락** — `scripts/agent_orchestrator.py` 가 import 하는데 v0.1.5 템플릿에 파일이 없어 오케스트레이터 import 불가(`test_role_mentions` collection-error). 호스트 추가 파일로 임시 보강하거나 업스트림 패치 대기.

---

## 6. 표준 절차 — 모든 프레임워크 변경은 이슈로 추적 (MANDATORY)

agent_runtime(①·③) 또는 "순수 autofolio 가 아닌" 공통 인프라를 건드리는 **모든** 작업은
**반드시 GitHub 이슈로 추적**한다. 예외 없다.

1. **착수 전 이슈 생성** — 무엇을·왜·검증계획. (예: 업스트림 vN→vM sync, 시임 재조정, 게이트 변경)
2. **진행 중 업데이트** — 의미 있는 단계마다 이슈에 코멘트(적용 결과·검증 수치·후속).
3. **PR 연결** — PR 본문에 `Refs #<issue>` / `Closes #<issue>`.
4. **업스트림 귀속** — 호스트 개선분·업스트림 버그는 **`ycpiglet/agent_runtime` 리포 이슈**로 역제안/보고해 분기를 수렴시킨다(§5).
5. **autofolio 고유(②③)만 호스트에 남기고, 나머지(①)는 업스트림 정본을 채택**한다(이 원칙이 곧 "순수 autofolio 제외, 나머지는 agent_runtime 반영").

> 근거: 추적 없는 프레임워크 드리프트가 v0.3.0 sync 때 10건 충돌로 누적됐다(issue #101 참조). 이슈-우선 추적으로 분기·재작업을 방지한다.

## 7. 한 줄 요약

- **틀 = agent_runtime(①, 정본·자동 업데이트).** **맥락 = Autofolio 추가 파일(②, 항상 안전).** **시임 = `unmanaged`(③, 수동 재조정).**
- 업데이트는 `sync --check → --diff → --apply` (+ `lock --write`) 로 받고, 시임은 §4-4 로만 손댄다. Autofolio 튜닝은 **절대 자동으로 덮어써지지 않는다.**
- **모든 프레임워크 변경은 이슈로 추적한다(§6, MANDATORY).**
