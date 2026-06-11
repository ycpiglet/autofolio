# Autofolio Component Matrix

## Core Components

| 컴포넌트 | 용도 | 상태 | 디자인 규칙 |
|---|---|---|---|
| 헤더/타이틀 | 화면 식별, 현재 자원 상태 전달 | 기존 사용 유지 | `theme.APP_ICON` + `theme.APP_NAME` |
| KPI 메트릭 (`st.metric`) | 자산, 수익률, 주문 수 등 핵심 수치 | 안정 | 금액은 `fmt_won`, 수익률은 `fmt_pct` 사용 |
| 환경 라벨 | mock/paper/prod/unknown 표시 | 구현 | `theme.env_label()` 단일 소스 사용 |
| 손익 표기 | 수익/손실 색 강조 | 구현 | `pnl_color` 규칙 유지 (KR: +빨강, -파랑) |
| 주문 실행 버튼 | 엔진 수동 실행 | 구현 | 라벨에 현재 환경 라벨 포함 |
| 주문/체결 테이블 | 상태 추적 | 기존 사용 | 열 폭/헤더 고정, 정렬 일관화 |
| 토스트/경고 | 게이트/오류 안내 | 기존 사용 | 경고 우선순위: 위험(빨강) > 주의(노랑) > 알림(파랑) |

## Surface & Layout

- 화면 패턴은 1줄 요약 → 2~3개 핵심 패널 → 작업 패널 → 상세 로그 순.
- 불필요한 장식을 줄이고, 액션과 상태를 한 화면 안에서 확인 가능하게 배치.
- 텍스트 길이를 짧게 유지해 모바일/소형 화면에서 라인 브레이크 최소화.

## Tokens Mapping

| Token Group | 예시 |
|---|---|
| `SEMANTIC_TOKENS["pnl"]` | 손익 컬러 규칙 |
| `SEMANTIC_TOKENS["env"]` | env별 시맨틱 컬러 |
| `SEMANTIC_TOKENS["surface"]` | 페이지/패널/구분선 |
| `theme.env_label()` | 환경 라벨 표시 |

## Acceptance Map

- 환경 라벨은 mock/paper/prod/unknown를 모두 구분한다.
- 손익 컬러는 기존 한국 관습을 유지한다.
- 테마 변경은 동작 코드 변경 없이 helper 수준으로 먼저 반영한다.
