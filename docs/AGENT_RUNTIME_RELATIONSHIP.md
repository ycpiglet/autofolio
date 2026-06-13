# agent_runtime ↔ autofolio 관계 헌장 (Relationship Charter)

> **이 문서는 "두 프로젝트가 서로 어떤 관계인가"의 정본이다.**
> 기술적 sync 절차는 [`AGENT_RUNTIME_INTEGRATION.md`](AGENT_RUNTIME_INTEGRATION.md)(틀/맥락/시임·런북),
> 마찰점 피드백은 [`agent_runtime_feedback.md`](agent_runtime_feedback.md)를 본다.
> 작성: 2026-06-14 · 소유: 호스트(autofolio) · sync 비대상(unmanaged 성격의 호스트 문서)

---

## 0. 한 줄 정의

- **agent_runtime = 재사용 가능한 개발 플랫폼**(= 개발팀의 작업방식·게이트·프로세스). "*어떻게* 만드나".
- **autofolio = 그 위에 짓는 제품**(= 에이전트가 리서치·크롤링→제안→자가분석→투자하는 시스템). "*무엇을* 만드나".
- **같은 Owner가 양쪽을 다 소유한다.** 외부 벤더가 아니라 **사내 플랫폼 ↔ 제품** 관계다. "외주"가 아니라 "한 번 잘 만들어 재사용 + 깨끗한 경계".

쉬운 비유: 회사가 **업무 시스템(전자결재·작업관리 = agent_runtime)** 을 들여와 **본업(투자 시스템 = autofolio)** 을 운영한다. 단, 그 업무 시스템을 만든 것도 같은 Owner다.

---

## 1. 두 조직 모델

[`agents/lead_engineer/STATUS.md`](../agents/lead_engineer/STATUS.md)의 "두 조직"과 동일한 분리다.

| | 무엇 | 어디 |
|---|---|---|
| **개발팀** | agent_runtime 프레임워크(방법론·게이트·릴리스·거버넌스) | `agent_runtime/agents/**`, `scripts/**`(틀) |
| **자산운용팀(제품 두뇌)** | autofolio 고유 IP — 투자 리서치·제안·분석·실행 | `.claude/agents/asset-team/**`, `.claude/agents/governance/**`, `app/**` |

**경계를 밝게**: agent_runtime은 *개발 방법론*을 준다. 하지만 **투자 두뇌(리서치/크롤링→제안→자가분석→투자)는 autofolio 고유 자산이고 agent_runtime이 주지 않는다.** 플랫폼은 비계(scaffolding)와 프로세스를 줄 뿐, product brain은 호스트가 짓는다.

---

## 2. 핵심 원칙 3가지

### ① 수요 기반 (demand-driven) — 단, "사용"과 "확장"을 구분

세 가지 활동을 절대 혼동하지 않는다:

| 활동 | 언제 |
|------|------|
| **agent_runtime으로 autofolio를 개발** | **항상.** 모든 개발은 agent_runtime 프로세스로 한다(위임의 핵심). |
| **agent_runtime 자체를 새로 고치거나 키움** | autofolio가 **실제로 막힐 때만**(상상으로 미리 만들지 않음). 가급적 직접 만들기보다 **업스트림 이슈/피드백**으로. |
| **agent_runtime 업데이트를 autofolio에 들임** | **정식 태그 릴리스**만, 호스트 일정에 맞춰. |

> **욕심이냐 전략이냐를 가르는 한 줄: "이 agent_runtime 작업이 autofolio의 실제 막힘에서 나왔는가?"** 예면 전략, 아니면 욕심.

예외: agent_runtime은 **자체 로드맵**(예: Owner 의사결정용 GUI 대개편)을 독립적으로 진행할 수 있다. 그건 플랫폼의 사업이고, autofolio는 나오면 **베타로 검증**해주는 역할이다. autofolio의 주의를 agent_runtime *기능 상상 개발*로 돌리지 않는다는 뜻이지, agent_runtime이 진화하면 안 된다는 뜻이 아니다.

### ② Owner 층위 참여 (성숙할수록 가벼워짐)

