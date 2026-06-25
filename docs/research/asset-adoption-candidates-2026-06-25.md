# 금융/뱅킹 에셋·리소스 후보군 레지스트리 (채택 현황) — 2026-06-25

> Owner 제공 후보 목록 × autofolio **현재 채택 상태** 대조. 라이선스 검증은
> [`asset-curation-matrix.md`](./asset-curation-matrix.md)(2026-06-19) 기준. 엄브렐러 태스크:
> TASK-140(UI 비주얼 에셋 확장 채택). 전제: 자체호스팅(런타임 CDN 0), 라이선스 MIT/Apache/ISC/CC0.
> 상태: ✅ 이미 사용 · ◐ 설치/연구됨이나 미적용(갭) · ❌ 불요/제외(사유)

## 아이콘
| 후보 | 라이선스 | 상태 | 비고 |
|---|---|---|---|
| **Lucide** (`lucide-react`) | ISC/MIT | ✅ 사용 | 단일 채택. PortfolioDashboard·dialog 등 + 자체 `ui/icons/`(Candlestick·CurrencyWon) |
| Tabler / Phosphor / Heroicons | MIT | ❌ 불요 | 2번째 패밀리=stroke 불일치. Tabler `currency-won`은 ₩ 보완 옵션만 |
| Iconify | (통합) | ❌ 불요 | 자체호스팅이라 런타임 CDN 통합 불필요 |
| Flaticon / Icons8 | 무료=귀속/유료 | ❌ 제외 | 귀속 의무·상용 무귀속 유료 |
| **(갭) 사이드바 이모지** | — | ◐ **①채택** | `SidebarNav.tsx` 🏠📊💱… → Lucide 단일화 (이미 설치, 의존성 0 추가) |

## 차트 / 데이터 시각화
| 후보 | 라이선스 | 상태 | 비고 |
|---|---|---|---|
| **Lightweight Charts** | Apache-2.0 | ✅ 사용 | 캔들/시계열 (TradingView) |
| **Recharts** | MIT | ✅ 사용 | 대시보드 선언형 |
| **KLineChart · uPlot · @fnando/sparkline** | Apache/MIT | ✅ 사용 | #98에서 추가(캔들 엔진·경량 라인·스파크라인) — 목록보다 풍부 |
| ECharts / D3 / TradingView Charting Library | Apache/ISC/혼합 | ❌ 불요 | 위 스택으로 커버. ECharts=중복, TV Charting Lib=신청·무게 과다 |

## UI 컴포넌트 / 디자인 시스템
| 후보 | 라이선스 | 상태 | 비고 |
|---|---|---|---|
| **shadcn/ui** | MIT | ✅ 사용 | 복붙형(소유권 본인 코드) |
| **Base UI** (`@base-ui/react`) | MIT | ✅ 사용 | 프리미티브(Radix 대신 채택) |
| MUI / Ant Design | MIT | ❌ 불요 | aesthetic·무게 상이 |
| Tremor | Apache-2.0 | ❌ 불요 | shadcn+recharts+KpiCard로 KPI/대시보드 커버 |

## 일러스트레이션
| 후보 | 라이선스 | 상태 | 비고 |
|---|---|---|---|
| **DiceBear**(아바타/캐릭터) | 코어 MIT, CC0 스타일 | ✅ 사용 | 계정·AI 에이전트 아바타(CC0 스타일 한정) |
| **unDraw**(빈/에러) | 커스텀(귀속 불요) | ◐ **②채택** | 현재 일러스트 없음 → 빈/에러 상태에 `#3182F6` 리컬러. **준수**: 필요 SVG만 자체호스팅(핫링크·팩 재배포·AI학습 금지) |
| Open Peeps / Humaaans | CC0 | ◐ 후보(보조) | 온보딩 캐릭터(선택) |
| Storyset / Icons8(일러스트) | 무료=귀속 | ❌ 제외 | 귀속/링크백 강제 |

## 데이터/API (실제 금융 데이터)
| 후보 | 상태 | 비고 |
|---|---|---|
| **KIS(한국투자증권) API** | ✅ 주 데이터원 | KR 시장 — autofolio 브로커/시세/주문 |
| Alpha Vantage / Finnhub / Twelve Data / yfinance | ➖ N/A(보류) | US/글로벌용. 글로벌·미국 자산 확장 또는 프로토타입 폴백 때만 검토 |

## 결론 / 액션
- **신규 도입 거의 없음** — 목록 대부분이 이미 설치·사용 또는 이미 연구(asset-curation-matrix)됨.
- **실행 액션 2건**(TASK-140 범위, 본 PR에서 진행):
  1. **사이드바 이모지 → Lucide** (의존성 0, stroke 일관성). 매핑: 홈`Home`·포트폴리오`PieChart`·매매`ArrowLeftRight`·내역`ReceiptText`·분석`Search`·에이전트`Bot`·알림`Bell`·성향진단`Compass`·설정`Settings`·매뉴얼`BookOpen`. (분석은 기존 🔍에 부합하는 `Search` 채택 — `TrendingUp`은 차트 테마와 중복.)
  2. **unDraw 빈/에러 일러스트**(브랜드 리컬러, `web/public/illustrations/` 자체호스팅) → EmptyState·에러 패널 연결.
- 보류 후보(향후): Open Peeps/Humaaans(온보딩), 글로벌 데이터 API(자산 확장 시).
