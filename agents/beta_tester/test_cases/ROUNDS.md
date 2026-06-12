# Beta Tester Rounds

| Round | Cycle | Date | Scope | Result | Evidence |
|-------|-------|------|-------|--------|----------|
| BTR-2026-06-12-001 | CYCLE-001 | 2026-06-12 | Guest login + 8 demo UI views via Streamlit AppTest | Clean, no BTC filed | `pytest tests/unit/test_beta_cycle001_ui_smoke.py` |

## BTR-2026-06-12-001

- 라운드: CYCLE-001
- 수행일: 2026-06-12
- 관점: 처음 접하는 사용자가 게스트 데모로 들어가 주요 화면을 훑어본다.
- 범위: 로그인, 홈, 포트폴리오, 매매/주문, 내역/손익, 분석, 에이전트, 알림, 설정.
- 방식: `KIS_ENV=mock` 기본값과 Streamlit `AppTest`로 demo/mock UI 렌더를 검증했다.
- 결과: 앱 예외 없음. 화면별 기대 텍스트 또는 주요 버튼/섹션 확인. 발견 BTC 없음.
- 제한: 이 환경에서 백그라운드 Streamlit 서버가 유지되지 않아 브라우저 스크린샷 라운드는 수행하지 못했다. 시각적 이슈가 발견되지 않았으므로 BTC 스크린샷은 생성하지 않았다.
