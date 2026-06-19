# 일러스트·캐릭터·아바타·3D (확장 리서치, 2026-06-19)

> 리서치/큐레이션만. **코드·의존성 변경 0.** 적용은 별도 승인 후.
> 사용자 요청의 **시각 요소(이미지·캐릭터) 핵심 문서**. 1차 리서치([asset-curation-matrix.md](./asset-curation-matrix.md))가 다룬 baseline(unDraw·Open Peeps·Humaaans·IRA·DrawKit)을 **넘어서**, 자체호스팅(런타임 CDN 0)·브랜드 `#3182F6` 리컬러 적합성·한국 핀테크 톤 기준으로 확장.
> 라이선스는 각 출처 실제 LICENSE/약관에서 **검증일 2026-06-19** 기준 확인. 불확실 항목 ⚠️. 관련: [개요](./2026-06-19-open-source-visual-assets-expanded.md).

⚠️ **반복되는 공통 함정 2가지**: (1) 대부분의 "무료" 팩 라이선스는 **"애셋을 팩/컬렉션으로 재배포"를 금지**한다 — *내 앱 UI에 렌더링용으로 쓰는 것은 OK, 내려받은 원본을 다시 배포 가능한 묶음으로 공개 리포에 올리는 것은 위반*. **실제 쓰는 SVG만 선별 커밋**하면 안전. (2) unDraw/DrawKit 등 일부는 **AI/ML 학습 금지** 조항 — UI 표시엔 무관하나 애셋을 모델 학습 파이프라인에 넣지 말 것.

---

## 1. 일러스트레이션 (핀테크 테마 + 캐릭터/마스코트)

> 빈/에러/온보딩/성공 상태 + 마스코트. **단일 액센트 `#3182F6` 정밀 리컬러가 최우선이면 기존 unDraw**(사이트 내 브랜드색 픽커·finance 30+종)가 여전히 우위이고, 아래 멀티컬러 세트는 보완재. `핀테크?`=금융 테마 보유, `캐릭터?`=마스코트급 인물/캐릭터.

