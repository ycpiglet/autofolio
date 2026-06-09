# agent_runtime — 호스트 통합 피드백 (Autofolio 적용 경험)

> agent_runtime **v0.1.5**를 Autofolio(개인 자산운용 OS)에 전체 이식하며 "프레임워크=틀 / 호스트=맥락"으로 **분리 운영**하려다 정리한 마찰점.
> 이 문서는 그대로 agent_runtime 이슈/디자인 노트 본문으로 쓸 수 있게 작성. 작성: 2026-06-09.

---

## TL;DR
다음 버전의 핵심은 **"프레임워크가 호스트의 맥락을 읽어 들이는 고정 규약(read-location)"**(§1)과 **sync의 오버레이 모델**(§2). 그 전에 **clean install이 green이 아닌 결함 3건**(§4)은 즉시 고칠 수 있음.

---

## 1. 가장 큰 빈자리 — 호스트 "맥락 주입" 규약이 없다  ★재구조화 본체
- 프레임워크는 틀만 주고, 호스트가 **목적/비전/도메인/역할매핑/안전제약**을 *어디에* 두면 프레임워크가 읽는지 정의가 없다.
- 결과: 호스트는 (a) 템플릿 파일을 편집(→충돌)하거나 (b) 프레임워크가 모르는 임시 파일에 맥락을 흩뿌린다. 프레임워크가 호스트 의도를 "읽을" 방법이 없음.
- **제안**: 부트스트랩/에이전트 start 시 읽는 **고정 read-location**을 규약화.
  - 예) `host/context.yml`(또는 `CONTEXT.md`) — 스키마: `project_purpose · domain · vision · glossary · roles_overlay(역할→경로/책임) · safety_constraints · stack`.
  - 이 위치는 **항상 unmanaged**(sync 비대상)로 정의 → 업데이트가 절대 건드리지 않음.
  - 프레임워크 측은 이 파일을 읽어 AGENTS/STATUS/에이전트 컨텍스트에 주입(없으면 우아하게 생략). → "다음 버전에서 어디서 정보를 읽는다"가 바로 이것.

## 2. sync가 binary다 — 오버레이/머지 개념 부재
- 파일 상태가 `pristine-managed` / `unmanaged(동결)` / `blocking-conflict` 셋뿐.
- 템플릿 파일을 **한 줄만** 호스트화해도 영구 conflict가 되고, conflict가 하나라도 있으면 `sync --apply`가 **전체 0건 적용 후 중단**(all-or-nothing). → 불가피한 한 줄 때문에 나머지 148파일 업데이트가 막힘.
- **제안(택1 이상)**: (a) `@include`/**managed-region 마커**(마커 밖 호스트 편집은 업데이트에도 생존), (b) 파일별 3-way 머지, (c) "managed base + host override" 레이어. 최소한 (d) `--apply`가 conflict 파일만 건너뛰고 나머지를 적용하는 옵션.

## 3. roles.yml이 단일 managed 파일
- 역할 레지스트리는 본질적으로 **프로젝트별**인데 프레임워크 1파일이라 호스트가 편집→충돌(현재 Autofolio도 이 파일이 시임).
- **제안**: 패키지에 framework 기본 roles 제공 + 호스트 `roles.host.yml`이 **확장/오버라이드**. 역할 정의 업데이트가 충돌 없이 흐르고, 호스트 고유 역할(예: `kis-api-engineer`)이 1급 시민이 됨.

## 4. 프레임워크가 자기 검사기/의존을 만족 못 한 채 배포됨 — clean install이 red  ★즉시 수정 가능
신규 호스트에서 `sync apply → check_agent_docs → pytest`가 바로 green이어야 하는데 아래로 깨짐:
- **`AGENTS.md` §14 누락**: `scripts/check_agent_docs.py::check_token_budget`이 AGENTS.md의 `TOKEN-BUDGET.md`(§14) 참조를 **ERROR로 강제**하는데, 템플릿 `AGENTS.md`엔 §14가 없음 → 호스트가 AGENTS.md를 편집해야만 green(= 강제 시임 발생).
- **`schemas/task.schema.json` 미동봉**: `scripts/validate_task_schema.py`와 `scripts/test_validate_task_schema.py`가 요구하는데 파일이 없어 `pytest` **collection-error**. (테스트에서 역설계해 12개 테스트를 통과하는 스키마를 첨부 가능.)
- **`scripts/orchestrator_safety_gate.py` 미동봉**: `scripts/agent_orchestrator.py`가 `import orchestrator_safety_gate`(`evaluate_call(...)` 호출)하는데 템플릿에 없음 → 오케스트레이터 **import 불가**, `scripts/test_role_mentions.py` collection-error.
- **제안**: 이 3개를 템플릿에 동봉(또는 검사기를 산출물 부재에 관대하게). **"clean install → green"을 CI 게이트**로.

## 5. 자체 테스트 ↔ 호스트 테스트가 안 갈라짐
- `scripts/test_*.py` ~46개 중 **36개**가 agent_runtime **고유 TASK 코퍼스 / 로컬 스케줄 데몬 / 호스트 경로**에 의존 → 빈 호스트에서 기본 `pytest`가 red인데, 그게 "정상"이라는 안내가 없음(호스트가 회귀로 오해).
- **제안**: self-test에 마커(`@pytest.mark.framework`) 또는 별도 경로, 그리고 호스트용 `pytest.ini`/`conftest.py` 템플릿 제공("호스트 기본 수집 = 호스트 테스트만").

## 6. unmanaged UX
- `unmanaged` 파일은 sync가 침묵 무시 → 업스트림이 그 파일을 바꿔도 호스트가 **모름**.
- **제안**: `sync --check`가 unmanaged 분기를 정보성으로 보고, `sync --reconcile`이 호스트 vs 템플릿 diff를 출력(현재는 수동 헬퍼로 처리 중).

---

## 우선순위 제안
1. **즉시(확실·저위험)**: §4의 3개 산출물 동봉 → clean install green + CI 게이트.
2. **핵심 설계(재구조화 본체)**: §1 host-context read-location + §2 sync 오버레이 모델.
3. **부가**: §3 roles 확장, §5 테스트 분리, §6 unmanaged UX.

## 참고: Autofolio가 현재 우회한 방식
- 시임 2파일(`AGENTS.md`, `agents/roles.yml`)을 `agent_runtime.yml`의 `sync.unmanaged`로 호스트 소유 선언.
- 통합/링크 문서 `docs/AGENT_RUNTIME_INTEGRATION.md`(계층 모델·분기 원장·업데이트 런북)로 분리 운영.
- §1이 생기면 이 우회(특히 AGENTS.md 시임)는 대부분 제거 가능.
