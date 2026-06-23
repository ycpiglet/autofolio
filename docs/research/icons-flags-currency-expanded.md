# 아이콘·국기·통화 글리프 (확장 리서치, 2026-06-19)

> 리서치/큐레이션만. **코드·의존성 변경 0.** 적용은 별도 승인 후.
> 1차 리서치([asset-curation-matrix.md](./asset-curation-matrix.md))가 다룬 baseline(Lucide·Phosphor·Tabler·Heroicons·Remix)을 **넘어서**, 자체호스팅(런타임 CDN 0)·Lucide 호환·KR+US+글로벌 멀티마켓(국기·통화기호 1급 자산) 기준으로 확장.
> 라이선스는 실제 GitHub `LICENSE`/공식 라이선스 페이지/npm `license`/Iconify 기계판독 메타(`collections.json`, `info.license.spdx`)에서 **검증일 2026-06-19** 기준 직접 확인. 확인 불가 항목은 **⚠️ 미검증**. 관련: [개요](./2026-06-19-open-source-visual-assets-expanded.md).

**제품 제약 재확인:** ① **셀프호스트 전용 — 런타임 CDN 0.** 인라인 SVG 또는 빌드타임 번들로만 출하, `api.iconify.design` 같은 런타임 아이콘 API 금지. ② 기존 베이스 **Lucide(ISC, 아웃라인, 24px 그리드, 2px stroke)** — 2번째 패밀리는 stroke/weight 불일치 위험이라 호환성 명시. ③ **상용(유료) 제품**이므로 CC-BY(귀속)·CC-BY-SA(카피레프트)·독점은 컴플라이언스 트리아지 대상. ④ KR+US+글로벌 → **국기·통화기호**가 1급 자산.

## 핵심 결론 3줄 (먼저 읽기)

1. **Lucide에는 원화 ₩ 글리프가 없다**(generic `dollar-sign`/`euro`/`japanese-yen`만). KRW 핀테크에서 ₩가 필요하면 → **Tabler `currency-won`(MIT, 아웃라인 2px, Lucide와 동일 작도)** 또는 **MingCute `currency-won`(Apache-2.0, 2px line)**. **Material Symbols에는 `currency_won`이 없다**(Google 4,258개 코드포인트 전수 확인 — 일부 2차 출처의 "있음" 주장은 오류).
2. **국기는 circle-flags(MIT, 원형 600+) + flag-icons(MIT, 사각 4×3/1×1) 조합이 정답.** 둘 다 순수 MIT·무귀속·KR(태극기)/US 커버, `unplugin-icons`로 사용한 코드만 트리셰이킹 번들 → 런타임 CDN 0 충족. **OpenMoji(CC-BY-SA)·Twemoji/EmojiOne(CC-BY)는 국기 용도로 회피.**
3. **모든 브랜드/암호화폐/카드 로고 세트는 코드 라이선스(CC0/MIT)와 무관하게 로고 자체가 상표다.** Simple Icons가 Visa/Mastercard/PayPal을 의도적 제외한 것이 그 증거. 토스·카카오·증권사·거래소·카드사 로고 표시는 **브랜드별 상표 가이드라인 개별 검토**가 출시 전 필수.

## 표 1. 일반 아이콘 세트 (Lucide 보완 후보)

