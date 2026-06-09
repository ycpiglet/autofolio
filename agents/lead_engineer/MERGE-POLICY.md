# MERGE-POLICY — 자율 머지 게이트 (호스트 provisional)

> **상태: PROVISIONAL (호스트 작성).** 업스트림 `AGENTS.md §3.5`(자율 머지 거버넌스)가
> 아직 커밋되지 않아(아래 §근거) Autofolio 가 잠정 정본으로 둔다. **업스트림 §3.5 가
> 생기면 그쪽이 우선(전부 반영)이고, 이 문서는 Autofolio 전용 애드덤만 남긴다(§우선순위).**
> 소유: 호스트(오버레이 ②) — `agent_runtime sync` 가 건드리지 않으므로 업스트림과 **병렬
> 진화·자동충돌 없음**. AGENTS.md 에는 §15 포인터만 둔다(본문 §0–§12 pristine 유지).
> 작성: 2026-06-09T19:20+09:00 · 근거 스크립트: `scripts/auto_merge.py`, `scripts/cycle_gate.py`

## 근거 (왜 호스트가 잠정 작성하나)

- 프레임워크 v0.1.5 는 자율 머지/심의 **스크립트**(`auto_merge.py`·`cycle_gate.py`·
  `agent_seminar.py`·`subagent_council.py`·`agent_retro.py`)를 실어 보냈다.
- 그러나 `auto_merge.py` 가 "설계 근거"로 참조하는 **`AGENTS.md §3.5.2`·`§3.5.1`·
  `MEETING-2026-06-01-003`·`EVIDENCE-2026-06-01-003` 은 업스트림 레포 어디에도 커밋되지
  않았다**(2026-06-09 확인: 템플릿 AGENTS.md·main·v0.1.5 모두 §3.5 없음, 레포-루트
  AGENTS.md 404, 트리 209경로에 MEETING/EVIDENCE 0건). 즉 **스크립트는 배포됐는데 그
  근거 거버넌스는 미배포** — `docs/AGENT_RUNTIME_INTEGRATION.md §5` 가 지적한 §14 누락과
  동류의 업스트림 자기-불일치.
- 따라서 그 능력을 Autofolio 에서 *지금* 통제하기 위해, `auto_merge.py` 의 실제 게이트
  로직을 정본화해 이 문서에 둔다(코드가 사실상 스펙).

## 가역성 (AGENTS.md §5 보정)

main 머지는 (배포를 유발하더라도) **instant rollback + revert PR 로 되돌릴 수 있어
R2(act+flag) 이지 R3 가 아니다.** 따라서 아래 게이트가 모두 통과하면 **사람 승인 없이
자율 머지**하고, 비가역(R3) surface 만 Owner 에스컬레이션한다.

## 자율 머지 게이트 (모두 true → AUTO-MERGE, R2)

`scripts/auto_merge.py` 와 동일하다(코드가 정본):

1. PR state=OPEN, mergeStateStatus=CLEAN, mergeable=MERGEABLE
2. 모든 status check = SUCCESS (pending/failing/required-skip 없음)
3. reviewDecision 이 CHANGES_REQUESTED 아님
4. 변경 파일에 **R3 surface(아래)** 없음
5. 비문서(코드) 변경량 ≤ `CODE_LINE_CAP`(현재 600). 문서/운영기록만이면 면제

심의 선행: 실질 변경은 머지 전 **심의(`subagent_council`/`agent_seminar`/`cycle_gate`)
→ 결정** 절차를 거친다(회의/논의/토의 → 결정 → PR → 자율 머지).

## ESCALATE (하나라도 → 사람 결정, R3)

게이트 위반 · CI red · 아래 R3 surface 포함.

### Autofolio R3 surface (호스트 전용 튜닝 — 이 부분만 로컬 소유)

> 업스트림 `auto_merge.py` 기본 R3 패턴은 Vercel/`Managed database/` 중심이라 Autofolio
> 와 다르다. Autofolio 의 고-blast surface 는 다음으로 정의한다(`auto_merge.py` 를 직접
> 수정하지 않는다 — 그건 관리대상 ① 이라 드리프트가 됨; 운영 판단 시 이 표를 적용):

- `.github/workflows/**` — CI(모든 미래 실행에 영향)
- `.env`, 시크릿, **KIS 앱키/계좌(`KIS_*`)**
- `app/brokers/kis/**` 실주문 경로(`place_order`/`cancel_order`), `app/engine/order_flow.py`,
  `app/risk/**` 안전 게이트 — **실거래·안전 직결**
- DB 스키마/마이그레이션(`app/database/schema.sql`, `*migrate*`)
- 자동 실매매 ON 전환·킬스위치 무력화 등 **안전 정책 변경**(MVP_SPEC §10/오류표)

## 하네스 주의 (별개 층)

이 정책은 **프로젝트 거버넌스**다. 실행 환경(Claude Code)의 **안전 분류기**는 별개 층이라,
정책상 자율 머지가 허용돼도 실제 `gh pr merge`(main, 배포 유발)·실주문은 프롬프트/차단될 수
있다. 자동화로 머지하려면 `scripts/auto_merge.py --execute` 를 CI/허용된 러너에서 돌린다.

## 우선순위 — 업스트림 우선 (병렬 진화·충돌 회피)

이 문서는 **호스트 소유(②)** 라 업스트림 sync 와 충돌하지 않고 병렬로 산다. 업스트림이
완성되면 **강제로 업스트림을 정본**으로 채택한다:

**트리거**: 설치된 업스트림 템플릿 `AGENTS.md` 가 §3.5(자율 머지 거버넌스)를 획득.
**감지/강제**: `python scripts/check_merge_policy_precedence.py` — 업스트림 §3.5 발견 시
non-zero 로 "교체 필요"를 알린다(§4 런북·SessionStart 점검에 연결).
**교체 절차(precedence swap)**:
1. **업스트림 §3.5 = 정본(전부 반영)** — verbatim 채택. 위 "가역성/게이트/ESCALATE 공통부"는
   업스트림 소유로 넘긴다.
2. 이 문서는 **Autofolio 애드덤만 잔존(조금 반영)** — `### Autofolio R3 surface` + `## 하네스
   주의` 만 남기고 공통부 프로즈는 삭제, 본문 머리에 "업스트림 §3.5 보완" 명시.
3. `AGENTS.md` 오버레이 **§15 프로즈 제거**, 업스트림 §3.5 + 이 애드덤을 가리키는 한 줄
   포인터로 축소.
4. `docs/AGENT_RUNTIME_INTEGRATION.md §3.1` 의 우선순위 항목을 "반영 완료"로 갱신.

> 요지: **공통부는 업스트림이 100% 가져가고, 로컬은 Autofolio 고유 surface 만 남긴다.**
> 공통부를 공유 본문(AGENTS.md §0–§12)에 박지 않았기 때문에 이 교체는 텍스트 충돌 없이
> "삭제+포인터 교체"로 끝난다.