- **Owner가 하는 것**: 방향 설정 · 막힘 보고 받고 결정 · 승인. (CEO/오너 역할)
- **에이전트 자율**: 직접 코딩 · 세부 PM · 구현. (엔지니어 역할)
- **부트스트랩 단서**: "손 안 대도 되는 프로세스"를 가지려면 그게 성숙할 때까지는 손을 대야 한다. 지금이 가장 무거운 시기이고, agent_runtime이 성숙할수록 Owner 부담은 줄어든다.

### ③ 일반/특수 분리 (과적합 방지)

피드백·결정을 항상 두 통으로 나눈다:
- **"어디서나 쓸 것"(general)** → agent_runtime 본체로 (이슈/피드백).
- **"autofolio만의 것"(host-specific)** → 우리 전용 칸(시임/오버레이)으로.

autofolio는 첫 번째 사용처라, agent_runtime이 그 특수 맥락(한국 주식 개인 매매)에 과적합되지 않게 의식적으로 가른다.

---

## 3. 가드레일 (안전장치)

리스크(① 우리 진도가 플랫폼 사정에 묶임 ② 도구 다듬기가 본업을 잡아먹음)를 막는 장치:

1. **우리 전용 칸 (시임/`unmanaged`)** — 호스트 고유 설정(규칙·역할 정의·한글 문서)을 sync가 못 건드리는 칸에 둔다 → 업데이트가 우리 것을 덮어쓰지 않음. (`agent_runtime.yml`의 `sync.unmanaged`.)
2. **정식 출시본만 받기 (태그 릴리스만 sync)** — 공사 중인 미완성본(미태그 main)은 받지 않는다 → 저쪽이 출렁여도 우리는 sync 시점에만, 우리가 고른 때만 느낀다.
3. **본말전도 금지** — agent_runtime은 "투자 시스템을 더 빨리·안전하게 만들기 위한 수단"이지 목적이 아니다.

---

## 4. 비전 / 로드맵

1. **지금**: autofolio = agent_runtime의 첫 고객·설계 파트너·베타테스트. 실제로 굴리며 효과·비용·이슈를 보고 → agent_runtime이 검증받음(실사용 없는 프레임워크는 검증 불가).
2. **다음**: autofolio를 주변 비전공자·일반인에게 배포 → 그들이 겪는 실제 문제를 푸는 툴로 제공 → 사용자 피드백 수집.
3. **추후**: agent_runtime이 다른 프로그램들의 **핵심 개발 플랫폼**으로 재사용. autofolio는 그 일반화의 첫 검증 사례.

이 관계는 **대칭적·상호 보완적**이다: autofolio는 agent_runtime에 실사용 검증을, agent_runtime은 autofolio에 개발 프로세스를 준다.

---

## 5. 현재 알려진 host-fit 갭 (agent_runtime 우선 개선 후보)

호스트가 플랫폼을 깊이 쓰려 할 때 마찰을 내는 지점들(상세는 `agent_runtime_feedback.md`):

- **§7 wheel 패키징 버그**: 점-파일 템플릿(`.gitattributes`·`.githooks`·`.github`·`.codex`)이 wheel에서 제외 → `pip install`+`sync`로 못 받음.
- **§1 host-context read-location 부재**: 호스트가 목적·도메인·안전제약을 *어디에* 두면 프레임워크가 읽는지 규약이 없음.
- **work_cli/스캐폴더 부재**: v1 work-item을 손으로 채워야 해 채택 마찰이 큼.
- **상태 어휘 현지화 부재**: 프레임워크 v1은 영문 enum, 호스트는 한글 상태 → 이중 체계 마찰.

---

## 6. 한 문장 요약

> agent_runtime은 autofolio(그리고 미래 프로그램들)를 더 잘 만들기 위한 **재사용 개발 플랫폼**이다. autofolio를 만들 땐 **항상** 그것을 쓰되, 플랫폼 *자체 확장*은 **실제 막힘에서만**, Owner는 **방향·결정·승인만**, 피드백은 **일반/특수를 갈라** 보고하고, 우리 고유 자산은 **전용 칸**에 두고 **정식 출시본만** 받는다.