| 팩 | 스타일 | 라이선스(검증) | 귀속 | 자체호스팅 | 핀테크? | 캐릭터? | 적합 표면 / 노트 | URL |
|---|---|---|---|---|---|---|---|---|
| **unDraw** (baseline) | 평면 단색강조 | 커스텀 오픈(공식 "MIT" 명시 없음) — 상업 OK·무귀속. ⚠️ 팩 재배포·AI학습 금지 | 불필요 | O | O(30+) | △ | **단일필 `#3182F6` 리컬러 챔피언**(사이트 내 색 픽커). 빈 상태 1순위 | [license](https://undraw.co/license) |
| **ManyPixels** 갤러리 | 멀티컬러 플랫(5스타일) | 커스텀(=CC0급, 무귀속·상업OK). ⚠️ 팩 재배포·경쟁서비스 금지 | **불필요** | O (SVG/PNG, 다운로드 전 색 선택) | **O**(Money Transfer·Wallet·Calculator·Report) | O | empty/error/success/교육. 멀티컬러라 단일필 아님(팔레트 조정) | [gallery](https://www.manypixels.co/gallery) · [license](https://www.manypixels.co/license) |
| **Pixeltrue** | 멀티컬러 일러+Lottie | 커스텀(무귀속·상업OK). ⚠️ 원본파일 재배포 금지 | **불필요** | O (SVG/PNG/Lottie JSON) | **O**(무료에 piggy bank·coin·savings 확인) | △ | loading(Lottie)/success/onboarding/empty. **무료 finance 씬+애니 유일** | [free](https://www.pixeltrue.com/free-illustrations) · [license](https://www.pixeltrue.com/license) |
| **Lukasz Adam** | 심플 플랫, 리컬러 친화 | **CC0** (무귀속, 번들·AI학습 전부 허용) | **불필요** | O (Gumroad $0) | △(crypto·e-commerce 강함) | O | onboarding/landing/교육. 법적으로 가장 안전 | [illustrations](https://lukaszadam.com/illustrations) |
| **Open Doodles** | 손그림 캐릭터 | **CC0 1.0** | **불필요** | O | △ | **O**(마스코트급) | **마스코트 1순위(진짜 CC0)**·빈/성공 상태 | [opendoodles.com](https://www.opendoodles.com/) |
| **IRA Design** (Creative Tim) | 그라디언트+아웃라인 캐릭터 36 | **MIT** (GitHub SPDX) | 코드 고지만 | O (SVG/PNG/AI) | △ | **O**(내장 색/그라디언트 빌더) | **마스코트 1순위 대안** — 브랜드 그라디언트 즉시 적용 | [LICENSE](https://github.com/ira-design/ira-illustrations/blob/master/LICENSE.md) |
| **Stubborn** (Craftwork) | 풀바디 캐릭터 컨스트럭터(25+50) | **커스텀 Craftwork(무료)** — CC0 아님, 상업 OK·무귀속. ⚠️ **재배포 금지 + 서드파티 생성기 내장 시 $480 확장** | 불필요 | O (SVG/Figma) | △ | **O** | **마스코트 빌드(내부 사용 한정)** | [license](https://craftwork.design/license) |
| **Delesign Free** | 볼드 멀티컬러 | 커스텀(무귀속·상업OK, 리셀/경쟁만 금지) | **불필요** | O (사이트서 색 커스텀) | ⚠️ 미검증(무료 finance 이름 미확인) | △ | empty/error(테마 확인 후) | [license](https://free-designs.delesign.com/free-designs/free-license/) |
| **Flowbite Illustrations** | Tailwind용 플랫, 다크/라이트 | **MIT** (무귀속, 번들OK) | **불필요** | O (SVG, GitHub) | ⚠️ 미검증(finance 카테고리 미확인) | △ | (Tailwind 스택 정합) empty/error | [github](https://github.com/themesberg/flowbite-illustrations) |
| **SVGRepo (CC0 한정)** | 아이콘/스팟 일러 | **혼합** — CC0/PD는 무귀속; **CC-BY 컬렉션은 귀속 필수(회피)** | 컬렉션별 → **CC0만 필터** | O (SVG) | O(Finance And Payments 147·Money Multicolor 50) | △ | empty 보조/교육 아이콘. **컬렉션별 배지 확인 필수** | [licensing](https://www.svgrepo.com/page/licensing/) |
| **Black Illustrations** | 흑인 인물 플랫 | 커스텀 상업(무귀속, 사칭만 금지). 원본 재배포 금지 | **불필요** | ⚠️ 포맷 미검증 | **O**(Stock Market·Financial Literacy 팩) | O(인물) | 다양성 인물 씬(포맷/리컬러 미검증) | [licensing](https://www.blackillustrations.com/licensing-agreement) |
| **Popsy** | 멀티컬러 플랫 | 커스텀 — **귀속 필수** | ⚠️ **popsy.co 귀속 필수** | SVG(다운로드 가능) | △(rocket/investing) | △ | (귀속 부담) | [illustrations](https://popsy.co/illustrations) |
| **Storyset (Freepik)** | 5스타일, 색편집기 | Freepik — **무료=귀속 필수** | ⚠️ 필수(Flaticon 프리미엄으로만 해제) | SVG/PNG(#3182F6 지정 가능) | **O 매우 풍부**(Investment·Coins·Piggy Bank·Savings) | O | (유료 전환 시) onboarding/empty | [terms](https://storyset.com/terms) |
| **Ouch! (Icons8)** | 다수 스타일(3D/Line) | Icons8 — **무료=링크백 필수** | ⚠️ 필수(유료로 해제) | SVG/PNG | **O ~2,557 finance** | O | (One-tone/Line만 리컬러) | [license](https://icons8.com/license) |
| **Iconscout Free** | 마켓 혼합 | 무료=**귀속 필수** | ⚠️ 필수 | SVG/PNG | O(멀티컬러) | △ | (귀속 부담) | [licenses](https://iconscout.com/licenses) |
| **Blush** | 인물/씬 빌더 | 커스텀(무귀속·상업OK). ⚠️ **브랜드색+편집 SVG는 Pro($12/mo); 무료는 PNG+프리셋만** | 불필요 | △ (무료=PNG) | △ | O | 마스코트 대안(브랜드 리컬러는 사실상 유료) | [license](https://blush.design/license) |

### 제외 / 주의 — 일러스트

- ❌ **Absurd Design (제외)** — 공식 `/freelicense`: **무료 비상업 전용 + 귀속 강제**(블로그 "상업 무료" 주장과 배치, 1차 출처 우선). 페인터리 멀티컬러라 단일 브랜드 리컬러 불가 + AI학습 금지. → 상용 Autofolio 무료 사용 불가. [freelicense](https://absurd.design/freelicense)
- ❌ **DrawKit (제외)** — 무귀속이나 **컴파일/재배포 전면 금지 + AI학습 금지** → 앱 번들 자체가 금지 대상. ("MIT" 주장은 옛 정보, 현행 독점.) [license](https://drawkit.com/license)
- ❌ **Reshot (신규 제외)** — 라이선스는 양호(무귀속)하나 **2026년 1월 Envato 서비스 종료** → 신규 다운로드 불가. 종료 전 받아둔 애셋만 사용 가능.
- ⚠️ **귀속 필수(무귀속 요건상 보류)**: Storyset·Ouch!(Icons8)·Iconscout·Popsy — finance 풍부하나 무료는 귀속/링크백 강제.
- ⚠️ **Stubborn = CC0 아님(정정)** — 커스텀 무료(재배포 금지). 진짜 CC0 풀바디 대안은 **Open Doodles**.
- ⚠️ **Blush 브랜드 리컬러는 사실상 유료(Pro).** 무료·CC0 우선이면 Open Doodles/IRA Design로 대체.
- ⚠️ **미검증(채택 전 갤러리 확인)**: Delesign·Flowbite의 finance 인벤토리, Black Illustrations 포맷/리컬러/가격.

---

## 2. 아바타 (계정 + AI 에이전트)

> 사용자 **계정 아바타**와 앱의 여러 **AI 금융 에이전트 페르소나**(에이전트별 고유 아바타)용. ⚠️ **CDN 0 준수**: `api.dicebear.com`·`boringavatars.com`·`multiavatar.com` 호스티드 URL 금지, 반드시 npm/소스 번들로 인앱 렌더.

DiceBear은 **코어 라이브러리(`@dicebear/core`, `@dicebear/collection`)가 MIT**이고 **그림 에셋은 스타일별로 라이선스가 다르다** — 반드시 스타일 단위 확인.

| 자원 | 유형 | 라이선스(검증; 스타일별) | 귀속 | 자체호스팅 | 적합 표면 | URL |
|---|---|---|---|---|---|---|
| **DiceBear 코어** | 생성 라이브러리(npm) | **MIT** (코드) | 코드 고지 | O (npm) | 인프라(스타일 렌더) | [LICENSE](https://github.com/dicebear/dicebear/blob/main/LICENSE) |
| └ **Notionists / -neutral** | 스타일 | **CC0 1.0** (Zoish) ✅ | 불필요 | O | **계정 1순위**·에이전트 | [styles](https://www.dicebear.com/styles/notionists/) |
| └ **Lorelei / -neutral** | 스타일 | **CC0 1.0** ✅ | 불필요 | O | 계정(친근) | [licenses](https://www.dicebear.com/licenses/) |
| └ **Open Peeps** | 스타일 | **CC0 1.0** (Pablo Stanley) ✅ | 불필요 | O | 계정(손그림) | [licenses](https://www.dicebear.com/licenses/) |
| └ **Thumbs / Initials / Shapes / Rings / Glass / Pixel Art / Identicon** | 스타일 | **CC0 1.0** ✅ | 불필요 | O | 폴백·추상 토큰·에이전트 | [licenses](https://www.dicebear.com/licenses/) |
| └ **Bottts / -neutral** | 스타일 | ⚠️ "Free for personal and commercial use"(Pablo Stanley) — CC0/MIT 아닌 커스텀 무료 | 불필요(권장 표기) | O | **AI 에이전트 1순위**(로봇 메타포) | [styles](https://www.dicebear.com/styles/bottts/) |
| └ **Avataaars** | 스타일 | ⚠️ "Free for personal and commercial use"(Pablo Stanley) | 불필요 | O | 계정(친근) | [styles](https://www.dicebear.com/styles/avataaars/) |
| └ **Adventurer / Personas / Micah / Big Smile / Fun Emoji** | 스타일 | ⚠️ **CC BY 4.0** — **귀속 필수** | **필수** | O | (무귀속 운용이면 회피) | [licenses](https://www.dicebear.com/licenses/) |
| └ **Icons** | 스타일 | ⚠️ **MIT**(Bootstrap Icons 기반) | 고지 | O | UI 아이콘/에이전트 | [licenses](https://www.dicebear.com/licenses/) |
| **Boring Avatars** (`boring-avatars`) | 생성 라이브러리(React) | **MIT** ✅ | 코드 고지 | **O — npm** | **에이전트 식별 토큰**(beam/marble 추상) | [LICENSE](https://github.com/boringdesigners/boring-avatars/blob/master/LICENSE) |
| **Big Heads** (`@bigheads/core`) | 생성 라이브러리(React) | **MIT** ✅ | 코드 고지 | O (npm) | 계정(일러스트 캐릭터) | [LICENSE](https://github.com/RobertBroersma/bigheads/blob/master/LICENSE) |
| **Avataaars** (`avataaars` npm) | 생성 라이브러리(React) | **MIT** (Pablo Stanley·Fang-Pen Lin) ✅ | 코드 고지 | O (npm) | 계정(친근) | [LICENSE](https://github.com/fangpenlin/avataaars/blob/master/LICENSE) |
| **react-nice-avatar** | 생성 라이브러리(React) | **MIT** ✅ | 코드 고지 | O (npm) | 계정(노션풍 커스터마이즈 UX) | [LICENSE](https://github.com/dapi-labs/react-nice-avatar/blob/main/LICENSE) |
| **minidenticons** | 생성 라이브러리(SVG) | **MIT** ✅ | 코드 고지 | O (npm, 초경량) | 결정론적 플레이스홀더(저비용) | [LICENSE](https://github.com/laurentpayot/minidenticons/blob/main/LICENSE) |
| **Multiavatar** (`@multiavatar/multiavatar`) | 생성 라이브러리 | ⚠️ **MULTIAVATAR LICENSE v1.0**(커스텀) — 상업 무료이나 **"유사/경쟁 제품 복제 금지, 디자인 셋 리패키지/리브랜딩 금지"** | 선택 | O (npm) | 계정(개성 캐릭터) — **보조만** | [LICENSE](https://github.com/multiavatar/Multiavatar/blob/main/LICENSE) |

---

## 3. 3D 일러스트·아이콘 (self-host PNG/GLB/SVG)

| 자원 | 유형 | 라이선스(검증) | 귀속 | 자체호스팅 | 적합 표면 | URL |
|---|---|---|---|---|---|---|
| **3dicons.co** | 3D 아이콘(PNG + Blender 소스) | **CC0** ✅ | **불필요** | **O — PNG 번들** | **대시보드/랜딩/빈상태** 액센트(코인·차트·성장) | [3dicons.co](https://3dicons.co/) |
| **Microsoft Fluent Emoji** | 3D 렌더 이모지(PNG) + Color/Flat/HC(SVG) | **MIT** (전 저장소, 3D PNG 포함) ✅ | 코드 고지(NOTICES) | **O — assets PNG 번들** | **친근 금융 이모지** 💰📈📊 (대시보드/온보딩/빈상태) | [LICENSE](https://github.com/microsoft/fluentui-emoji/blob/main/LICENSE) |
| **opensource3dassets.com** (`ToxSam/...`) | 3D 모델 레지스트리(GLB, 991+) | **CC0** ✅ | 불필요 | O (GLB 호스팅) | 3D 씬/특수 액센트(금융 모티프는 제한적) | [github](https://github.com/ToxSam/open-source-3D-assets) |
| **cc0-icons** | 아이콘(SVG, 2D) | **CC0** ✅ | 불필요 | O | UI 아이콘(2D, 보조) | [github](https://github.com/cc0-icons/cc0-icons) |
| **Shapefest** | 3D 추상 도형(PNG 512px 무료) | ⚠️ 커스텀 — 상업 OK·무귀속이나 **"라이브러리/서브라이브러리 재배포 금지", 단독 재배포/판매 금지** | 불필요 | △ — **디자인 요소로만** | 랜딩/마케팅 비주얼(앱 정적 에셋 번들은 경계) | [license](https://www.shapefest.com/license-agreement) |
| ~~Iconscout 3D~~ | 3D 아이콘 | ❌ **제외** — 대부분 유료/재배포 제한 | — | — | — | [iconscout.com](https://iconscout.com/) |

---

## 권장 (Top picks)

**마스코트 / 캐릭터 (온보딩·빈/성공 상태):**
- **1순위 — Open Doodles(진짜 CC0)** 또는 **IRA Design(MIT, 내장 컬러/그라디언트 빌더로 브랜드 블루 즉시)**. 캐릭터 일관성·내부 빌드가 필요하면 **Stubborn(커스텀 무료, 내부 사용 한정)**.
- 빈/성공 상태 보강: **unDraw**(`#3182F6` 색 픽커) + **Lukasz Adam(CC0)** + **ManyPixels** + **Pixeltrue**(무료 finance 씬+Lottie).

**계정 아바타 (사용자):**
- **1순위 — DiceBear `notionists`/`notionists-neutral`(CC0, 무귀속)** + 폴백 **`initials`(CC0)**. `@dicebear/core`+`@dicebear/collection` 자체호스팅(CDN 0), 시드=userId 결정론적. 커스터마이즈 UX가 필요하면 **react-nice-avatar(MIT)**.

**AI 에이전트 페르소나 (계정과 시각 구분):**
- **1순위 — DiceBear `bottts`/`bottts-neutral`**(로봇=AI 메타포 직결, 시드=agentId). ⚠️ 라이선스는 CC0 아닌 Pablo Stanley 커스텀 무료(귀속 강제 없음).
- **무귀속·약관단서 0 최우선** → **Boring Avatars(MIT, npm)** beam/marble 추상 토큰(Toss-blue 팔레트 주입, 인물형 계정과 명확 구분). 또는 CC0 청정 선호 시 DiceBear `shapes`/`rings`(CC0).

**3D 액센트 (대시보드/랜딩/빈상태, 선택):**
- **3dicons.co(CC0) + Microsoft Fluent Emoji 3D(MIT)** 조합. 코인·차트·성장·💰📈 모티프 PNG 번들. Fluent Emoji는 MIT 텍스트만 배포물에 포함하면 화면 귀속 불필요.

## 제외 / 주의 (종합)

- ⚠️ **CC BY 4.0 DiceBear 스타일**(Adventurer·Personas·Micah·Big Smile·Fun Emoji) + Icons(MIT) — 귀속 필수. 무귀속 정책이면 **사용 금지**, CC0 스타일로 한정.
- ⚠️ **Multiavatar** — 상업 무료지만 "경쟁 제품 복제/리브랜딩 금지" → 보조 용도만.
- ⚠️ **Shapefest** — "라이브러리/서브라이브러리 재배포 금지" → 앱 정적 3D 액센트 기본 픽 제외, 마케팅 비주얼 한정.
- ⚠️ **모든 호스티드 URL**(`api.dicebear.com`·`boringavatars.com`·`multiavatar.com`) — **CDN 0 위반, 금지.** npm/소스 번들로 자체호스팅.
- ❌ **Absurd Design(비상업)·DrawKit(번들 금지)·Reshot(서비스 종료)·Iconscout 3D(유료)** — 제외.
- ✅ **공통 안전 운용**: 멀티컬러 일러는 다운로드 전 색 선택 또는 SVG `fill` 편집으로 브랜드 정렬, **실제 사용 SVG/PNG만 선별 커밋**(팩 재배포 조항 회피).
