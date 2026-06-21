# EVIDENCE-2026-06-19-002 Profile confirmation and portfolio KPI polish

## 질문

TASK-091에서 성향 진단 확인 문구와 포트폴리오 탭 표시의 UX 누락을 재발하지 않게 수정했는가?

## 적용 범위

- 성향 진단 확인 문구 입력 UX
- 성향 진단 저장 전 클라이언트 validation
- 포트폴리오 상단 평가손익 KPI
- 포트폴리오 진단 문장 키워드 강조
- 포트폴리오 상단 현금 KPI 우선순위

## 증거

| 항목 | 결과 | 근거 |
|------|------|------|
| 확인 문구 guide | pass | 입력 중에도 `위 항목을 모두 이해했습니다.` 회색 guide overlay 유지 |
| wrong confirmation | pass | E2E에서 wrong phrase 입력 후 POST attempts 0 검증 |
| 평가손익 퍼센트 | pass | demo walkthrough에서 `[data-kpi-id="unrealized"]`에 `+4.56%` 표시 검증 |
| 현금 KPI | pass | demo walkthrough에서 `[data-kpi-id="cash"]` 없음 검증 |
| 진단 키워드 | pass | demo walkthrough에서 `보유 목적`, `손실 허용 범위` strong 렌더링 검증 |

## 검증 명령

```powershell
npm run lint
npm run test:e2e -- e2e/investor-profile.spec.ts --reporter=line
npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line
npm run build
.venv\Scripts\python.exe -m pytest tests/api/test_profile_survey.py -q
.venv\Scripts\python.exe -m pytest tests/api/test_portfolio.py tests/unit/test_portfolio_groups.py -q
```

## 결과

- `npm run lint` -> pass.
- `investor-profile.spec.ts` -> 3 passed.
- `demo-walkthrough.spec.ts` -> 1 passed.
- `npm run build` -> pass.
- profile survey API -> 12 passed, 4 warnings.
- portfolio focused tests -> 22 passed, 1 warning.

## 남은 리스크

- 확인 문구 overlay는 내부 책임 고지 UX이며 공인 전자서명 요건을 충족한다는 의미가 아니다.
- 포트폴리오 현금 정보는 상단 독립 KPI에서만 제거했고, 자산 배분과 총자산 상세에는 유지했다.
