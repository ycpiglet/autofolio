# [Host Integration Report] Autofolio ↔ agent_runtime v0.1.5 — 이식 전체 경위·충돌·결과 및 재구조화 입력

> **성격 — 이것은 "지시"가 아니라 "입력"입니다.** 분석·재설계·구현·이슈 분할·검토·반영 여부는 **agent_runtime 측이 자유롭게 판단·기획**하세요. 본 문서는 그 판단의 근거(발생경위·충돌·결과)를 육하원칙으로 정리한 원자료입니다. 그대로 보관하거나, 필요한 단위로 분해해 이슈/디자인노트로 재사용하셔도 됩니다.
>
> 작성: 2026-06-09 · 작성 주체: Autofolio 호스트의 Lead Engineer(Claude Code) · 대상 버전: **agent_runtime v0.1.5**

---

## 0. 육하원칙 요약 (5W1H)

| 항목 | 내용 |
|---|---|
| **Who** | 호스트 = **Autofolio**(1인 소유 개인 자산운용 OS, KIS 기반 국장 자동매매). 작업 주체 = Lead Engineer(Claude Code, model `claude-opus-4-8`). |
| **What** | agent_runtime v0.1.5 **프레임워크 전체(템플릿 150파일)** 를 호스트에 이식하고, **"틀=프레임워크 / 맥락=호스트"** 로 분리 운영. |
| **When** | 2026-06-08 ~ 06-09. |
| **Where** | `github.com/ycpiglet/autofolio`(프레임워크와 **별개 레포**). 프레임워크 출처 = pip 패키지 `agent_runtime` + `templates/project/`(150). |
| **Why** | Autofolio는 **맥락·상황·목적·비전만** 제공하고, 운영 틀(에이전트 협업·BRIEF/PLAN 리포팅·Reversibility Gate·검증 게이트)은 **전부 agent_runtime에서 가져와 재사용**하려는 의도. 호스트는 프레임워크를 "고쳐 쓰는" 게 아니라 "그대로 쓰되 맥락만 얹는다". |
| **How** | 공식 `agent_runtime sync --apply`(150) → `lock --write` → 의존성 설치 → `roles.yml` 튜닝 → 운영문서 seed → `check_agent_docs.py`/`pytest` 검증 → 시임 분리(`sync.unmanaged`). 상세는 §3 타임라인. |

**핵심 결론 한 줄**: 프레임워크는 잘 작동하지만, **(a) 호스트 맥락을 읽어 들이는 규약이 없고, (b) sync가 binary라 불가피한 호스트 편집이 영구 충돌이 되며, (c) clean install이 자기 검사기/의존을 충족 못 해 red로 시작**합니다. 이 셋이 "재구조화"의 직접 입력입니다.

---

## 1. 핵심내용 (CORE) — 재구조화에 직접 들어갈 것

> 우선순위·해법 선택은 그쪽 자유. 아래는 "무엇이/왜 문제였나"의 근거.

### CORE-1. 호스트 "맥락 주입" 규약 부재  ★다음 버전 본체
- **무엇**: 프레임워크는 틀만 주는데, 호스트가 *목적/도메인/비전/역할매핑/안전제약*을 **어디에 두면 프레임워크가 읽는지** 정의가 없음.
- **경위/결과**: Autofolio는 맥락을 (a) 템플릿 파일 편집(→충돌), (b) 프레임워크가 모르는 임시 호스트 파일(`STATUS.md` 컨텍스트 블록, `docs/*`)에 흩뿌리는 식으로 우회. 프레임워크가 호스트 의도를 **"읽을" 단일 진입점이 없다**.
- **개선 방향(예시, 택일 자유)**: 부트스트랩/에이전트 start가 읽는 **고정 read-location** 규약화 — 예) `host/context.yml`(또는 `CONTEXT.md`), 스키마 `project_purpose · domain · vision · glossary · roles_overlay · safety_constraints · stack`. **항상 unmanaged**로 정의. 프레임워크가 이를 읽어 AGENTS/STATUS/에이전트 컨텍스트에 주입(없으면 우아하게 생략). → 사용자가 말한 "다음 버전에서 어디서 정보를 읽는다"가 정확히 이것.

