# agent_runtime 평가 지표 틀 — autofolio를 workload로 (고정 + 변동)

> **목적**: agent_runtime 버전의 효과를 **객관·정량**으로 측정한다. autofolio의 실제 작업이 벤치마크 workload다.
> 관계 배경은 [`AGENT_RUNTIME_RELATIONSHIP.md`](AGENT_RUNTIME_RELATIONSHIP.md), 플랫폼 측 요청은 agent_runtime#128(self-eval)·#125(footprint)·#121(관계).
> 작성: 2026-06-14 · 소유: 호스트(autofolio)

---

## 0. 원칙

1. **오라클 = 검증된 통과.** "보기 좋았나"가 아니라 "테스트·게이트를 통과했나". 우리 `pytest`·`check_agent_docs`·spec/quality 리뷰가 곧 오라클이다(SWE-bench 원리 — repo 테스트가 ground truth).
2. **고정 + 변동 둘 다.** 고정만 → 버전이 올라갈수록 낡은 기준 적용. 변동만 → 매 버전 과적합·비교 불가. **고정 = 척추(종단 비교), 변동 = 팔다리(그 버전 새 기능 검증).**
3. **객관 우선, 주관 보조.** 수치화 안 되는 "우아함"은 샘플 루브릭 점수로 보조만. 객관인 척하지 않는다.
4. **작은 N 정직.** 모델은 run마다 출렁인다. 분리하려면 다중 실행이 필요하고 비싸다. 우리 규모에선 **"통계적 증명"이 아니라 "방향성 신호"** 수준임을 인정한다.

---

## 1. 고정 지표 (fixed / 버전 무관 · 종단 비교)

버전이 바뀌어도 항상 의미 있는 "작업이 좋고 싼가".

| 지표 | 정의 | 출처 |
|------|------|------|
| `first_pass_rate` | 첫 시도에 모든 게이트(pytest·check_agent_docs·리뷰) 통과한 task 비율 | CI + 리뷰 로그 |
| `rework_count` | task당 재작업(수정 라운드) 횟수 | WORK-SCHEMA measurement |
| `gate_failure_count` | task당 게이트 실패 횟수 | WORK-SCHEMA / CI |
| `reopened_count` | 완료 후 재오픈된 횟수 | WORK-SCHEMA closure |
| `wall_clock_per_task` | task 착수→머지 실시간 | 타임스탬프(`now.py`) |
| `tokens_per_task` | task당 토큰 | 세션/워크플로 usage |
| `merge_conflict_count` | 통합 시 머지 충돌 수 | git |
| `owner_interventions` | task당 오너 개입(결정·교정) 횟수 | 수기 카운트 |

> 이 8개는 **잠그고** 버전마다 동일하게 잰다. 종단 추세선이 "플랫폼이 실제로 나아지나"의 척추다.

## 2. 변동 지표 (variable / 그 버전 새 능력)

버전의 *새 기능*이 실제로 작동하는지. **기능이 바뀌면 이 표도 바뀐다.**

### v0.2.0 — 병렬 wave
| 지표 | 정의 | 출처 |
|------|------|------|
| `wave_parallelism` | wave당 동시 실행 unit 수(평균) | wave_dispatcher |
| `footprint_violation` | 선언 footprint ⊄ 실제 변경(`git diff`)인 unit 수 | 사후 대조(현재 게이트 부재 → #125) |
| `wave_defer_rate` | footprint 겹쳐 다음 wave로 밀린 비율 | wave_dispatcher |
| `pane_utilization` | 생성한 pane 대비 실제 동시 진행 비율 | 수기/세션 |
| `parallel_speedup` | (순차 추정 시간) / (실제 wave 실시간) | 1·§3 baseline 대비 |

> 다음 버전(예: GUI·RSI)이 오면 이 표를 **그 버전 지표로 교체**한다. 고정 §1은 그대로 둔다.

---

## 3. 파일럿 계획 (첫 측정)

- **대상**: TASK-050(일일한도 UTC)·051(compliance fail-open)·052(ack 루프) — **서로 독립·작음** → 병렬 wave 안전 시험에 적격(순차인 UI 페이즈 045~049는 부적격).
- **절차**:
  1. **baseline**: 3개를 *순차*(기존 cascade)로 처리 — §1 고정 지표 기록.
  2. **wave**: 3개를 *병렬 wave*(pane 분리)로 처리 — §1 고정 + §2 변동 기록.
  3. **비교**: `parallel_speedup`, footprint 위반 유무, 오너 컨펌 부담, 첫시도 통과율 차이.
- **산출**: 결과를 agent_runtime#128에 *실사용 데이터*로 코멘트. 방향성 신호로 보고(통계적 증명 아님).

---

## 4. 주의 (안티패턴)

- **Goodhart**: 지표 최적화가 목적이 되면 안 됨(예: 일을 안 쪼개 `rework_count` 낮추기). 지표는 결정·피드백용 신호지 목표가 아니다.
- **평가 연극**: 재는 데 본업보다 더 쓰지 않는다. 가벼운 자동 캡처 우선, 수기는 최소.
- **책임 분담**: *엄밀한* 벤치마크 하네스는 agent_runtime의 몫(#128). autofolio는 **실데이터 공급 + 가벼운 로컬 신호**.