| 세트 | 유형 | 라이선스(검증·SPDX/custom) | 귀속 | 개수/커버리지 | 적합도 | 통합 노트(Lucide 호환·표면) | URL |
|---|---|---|---|---|---|---|---|
| **MingCute** | 아웃라인+필 | **Apache-2.0** ✅ | **불필요** | ~3,300 (line+fill 쌍). 금융 RICH | ★★★★★ **최상** | **24px/2px line → Lucide와 거의 동일**. **`currency-won` ₩ ✅** + candlestick + safe_box(Lucide 결핍 글리프 보완). receipt만 `bill`로 대체. 사이드바·대시보드·테이블 전면 | [github.com/Richard9394/MingCute](https://github.com/Richard9394/MingCute) |
| **Material Symbols** | 가변폰트(아웃라인/필) | **Apache-2.0** ✅ | NOTICE만 | ~2,500 base. 금융 RICH | ★★★★ | FILL 0 / weight~300 / 24dp로 맞추면 Lucide와 정합. candlestick_chart·account_balance·savings·receipt_long 풍부. **단, `currency_won` 없음**. 대시보드·차트 | [github.com/google/material-design-icons](https://github.com/google/material-design-icons) |
| **Iconoir** | 아웃라인 | **MIT** ✅ | 불필요 | ~1,671. 금융 MED-RICH | ★★★★ | **순수 아웃라인 1.5px → stroke=2 시 Lucide와 가장 깨끗하게 정합**. **candlestick-chart ✅**, coins/bank/piggy-bank 있음. ₩·receipt 없음 | [github.com/iconoir-icons/iconoir](https://github.com/iconoir-icons/iconoir) |
| **Hugeicons (free)** | 아웃라인 | **MIT** (free 한정) ✅ | 불필요 | free ~5,400 (Stroke Rounded만). 금융 RICH | ★★★★ | 24px/Rounded → Lucide와 양호(코너 더 둥금). chart/candlestick/coins/bank/wallet/receipt/shield 풍부. **⚠️ Pro(~54k)는 유료·SVG 출하 금지 → `@hugeicons/core-free-icons`로 고정.** ₩ free 여부 ⚠️ 미검증 | [github.com/hugeicons/hugeicons-react](https://github.com/hugeicons/hugeicons-react) |
| **Carbon (IBM)** | 아웃라인 | **Apache-2.0** ✅ | NOTICE만 | ~2,600+. 금융 RICH | ★★★★ | 24px/2px, 특허 그랜트(상용 가점). chart-candlestick·currency-*·wallet·receipt 확인. 터미널이 Lucide보다 각짐 → 래퍼 정규화. **₩ 글리프 ⚠️ 미검증** | [github.com/carbon-design-system/carbon](https://github.com/carbon-design-system/carbon) |
| **Fluent UI System (MS)** | 아웃라인+필 | **MIT** ✅ | 불필요 | unique ~2,000+ (변형 포함 ~18,648). 금융 RICH | ★★★ | regular 24px만 쓰면 양호하나 stroke/코너 반경이 Lucide와 가시적 차이. coin-stack·building-bank·data-trending. ₩·candlestick 없음 | [github.com/microsoft/fluentui-system-icons](https://github.com/microsoft/fluentui-system-icons) |
| **Bootstrap Icons** | 아웃라인+필 | **MIT** ✅ | 불필요 | ~2,000+. 금융 RICH | ★★★ | **16px 그리드**(vs Lucide 24px) → 더 묵직/조밀. graph-up/down·bank·wallet·piggy-bank·currency-dollar/yen/euro/bitcoin. **₩ 없음** | [github.com/twbs/icons](https://github.com/twbs/icons) |
| **Ionicons** | 아웃라인/필/샤프 | **MIT** ✅ | 불필요 | ~1,300 컨셉. 금융 THIN-MED | ★★★ | `-outline` 변형은 stroke 기반 → Lucide와 양호. wallet/receipt/trending 있으나 coin/$/₩/bank 부재 | [github.com/ionic-team/ionicons](https://github.com/ionic-team/ionicons) |
| **TDesign (Tencent)** | 아웃라인+필 | **MIT** ✅ | 불필요 | 금융 MED | ★★★ | 24px 아웃라인, Lucide와 양호. 다국적(중화권) 통화 강점, ₩ ⚠️ 미검증 | [github.com/Tencent/tdesign-icons](https://github.com/Tencent/tdesign-icons) |
| **NAV Aksel (노르웨이 정부)** | 아웃라인+필 | **MIT** ✅ | 불필요 | 957. 금융 RICH | ★★★ | path 기반이나 20–24px에서 Lucide와 무게감 정합. **전용 Money/Statistics 카테고리**(BankNote/Wallet/Piggybank/Receipt/CurrencyExchange/차트). **₩·$ 없음**(Kroner 중심), candlestick 없음. Iconify 미수록 → npm 직접 | [github.com/navikt/aksel](https://github.com/navikt/aksel) |
| **Akar** | 아웃라인 | **MIT** ✅ | 불필요 | ~500. 금융 THIN-MED | ★★ | **24px/2px/라운드캡 → Lucide와 매우 깨끗**. 다만 coin/$/card 정도로 금융 얕음. ₩·candlestick 없음 | [github.com/artcoholic/akar-icons](https://github.com/artcoholic/akar-icons) |
| **Material Icons (구형)** | 고정폰트(5패밀리) | **Apache-2.0** ✅ | NOTICE만 | unique ~2,100×패밀리 | ★★ | Outlined 패밀리만 Lucide와 호환(더 무거움). Symbols로 대체 권장 | `@material-design-icons/svg` |
| **Majesticons** | 아웃라인+솔리드 | **MIT** ✅ | 불필요 | ~720. 금융 MED | ★★ | line 24px/~1.5px, Lucide보다 얇고 부드러움. ₩·candlestick 없음 | [github.com/halfmage/majesticons](https://github.com/halfmage/majesticons) |
| **Feather** | 아웃라인 | **MIT** ✅ | 불필요 | 287. 금융 THIN | ★ | **24px/2px/라운드캡 — Lucide의 원조**. 단 Lucide가 Feather 상위집합이라 추가 실익 거의 없음(휴면) | [github.com/feathericons/feather](https://github.com/feathericons/feather) |
| **Radix Icons** | 아웃라인 | **MIT** ✅ | 불필요 | ~300+. 금융 THIN | ★ | **15×15 그리드**(Lucide보다 조밀), UI 크롬 전용. 금융 소스 아님 | [github.com/radix-ui/icons](https://github.com/radix-ui/icons) |

## 표 2. 프리미엄/심미 세트 — ⚠️ 귀속·독점 주의 (대부분 제외 대상)

| 세트 | 유형 | 라이선스(검증·SPDX/custom) | 귀속 | 커버리지 | 적합도 | 통합 노트 | URL |
|---|---|---|---|---|---|---|---|
| **Solar (480 Design)** | 6스타일 | **⚠️ CC-BY-4.0** (Iconify `solar.json` spdx; repo LICENSE 부재) | **⚠️ 필수** | ~7,400 무료. 금융 RICH | ★★ (귀속 수용 시) | chart/wallet/bill/shield/card/safe 풍부하나 **candlestick·coin·₩ 없음**. **stroke 1.5px → Lucide 2px와 기본 불일치**. **⚠️ npm `solar-icon-set`은 GPL-3.0 — 금지**, `@iconify-json/solar` 사용 | [iconify solar](https://icon-sets.iconify.design/solar/) |
| **Streamline (free)** | line/solid/duotone | **⚠️ CC-BY-4.0 + 커스텀**(가시 클릭 링크 요구) | **⚠️ 필수 + 강함**: 푸터/About에 **"Free icons from Streamline" 클릭 링크** | free ~10–13k. 금융 RICH | ★ | **⚠️ 커스텀 함정**: 아이콘을 "사용자 삽입 가능 자산"(Canva식 빌더)으로 쓰면 안 됨(고정 대시보드는 OK) | [streamline license](https://help.streamlinehq.com/en/articles/5354376-streamline-free-license) |
| **Lets-Icons** | 4스타일 | **⚠️ CC-BY-4.0** (npm spdx) | **⚠️ 필수** | 1,528 무료. 금융 MED | ★ | 내부 패딩 있어 Lucide보다 작게/얇게 렌더. ₩ 부재 추정 | [iconify lets-icons](https://icon-sets.iconify.design/lets-icons/) |
| **Basil (Craftwork)** | 아웃라인+솔리드 | **⚠️ CC-BY-4.0** | **⚠️ 필수**(`react-basil` MIT는 코드만, 아트워크 아님) | 493 무료. 금융 THIN | ✗ | bank/wallet/shield/card·chart-pie만. **coin/₩/$/candlestick/trending/receipt 없음** — 금융 1차 불가 | [iconify basil](https://icon-sets.iconify.design/basil/) |
| **Untitled UI Icons** | 아웃라인(free) | **⚠️ 독점/커스텀**(LICENSE가 재배포 금지; package.json `"MIT"`는 **오기**, LICENSE 우선) | 불필요(무의미) | free 1,100+. 금융 RICH | **✗ 제외** | **stroke 2px/24px/라운드캡 = Lucide와 완벽 매치이나 라이선스가 막음**("판매/재배포/라이브러리 포함 금지"). **원시 SVG 벤더링 불가** → 비대칭 리스크 | [LICENSE](https://github.com/untitleduico/icons/blob/main/LICENSE) |
| **Gravity UI (Yandex)** | ⚠️ 필 중심 | **MIT** ✅ (마케팅의 "attribution required"는 오기, 실제 LICENSE 표준 MIT) | 불필요 | 781 무료 | ✗ (스타일) | **⚠️ fill 기반 + 16px 그리드** → Lucide와 혼용 금지. ₩/coin/wallet/bank 없음 | [github.com/gravity-ui/icons](https://github.com/gravity-ui/icons) |
| **Arcticons** | 모노 라인 앱아이콘 | **⚠️ CC-BY-SA-4.0**(카피레프트) / GPL-3.0(코드) | **⚠️ 필수 + ShareAlike 바이럴** | 14,000+ | ✗ | **ShareAlike 전염성**: 수정 SVG를 CC-BY-SA로 재공개 의무 → 폐쇄 상용 부적합 | [github.com/Arcticons-Team/Arcticons](https://github.com/Arcticons-Team/Arcticons) |
| Pixelarticons | 픽셀아트 | **MIT**(free ~816) / Pro 유료 | 불필요 | 4,159(Pro 포함) | ✗ (스타일) | 비트맵 블록 stroke — Lucide와 정합 불가. 레트로 액센트로만 | [github.com/halfmage/pixelarticons](https://github.com/halfmage/pixelarticons) |

## 표 3. 국기 (KR/US/글로벌 FX·멀티마켓)

| 세트 | 유형 | 라이선스(검증·SPDX) | 귀속 | 개수/커버리지 | 적합도 | 통합 노트 | URL |
|---|---|---|---|---|---|---|---|
| **circle-flags** (HatScripts) | **원형 SVG** | **MIT** ✅ | 불필요 | **634**. KR✅/US✅ + 주·언어·EU | ★★★★★ **FX 1순위** | 현대 핀테크 통화 피커 원형 미감에 최적. ~0.5MB 전체(사용분만 번들 시 수 KB). `@iconify-json/circle-flags`(MIT)+`unplugin-icons`로 런타임 CDN 0 | [github.com/HatScripts/circle-flags](https://github.com/HatScripts/circle-flags) |
| **flag-icons** (lipis) | **사각 4×3 + 1×1** | **MIT** ✅ (코드+SVG 통합 MIT) | 불필요(notice만) | ISO 3166-1 ~250+. KR✅/US✅. 미국 주 없음 | ★★★★★ | 테이블·계좌 행·큰 표시에 사각이 더 읽힘. `.fis`로 1×1 정사각. **`flag-icon-css`는 deprecated → `flag-icons` 사용** | [github.com/lipis/flag-icons](https://github.com/lipis/flag-icons) |
| **flagpack** (Yummygum) | 사각(~4:3) | **MIT** ✅ | 불필요 | 254. KR✅/US✅. 미국 주 없음 | ★★★★ | v2.0 트리셰이킹 per-flag import. **원형/1×1 없음**. React/Vue/Svelte 래퍼 | [github.com/Yummygum/flagpack-core](https://github.com/Yummygum/flagpack-core) |
| **CoreUI Flags (`cif`)** | 사각 | **CC0-1.0** ✅ | 불필요 | 199. KR✅/US✅ | ★★★★ | Iconify 국기 중 **가장 관대(퍼블릭도메인)**. circle-flags와 혼동 주의 | [iconify cif](https://icon-sets.iconify.design/cif/) |
| **country-flag-icons** (catamphetamine) | 사각 3×2 | **MIT** ✅ | 불필요 | ISO 3166-1+예외+일부 subdivision. KR✅/US✅ | ★★★ | **실제 1×1·원형 없음**(README 주석만). React 컴포넌트+string export | [github.com/catamphetamine/country-flag-icons](https://github.com/catamphetamine/country-flag-icons) |
| **region-flags** (google) | 사각(SVG+PNG) | **퍼블릭도메인**(COPYING; 공식 SPDX 아님) | 불필요 | ~270+. **미국 주+캐나다 주/GB 하위지역 포함이 차별점** | ★★★ (보조) | ISO 3166-2 하위지역(미국 주) 필요 시 유일 PD 옵션. **npm/Iconify 없음 → SVG 수동 벤더링**. ⚠️ 일부 국기 저작권 이슈 주석 | [github.com/google/region-flags](https://github.com/google/region-flags) |
| svg-country-flags (hampusborgos) | 사각 | **⚠️ "PD"**(유효 SPDX 아님) | 불필요 | ~250. KR✅/US✅ | ★★ | ⚠️ ~5년 미유지(stale)·LICENSE 파일 없음 | [github.com/hampusborgos/country-flags](https://github.com/hampusborgos/country-flags) |
| **Twemoji flags** (jdecked) | 이모지 아트워크 | **⚠️ 코드 MIT / 그래픽 CC-BY-4.0** | **⚠️ 필수**(그래픽) | RGI 이모지 국기 ~260 | ✗ (FX엔 부적합) | 귀속 라인 수용 시만. 이모지 룩 → 기하 통화 피커엔 부적합 | [github.com/jdecked/twemoji](https://github.com/jdecked/twemoji) |
| **OpenMoji flags** | 이모지 아트워크 | **⛔ CC-BY-SA-4.0** | **⚠️ 필수 + 카피레프트** | 270+ | **✗ 회피** | **함정**: 색/크기 변경(통화 피커 커스텀)하면 "Adapted Material"로 CC-BY-SA 재공개 의무 → 폐쇄 상용 오염 | [github.com/hfg-gmuend/openmoji](https://github.com/hfg-gmuend/openmoji) |

## 표 4. 통화기호 · 암호화폐 · 브랜드/카드 로고

| 세트 | 유형 | 라이선스(검증·SPDX) | 귀속 | 커버리지 | 적합도 | 통합 노트(⚠️ 상표) | URL |
|---|---|---|---|---|---|---|---|
| **Tabler `currency-won` 외** | 통화 아웃라인 | **MIT** ✅ | 불필요 | won✅/dollar/euro/yen/yuan/pound/rupee/bitcoin… `*-off` 변형 | ★★★★★ **₩ 1순위** | **`currency-won` ₩ ✅ — stroke 2px/24px, Lucide와 작도 동일.** `dollar-sign` 옆 무봉제. 표면: FX·통화 피커·잔고 | [tabler currency-won](https://tabler.io/icons/icon/currency-won) |
| **유니코드 텍스트 글리프** | 폰트 문자 | N/A | N/A | ₩ U+20A9, ₿ U+20BF, $ €, ¥, £ | ★★★★★ | **가장 단순**: 앱 폰트(Inter/Noto Sans)가 ₩£€¥$ 커버. ₿(U+20BF)는 Noto Sans Symbols 2 등 확인. 아이콘 배지가 필요할 때만 Tabler 글리프 | — |
| **MingCute `currency-won`** | 통화 아웃라인+필 | **Apache-2.0** ✅ | 불필요 | ₩✅ + 멀티통화 + exchange/refund | ★★★★★ | 표 1과 동일 — ₩ 보유한 두 무귀속 세트 중 하나(2px line, Lucide 정합) | [github.com/Richard9394/MingCute](https://github.com/Richard9394/MingCute) |
| Phosphor `currency-krw` | 통화(필) | **MIT** ✅ | 불필요 | krw✅ + ISO 통화 다수 | ★★★ | ₩ 있으나 **필 지오메트리**(thin/light가 아웃라인 근접). 부분 정합 | [github.com/phosphor-icons](https://github.com/phosphor-icons) |
| **Simple Icons** | 브랜드 로고(모노) | **CC0-1.0** ✅ | 불필요(법적) | ~3,442. visa/mastercard/paypal/coinbase/binance✅. apple-pay/google-pay✅ | ★★★ (전용 칩) | **⚠️ 상표 핵심**: "CC0이나 개별 아이콘이 CC0임을 의미하지 않음… 브랜드 가이드라인 준수는 사용자 책임." **Visa/MC/PayPal을 의도적 제외하는 브랜드 존재 = 상표 제약의 실증.** **24px 솔리드 → Lucide 아웃라인과 불일치**(브랜드 칩 전용) | [github.com/simple-icons/simple-icons](https://github.com/simple-icons/simple-icons) |
| **web3icons** (0xa3k5) | 암호화폐(모노+컬러) | **MIT** ✅ | 필요(notice만) | 2,500+ (token/network/wallet/exchange) | ★★★ (모던) | **2026.02까지 활발**(spothq 대체). `token`(currentColor 모노)/`token-branded`(컬러). **⚠️ 상표 면책 없음 → 자체 "로고는 각 소유자 상표" 고지 유지.** 솔리드 실루엣(Lucide 비정합) | [github.com/0xa3k5/web3icons](https://github.com/0xa3k5/web3icons) |
| cryptocurrency-icons (spothq) | 암호화폐(컬러/모노) | **CC0-1.0** ✅ (단 §4 상표 유보) | 불필요 | ~483 | ★★ (라이선스 최선, stale) | `cryptoicons.co`=이 프로젝트 자체 사이트. **⚠️ 2022년 마지막 — dormant.** 컬러 배지/모노 솔리드. 상표는 토큰별 유보 | [github.com/spothq/cryptocurrency-icons](https://github.com/spothq/cryptocurrency-icons) |
| **aaronfagan/ccicons** | 카드 브랜드 로고 | **Apache-2.0** ✅ | 필요(notice만) | 80×6변형. Visa/MC/Amex/Discover/JCB/UnionPay/Maestro/PayPal/Mir/Alipay… | ★★★ (카드 1순위) | **⚠️ 상표**: Visa·MC·Amex·Apple/Google Pay 강제 브랜드 가이드라인 → **네트워크별 검토 필수.** Apple/Google Pay 없음 → Simple Icons 보충. 컬러/솔리드(결제 UI 전용) | [github.com/aaronfagan/svg-credit-card-payment-icons](https://github.com/aaronfagan/svg-credit-card-payment-icons) |
| Cryptofonts(.com) 계열 | 암호화폐 | **⛔ GPL-3.0** | 필수 | — | **✗ 회피** | 카피레프트(소스 공개) — 폐쇄 상용 트리거 | [github.com/Cryptofonts](https://github.com/Cryptofonts) |
| react-payment-icons(jhkersul) | 카드 React | **⚠️ LICENSE 없음 = All Rights Reserved** | — | — | **✗ 제외** | 2020 아카이브·라이선스 없음 → 출하 불가. aaronfagan SVG 직접 벤더링으로 대체 | — |

## 권장 (Top picks)

**A. Lucide를 보완할 단일 최선 세트 → MingCute (Apache-2.0)**
- 무귀속, **24px/2px line으로 Lucide와 사실상 동일 작도**, 그리고 **Lucide가 결핍한 글리프를 정확히 메움**: `currency-won` ₩(드묾), candlestick(`candle`/`stock`), `safe_box`, 멀티통화, exchange/refund. KRW 핀테크의 단일 보강 세트로 가장 강력. 표면: 사이드바·대시보드·다이얼로그·테이블·FX·에이전트 탭 전면.
- 차순위 무귀속(MIT/Apache): **Iconoir**(stroke=2 시 가장 깨끗 + candlestick, ₩ 없음), **Material Symbols**(FILL 0/weight~300, 금융 RICH, ₩ 없음), **Hugeicons free**(금융 RICH, Pro 금지 주의), **Carbon**(특허 그랜트·엔터프라이즈, ₩ 미검증).

**B. 원화 ₩ 글리프 → Tabler `currency-won` (MIT) [이미 커버된 Tabler 활용]**
- Lucide·Material Symbols 모두 ₩ 없음. Tabler `currency-won`은 **stroke 2px/24px로 Lucide와 동일 컨벤션** → `dollar-sign` 옆 무봉제. 또는 **유니코드 ₩(U+20A9)를 앱 폰트로 렌더**(Inter/Noto Sans 커버)가 가장 단순 — 아이콘 그리드 배지가 필요할 때만 Tabler/MingCute 글리프.

**C. 국기(FX·멀티마켓 1순위) → circle-flags(MIT, 원형) + flag-icons(MIT, 사각) 조합**
- 둘 다 순수 MIT·무귀속·KR(태극기)·US 확실. **원형**은 통화 피커/계좌 행 칩에, **사각 4×3·1×1**은 테이블/큰 표시에. `unplugin-icons` + `@iconify-json/circle-flags`·`@iconify-json/flag`로 **사용 코드만 트리셰이킹 번들 → 런타임 CDN 0**. 미국 주(州) 국기가 후일 필요하면 region-flags(PD, 수동 벤더링) 북마크.

**D. Iconify를 "쓰되 오프라인으로" → unplugin-icons + @iconify/json (빌드타임·트리셰이킹·dev 전용)**
- Iconify 프레임워크(`@iconify/react`·`@iconify/utils`·`@iconify/json`)·`unplugin-icons` 모두 **MIT**. 기본 동작은 `api.iconify.design` 런타임 호출 → **금지**. 대신:
  - **unplugin-icons(권장)**: `node_modules`의 `@iconify-json/*`를 **빌드타임**에 읽어 **import한 아이콘만** 인라인(트리셰이킹) → **런타임 API·CDN 0**. Next.js 16 webpack에 플러그인 1개로 Lucide 베이스 + MingCute/circle-flags/cryptocurrency 혼용. Tailwind는 `currentColor` 인라인 SVG라 `className`으로 색/크기 제어.
- **⚠️ 라이선스 세탁 안 됨**: Iconify 채택해도 **각 세트는 원 라이선스 유지**(`info.license.spdx`로 조회). Solar=CC-BY, Material=Apache… 번들한 세트의 SPDX로 귀속/라이선스 페이지 자동 생성. **금융 UI는 MIT/ISC/CC0 세트(MingCute=Apache, Tabler/circle-flags/flag/Phosphor=MIT, cryptocurrency=CC0) 위주로 가면 귀속 부담 최소.** `@iconify/json`은 ~120MB지만 **devDependency 전용**(런타임 번들 비포함).

## 제외 / 주의 (트레이드마크 · 귀속 · 카피레프트)

- **⚠️ 귀속 필수(CC-BY-4.0) — 가시 크레딧 없이 상용 출하 불가**: **Solar**·**Lets-Icons**·**Basil**·**CoreUI free 아이콘**·**NRK**·**Streamline free**(추가로 **"Free icons from Streamline" 클릭 링크** 강제). *Material Symbols·Carbon·MingCute는 Apache-2.0라 NOTICE만(UI 크레딧 불요 — CC-BY와 구분).*
- **⛔ 카피레프트(폐쇄 상용 부적합)**: **OpenMoji 국기**(CC-BY-SA)·**Arcticons**(CC-BY-SA+GPL)·**Cryptofonts(.com)**(GPL-3.0)·**muffinresearch/payment-icons**(MPL-2.0). npm `solar-icon-set`이 GPL 래퍼인지 확인하고 `@iconify-json/solar`·`@web3icons/*`(MIT)로 대체.
- **✗ 독점/재배포 금지**: **Untitled UI Icons**(LICENSE가 재배포 금지; package.json `"MIT"`는 오기; 원시 SVG 벤더링 불가; 시각은 Lucide와 완벽 매치이나 라이선스가 막음), **Hugeicons Pro·Pixelarticons Pro**(유료·SVG 출하 금지 → free 패키지로 고정), **jhkersul/react-payment-icons**(라이선스 없음=All Rights Reserved).
- **⚠️ 상표(코드 CC0/MIT여도 로고는 각 소유자 상표) — 출시 전 브랜드별 개별 검토 필수**: **Simple Icons**(CC0지만 DISCLAIMER가 책임 부인; 일부 브랜드 의도적 제외), **web3icons**(MIT, 면책 없음 → 자체 고지), **cryptocurrency-icons**(CC0이나 §4 상표 유보), **aaronfagan/ccicons**(Apache-2.0이나 카드 네트워크별 강제 가이드라인). **토스·카카오·증권사·거래소·카드사 로고 표시는 각 브랜드 상표 가이드라인 준수가 컴플라이언스 게이트 항목**이며, 본 저장소의 [판매 전 금융규제 게이트](../../CLAUDE.md)와 함께 출시 전 개별 검토.
- **스타일 비정합(라이선스는 OK지만 Lucide와 혼용 금지)**: Gravity UI·Bootstrap Icons(필/16px), 모든 브랜드·암호화폐·카드 세트(컬러/솔리드 로고) → **전용 칩/패널에 격리**. Pixelarticons는 픽셀아트로 전면 부적합.

> **⚠️ 미검증(채택 전 확인)**: Hugeicons free의 ₩ 글리프 존재, Carbon의 ₩ 글리프, Lets-Icons/Streamline의 ₩, 일부 카드 세트 npm 패키지명.