### CORE-2. sync가 binary — 오버레이/머지 개념 부재
- **무엇**: `agent_runtime/sync.py` 기준 파일 상태가 `pristine-managed` / `unmanaged(동결)` / `blocking-conflict` 셋뿐.
- **경위/결과**: 템플릿 파일을 **한 줄만** 호스트화해도(lock digest 불일치) **영구 conflict**가 되고, `apply_updates`는 **conflict가 하나라도 있으면 0건 적용 후 중단**(all-or-nothing). 즉 불가피한 한 줄 때문에 나머지 업데이트가 전부 막힘. Autofolio는 시임 2파일을 `sync.unmanaged`로 빼서 우회했지만, unmanaged는 "동결"이라 업스트림 개선을 못 받음.
- **개선 방향(예시)**: (a) `@include`/**managed-region 마커**(마커 밖 호스트 편집은 업데이트에도 생존), (b) 파일별 3-way 머지, (c) "managed base + host override" 레이어, 최소 (d) `--apply --skip-conflicts`(conflict 파일만 건너뛰고 나머지 적용).

### CORE-3. clean install이 green이 아니다 — 프레임워크가 자기 검사기/의존을 미충족한 채 배포  ★즉시 수정 가능
신규 호스트에서 `sync apply → check_agent_docs → pytest`가 **바로 green이어야** 하는데, v0.1.5는 아래 3건으로 깨짐(전부 재현·확인):

| # | 결함 | 발생경위 | 즉시 해법 |
|---|---|---|---|
| 3a | **`AGENTS.md` §14 누락** | `scripts/check_agent_docs.py::check_token_budget`(L1314-1318)가 `AGENTS.md`에 `"TOKEN-BUDGET.md"` 문자열(§14)을 **ERROR로 강제**. 그런데 템플릿 `AGENTS.md`는 §12에서 끝나 §14가 없음 → fresh install이 자기 검사기를 통과 못 함. 호스트가 AGENTS.md를 편집해야만 green = **강제 시임 발생**. | 템플릿 `AGENTS.md`에 §14(Token Budget, `agents/lead_engineer/TOKEN-BUDGET.md` 링크) 추가. |
| 3b | **`schemas/task.schema.json` 미동봉** | `scripts/validate_task_schema.py`가 `ROOT/schemas/task.schema.json`을 `load_schema()`하고, `scripts/test_validate_task_schema.py`는 module-import 시 `load_schema()` 호출 → 파일 부재 시 **pytest collection-error**(전체 스위트 중단). | 템플릿에 `schemas/task.schema.json` 동봉. (테스트에서 역설계해 **12개 테스트 통과** 확인한 스키마를 §6 부록에 첨부.) |
| 3c | **`scripts/orchestrator_safety_gate.py` 미동봉** | `scripts/agent_orchestrator.py`(L35)가 `import orchestrator_safety_gate as safety_gate` 후 `safety_gate.evaluate_call(owner_role, intent, task_id, inbox)` 호출. 그런데 이 모듈이 **템플릿·패키지 어디에도 없음** → `agent_orchestrator` import 불가, `scripts/test_role_mentions.py` collection-error. | 의도된 게이트 모듈을 동봉(인터페이스: `evaluate_call(...) -> decision{allow/blocked/...}`). **호스트가 의도를 몰라 stub 작성은 보류** — 업스트림이 정본 제공 권장. |

> 제안: **"clean install → green"을 CI 게이트**로. 위 3건은 호스트가 손대기 전에 프레임워크가 자기 일관성을 갖추는 문제.

---

## 2. 부속내용 (SUPPLEMENTARY) — 품질·DX 개선 (반영 선택)

### SUP-1. `roles.yml`이 단일 managed 파일
역할 레지스트리는 **본질적으로 프로젝트별**(어떤 역할을, 어떤 파일 경로로). 단일 managed라 호스트가 편집→충돌(Autofolio 시임 2개 중 하나). → **framework 기본 roles + `roles.host.yml` 확장/오버라이드** 레이어. 그러면 호스트 고유 역할(예 `kis-api-engineer`)이 1급이 되고, 역할 정의 업데이트가 충돌 없이 흐름.

### SUP-2. 프레임워크 role 문서가 Claude Code 에이전트 포맷과 불일치
agent_runtime은 `agents/<role>/SKILL.md`(**프론트매터 없는 plain md**)로 역할을 정의. 그런데 Claude Code 네이티브 서브에이전트는 `.claude/agents/*.md` + **YAML 프론트매터**(`name/description/model/color/tools`)를 요구. → Claude Code 호스트는 둘을 **수동 브리지**해야 함(Autofolio는 앱 로더가 양쪽을 읽도록 구현 + 초기엔 `.claude/agents/dev-team/`에 프론트매터 단 복사본을 만들었다가 중복·링크경고로 제거). → **선택지**: (a) 역할 SKILL.md에 선택적 프론트매터 허용, (b) `agents/<role>/`→`.claude/agents/` 변환 어댑터 제공, (c) 무관심(호스트 책임으로 명시). CORE-1(맥락 규약)과 함께 보면 "역할을 호스트 에이전트 런타임에 어떻게 노출하나"가 공통 질문.

### SUP-3. 자체 테스트 ↔ 호스트 테스트 미분리
`scripts/test_*.py` **~46개 중 36개**가 agent_runtime **고유 TASK 코퍼스 / 로컬 스케줄 데몬 / 호스트 경로**에 의존(`test_task_api`·`test_task_mcp`·`test_session_start_hook`·`test_schedule_task` 등). 빈 호스트에서 기본 `pytest`가 red인데 **"정상"이라는 안내가 없어** 호스트가 회귀로 오해. → `@pytest.mark.framework` 마커 또는 별도 경로 + 호스트용 `pytest.ini`/`conftest.py` 템플릿("호스트 기본 수집 = 호스트 테스트만").

### SUP-4. `unmanaged` UX
`unmanaged` 파일은 sync가 **침묵 무시** → 업스트림이 그 파일을 바꿔도 호스트가 모름. → `sync --check`가 unmanaged 분기를 정보성으로 보고 + `sync --reconcile`이 호스트 vs 템플릿 diff 출력(현재 호스트는 수동 헬퍼로 처리).

### SUP-5. 배포 위생 잡건
- `templates/project/scripts/__pycache__/*.pyc`가 패키지에 포함됨(`_is_runtime_artifact`로 sync는 걸러내지만 패키지엔 잔존). 빌드 시 제외 권장.
- `python -m agent_runtime.sync`가 `__main__` 가드 부재로 **무출력 exit 0**(혼동 유발). CLI는 `agent_runtime sync ...`만 유효. → sync.py에 `if __name__=="__main__"` 추가하거나 모듈 직접 실행 차단 안내.
- `agent_runtime update --check`(host_update 경로)가 스테이징 빌드에서 **`invalid command 'bdist_wheel'`** 로 실패 → `sync`로 우회함. 빌드 의존(wheel) 명시 또는 update 경로가 build-isolation 없이도 동작하도록.

---

## 3. 이식 전 과정 타임라인 (발생경위 상세 — 하나부터 열까지)

> "개발팀 스킬뿐 아니라 이식 중 모든 충돌"을 요청받아 시간순으로 전부 기록.

1. **전체 인벤토리 + 공식 설치**: 처음엔 레포를 *선택적으로 스크롤*해 일부만 가져오는 실수 → 사용자 교정("README 읽고 전부 가져와"). 이후 공식 `agent_runtime sync --apply`로 **템플릿 150파일 전량** + `lock --write`(template_files=150). 의존성 보강: `openai`, `PyYAML`(+기존 streamlit/pandas/anthropic/cryptography/Authlib).
2. **루트 규약 도입**: `AGENTS.md`(SoT)·`CLAUDE.md`·`GEMINI.md`·`CURSOR.md`·`AGENT_RUNTIME.md` 정본 채택. 기존에 손으로 만든 AGENTS를 프레임워크 정본으로 **교체**. 리포팅을 BRIEF(Bottom Line→Signal→Insight→Decision)/PLAN/Reversibility Gate로 전환.
3. **`roles.yml` Autofolio 튜닝**: 16역할 레지스트리의 타프로젝트 웹앱 경로 제거 — `Managed database/schema.sql`→`app/database/schema.sql`, `public/app.html`→`app/ui/autofolio_app.py`, `vercel.json`→`requirements.txt`, `scripts/test_e2e.py`→`tests/`, Playwright→Streamlit AppTest. (→ 이 파일이 시임이 됨.)
4. **개발팀 에이전트 이식(16+1)**: 프레임워크 `agents/<role>/SKILL.md` 16종을 개발팀으로, Autofolio 전용 `kis-api-engineer` 추가. Claude Code 노출을 위해 초기엔 `.claude/agents/dev-team/<role>.md`(프론트매터+컨텍스트) 복사본 생성. (SUP-2 불일치가 여기서 발생.) 비엔지니어 9종(ceo/owner/scribe 등)에도 Autofolio 맥락(개발팀≠투자결정) 주입.
5. **자산운용팀(호스트 고유, 프레임워크 무관)**: `.claude/agents/asset-team/`(leadership 4 + korea 4 + us 3 + global 4 = 15) + governance(devils-advocate) + IC 워크플로. — 전부 호스트 추가 파일이라 sync 무관.
6. **운영 bring-up — `check_agent_docs.py`가 fresh install에서 6 ERROR**: 
   - `check_task_registry`(INDEX.md 필요), `check_backlog_fresh`(generated BACKLOG와 일치), `check_status_doc`(STATUS.md 4참조), `check_compound_log`(파일 존재), `check_audit_log`(`## 기록` + 11필드 AUDIT 엔트리), `check_token_budget`(AGENTS.md의 TOKEN-BUDGET.md 참조=**CORE-3a**).
   - 검증기를 정독해 정확한 통과조건을 역설계 → `STATUS.md`/`tasks/INDEX.md`/`compound_log.md`/`AUDIT-LOG.md` seed + `generate_views.py`로 `BACKLOG.md`+VIEW 생성 + `AGENTS.md`에 §14 추가 → **0 error**.
   - 함정: `generate_views.py`는 INDEX.md를 생성하지 않음(BACKLOG/VIEW만) → INDEX는 수동. frontmatter 없는 TASK는 `load_tasks()`가 스킵.
7. **dev 역할 중복 정리**: 프레임워크 정본 `agents/<role>/SKILL.md`와 `.claude/agents/dev-team/<role>.md` 복사본이 이중화 → `check_agent_docs`의 마크다운 링크 경고 **145개**(평면 복사본의 상대링크 깨짐). 정본을 단일 소스로, `kis-api-engineer`는 `agents/kis_api_engineer/SKILL.md`로 승격, 앱 로더가 정본 `agents/`+`.claude/agents`를 읽도록 확장, `.claude/agents/dev-team/` 제거 → 경고 145→107.
8. **`task.schema.json` 부재로 pytest collapse(=CORE-3b)** + **`orchestrator_safety_gate` 부재(=CORE-3c)** 발견. 스키마는 테스트에서 역설계해 동봉(호스트측), pytest 기본 수집을 `tests/`로 스코프(`pytest.ini`)해 프레임워크 self-test 36 fail(SUP-3)과 분리.
9. **시임 분리(분리 운영)**: `sync --check`로 분기 **정확히 2파일**(AGENTS.md, roles.yml) 실측 → `agent_runtime.yml`의 `sync.unmanaged`로 호스트 소유 선언(conflicts 2→0, `--apply` 차단 해소). 통합/링크 문서 `docs/AGENT_RUNTIME_INTEGRATION.md`(계층 모델·분기 원장·업데이트 런북) 신설.

### 그 외 호스트측 잡 충돌(프레임워크 무관, 패턴 참고용)
`st.navigation` URL 충돌(모든 페이지 함수명 `render`→`url_path` 부여) · `use_container_width` deprecated→`width="stretch"` · 앱 페르소나 로더가 `retros/README.md`를 에이전트로 오집계(프론트매터 없는 파일 스킵으로 수정) · PowerShell 작업 디렉터리 드리프트(명시 `Set-Location`) · 샌드박스가 와일드카드 `Remove-Item` 차단(특정 경로 사용) · `Select-Object -First N`이 파이프라인을 잘라 FAILED 줄을 가린 **false-green** 오독.

---

## 4. 결과 (현재 상태)

- `agent_runtime sync --check` → **conflicts=0, updates=0, status=ready**(시임 2파일 unmanaged).
- `python scripts/check_agent_docs.py` → **0 error**(105 warning: 정본 SKILL.md가 아직 없는 운영 산출물 reviews/·reports/·CYCLE 링크 — 첫 사이클에서 소멸).
- `pytest`(호스트 스코프 `tests/`) → **9 passed**. `schemas` 스키마 테스트 → **12 passed**. 프레임워크 `pytest scripts` → **480 passed / 36 failed / 1 error**(SUP-3, 코퍼스 의존).
- 앱 에이전트 로더 → **33 페르소나** 정상(자산 15 + governance 1 + 개발 정본 16 + kis 1).
- 분리 구조: 틀(①, 정본·자동업데이트) / 맥락(②, 호스트추가·sync무관) / 시임(③, unmanaged 2파일). 상세 `docs/AGENT_RUNTIME_INTEGRATION.md`.

---

## 5. agent_runtime 측에 드리는 요청(=자유도)

- 본 문서를 **그쪽 레포에 기록**(이슈/디자인노트)하고, **분석·재설계·구현·이슈분할·검토·반영을 자유롭게 판단**하세요. 호스트는 해법을 강제하지 않습니다.
- CORE 3건이 1차 입력, SUP는 선택. CORE-1/2는 "재구조화 본체", CORE-3은 "지금 고칠 버그".
- 호스트는 추가 재현/로그/패치 검증에 협조 가능(이 레포는 `ycpiglet/autofolio`).

---

## 6. 부록 — 즉시 사용 가능한 산출물

### 6.1 `schemas/task.schema.json` (CORE-3b — `test_validate_task_schema.py` 12개 통과 확인)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://agent-runtime/schemas/task.schema.json",
  "title": "TASK frontmatter",
  "type": "object",
  "required": ["type","id","status","owner","priority","difficulty","est_hours","est_tokens","tags","created","created_at"],
  "properties": {
    "type": {"const": "task"},
    "id": {"type": "string", "pattern": "^TASK-\\d{3,}$"},
    "status": {"type": "string", "enum": ["대기","진행 중","완료","보류","취소"]},
    "owner": {"type": "string"},
    "priority": {"type": "string", "enum": ["Critical","High","Medium","Low"]},
    "difficulty": {"type": "string", "enum": ["상","중","하"]},
    "est_hours": {"type": "number"},
    "est_tokens": {"type": "integer"},
    "tags": {"type": "array", "items": {"type": "string"}},
    "audit_log": {"type": "string"},
    "created": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
    "created_at": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}"}
  },
  "additionalProperties": true
}
```
> 검증기 `validate_task_schema.py`는 frontmatter 텍스트라 `est_hours`(number)·`est_tokens`(integer)를 문자열에서 coerce. `re.search` 패턴이므로 위 앵커(`^...$`)면 `test_bad_id_pattern`/`test_created_at_pattern`도 통과.

### 6.2 `AGENTS.md` §14 추가 예시 (CORE-3a)
```markdown
## 14. Token Budget

세션 토큰 카탈로그·예산 규약은 [agents/lead_engineer/TOKEN-BUDGET.md](agents/lead_engineer/TOKEN-BUDGET.md)를 따른다. 대형 작업 전 예상 비용을 BRIEF/PLAN의 Cost에 기재한다.
```

### 6.3 재현 명령 (clean host 기준)
```bash
agent_runtime sync --apply --root .      # 150 파일
python scripts/check_agent_docs.py       # → check_token_budget ERROR (3a)
pytest -q                                # → collection-error: schemas/task.schema.json (3b), orchestrator_safety_gate (3c)
python -c "import sys; sys.path.insert(0,'scripts'); import agent_orchestrator"  # ModuleNotFoundError: orchestrator_safety_gate (3c)
```

---

## 7. Addendum — 전수 감사 + 전달 결과 (2026-06-09)

### 7.1 근본원인
레포 CI(`tests/`, 94 passed)는 **패키지만** 검증하고 `templates/project/scripts/`(스크립트·검사기·자체 테스트)는 실행하지 않음 → 템플릿 자기 불일치가 무검증 배포. **제안: "clean-host 스모크"(임시 dir에 sync→check→pytest green) CI 게이트.**

### 7.2 누락 로컬 모듈 전수 (template scripts 107개 정적 분석 → 미해결 2종 + 스키마)
- `orchestrator_safety_gate.py` ← `agent_orchestrator.py`·`auto_runner.py`(top-level import → 둘 다 import 불가). 기대 IF: `evaluate_call(owner_role,intent,task_id,inbox)`·`SafetyDecision`·`write_evidence`·`check_emergency_stop`.
- `pipeline.py` ← `agent_worker.py`(함수 내, TASK-111). 기대 IF: `compute_next(meta,reply,changed_files)`·`write_stage_message(stage,inbox)`.
- `schemas/task.schema.json` ← validate_task_schema + test → **PR #2 해결**.

### 7.3 온보딩(pip vs clone) · 훅 · 스킬
- README에 Quick Host Install(pip+sync) **있음**이나 상단 deprecation/scope에 묻혀 처음에 클론·복사부터 함(부분이식 위험) → 교정 후 공식 설치. **제안: README 최상단 "Host? Start here" + `agent_runtime init` 1커맨드.**
- 훅: 스크립트 동봉, `.claude/` gitignore라 `install_hooks.py`로 PC별 등록 — `sync --apply`가 등록까지 안 해 단계가 숨음(init에 포함 권장).
- 스킬: per-role `agents/{role}/SKILL.md` 설계(별도 skills/ 없음=정상). 단 Claude Code 서브에이전트는 `.claude/agents/*.md`+프론트매터 요구 → host 브리지 필요(SUP-2).
- 템플릿에 `requirements.txt`/`pytest.ini`/`tests/` 부재 → host 수동 발견.

### 7.4 전달 결과 (업스트림에 기록 완료)
- **Issue [#1](https://github.com/ycpiglet/agent_runtime/issues/1)** — 본 보고서 본문 + 7장 전수감사 코멘트 (라벨 bug/enhancement/documentation).
- **PR [#2](https://github.com/ycpiglet/agent_runtime/pull/2)** — clean-install green 결함 2건(`schemas/task.schema.json` 동봉 + `AGENTS.md` §13–§14). 레포 패키지테스트 94 passed · 템플릿 스키마테스트 12 passed.
- `orchestrator_safety_gate`·`pipeline`은 의도 로직 불명으로 미작성(이슈 보고만). 결정·반영은 업스트림 자유.
