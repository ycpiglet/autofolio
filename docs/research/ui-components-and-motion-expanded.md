# UI 컴포넌트·디자인시스템 + 애니메이션/모션 (확장 리서치, 2026-06-19)

> 리서치/큐레이션만. **코드·의존성 변경 0.** 적용은 별도 승인 후.
> Autofolio 스택: **Next.js 16 + React + Tailwind**, 런타임 CDN 0(자체호스팅), 차트=**Recharts**, 브랜드 Toss-blue `#3182F6` + Pretendard. 기존 Tailwind 셋업과 충돌하는 "제2의 디자인시스템" 통째 도입은 비권장.
> 라이선스는 실제 LICENSE/가격 페이지에서 **검증일 2026-06-19** 확인. 불확실 항목 ⚠️. 관련: [개요](./2026-06-19-open-source-visual-assets-expanded.md).

---

## A. UI 컴포넌트·디자인시스템·대시보드 템플릿 (확장)

### 핵심 결론 (먼저 읽기)

- **Tremor + shadcn/ui 조합이 정답에 가장 가깝다.** 둘 다 **Tailwind + Radix 위에서 동작**하고, **차트가 Recharts 기반**이라 기존 Autofolio 차트와 자연스럽게 합쳐진다. 새 디자인시스템을 들이는 게 아니라 **현재 Tailwind 셋업을 확장**.
- **중요 변화(2026-06-19 확인):** **Tremor Blocks & Templates가 이제 전부 무료·오픈소스**(과거 유료 → "free and open-source"). KPI 카드·차트·테이블·페이지 셸 등 **금융 대시보드 블록 300+**를 무상 카피페이스트 → Tremor 가성비 크게 상승. (Vercel이 Tremor 인수 → 유지보수 안정.)
- 접근성 프리미티브가 필요하면 **Radix UI**(shadcn/Tremor의 토대)가 사실상 표준.
- **유료(제외 후보):** Tailwind Plus(구 Tailwind UI), Cruip, CoreUI PRO, Creative Tim PRO, 각 카피페이스트 라이브러리의 "Pro 블록"(Magic UI Pro, Aceternity All-Access, Cult Pro 등). **무료 코어만** 사용.

### 비교표

| 라이브러리/템플릿 | 유형 | 라이선스(검증) | 배포모델 | 자체호스팅 | 적합도 | 통합 노트 | URL |
|---|---|---|---|---|---|---|---|
| **shadcn/ui** | components (copy-paste) | **MIT** ✅ | **copy-paste**(CLI 코드 주입) | 완전(CDN 0) | ★★★★★ | Radix + Tailwind 기반, 차트=**Recharts**. 데이터테이블·다이얼로그/시트·폼·탭·**command palette**·toast·dashboard 블록. "코드 소유" 원칙 100% 부합 | [docs](https://ui.shadcn.com/docs) |
| **shadcn/ui Blocks** | template/blocks | **MIT** ✅ ("Free forever") | copy-paste (`npx shadcn add dashboard-01`) | 완전 | ★★★★★ | 사이드바+차트+데이터테이블 묶인 **dashboard-01**, login/sidebar 즉시 사용 | [blocks](https://ui.shadcn.com/blocks) |
| **Tremor** | components | **Apache-2.0** ✅ (서브컴포넌트 Radix/shadcn MIT 혼합) | npm + copy-paste | 완전 | ★★★★★ | **금융 대시보드 특화**. React+Tailwind+Radix, 차트=**Recharts**. KPI/stat 카드·테이블·spark/도넛/area·DataBar. **Vercel 인수** | [tremor.so](https://tremor.so) |
| **Tremor Blocks & Templates** | template/blocks | **무료·오픈소스** ✅ (과거 유료→현재 free) | copy-paste | 완전 | ★★★★★ | KPI 카드·차트·페이지네이션 테이블·페이지 셸·다이얼로그 **300+ 블록**, 라이트/다크 기본 | [blocks.tremor.so](https://blocks.tremor.so) |
| **Radix UI (Primitives)** | primitives (headless) | **MIT** ✅ (WorkOS) | npm | 완전 | ★★★★★ | 무스타일 접근성 프리미티브. shadcn·Tremor의 토대라 **이미 간접 사용 중**. 직접 추가도 안전 | [github](https://github.com/radix-ui/primitives) |
| **Headless UI** | primitives (headless) | **MIT** ✅ (Tailwind Labs) | npm | 완전 | ★★★★☆ | Radix와 역할 중복 → **둘 중 하나면 충분**(shadcn 쓰면 Radix 기본) | [github](https://github.com/tailwindlabs/headlessui) |
| **Origin UI** | components (copy-paste) | **MIT** ✅ (컴포넌트부) ⚠️ 저장소 루트는 AGPL-3.0(툴링용) | copy-paste | 완전 | ★★★★☆ | shadcn/Tailwind 확장. **AGPL 혼입 주의** → 컴포넌트 디렉터리(MIT)만 복사, 루트 코드 복사 금지 | [github](https://github.com/origin-space/originui) |
| **Kibo UI** | components (copy-paste) | **MIT** ✅ | copy-paste (`npx kibo-ui add`) | 완전 | ★★★★☆ | shadcn 레지스트리 확장. 복잡 컴포넌트(테이블/Kanban/Gantt/Dropzone). 거래 테이블·로드맵 뷰 유용 | [kibo-ui.com](https://www.kibo-ui.com) |
| **Motion Primitives** | components (copy-paste) | **MIT** ✅ | copy-paste | 완전 | ★★★☆☆ | React+Tailwind+Motion 애니메이션. KPI 카운트업·전환 등 폴리시용. 필수 아님 | [github](https://github.com/ibelick/motion-primitives) |
| **Mantine** | components (full DS) | **MIT** ✅ | npm | 완전 | ★★★☆☆ | 완성형 React DS(차트·DataTable·폼 훅 강력). 단 **자체 CSS-in-JS → Tailwind와 제2 DS 충돌** 우려 | [mantine.dev](https://mantine.dev) |
| **Chakra UI** | components (full DS) | **MIT** ✅ | npm | 완전 | ★★☆☆☆ | 접근성 좋으나 자체 스타일 엔진 → Tailwind 중복. Radix/shadcn이 더 정합 | [github](https://github.com/chakra-ui/chakra-ui) |
| **MUI (Material UI) 코어** | components (full DS) | **MIT** ✅ | npm | 완전 | ★★☆☆☆ | 코어 무료지만 Material 언어가 Toss 톤과 이질. **MUI X Pro 유료**(아래). Tailwind 스택엔 비권장 | [github](https://github.com/mui/material-ui) |
| **HeroUI (구 NextUI)** | components (full DS) | **MIT 또는 Apache-2.0** ⚠️ (README=MIT, 사이드바=Apache, 둘 다 허용형) | npm | 완전 | ★★★☆☆ | React Aria + Tailwind v4 모던 DS. 디자인 언어 중복. 라이선스 표기 정합성 확인 권장 | [github](https://github.com/heroui-inc/heroui) |
| **Ant Design** | components (full DS) | **MIT** ✅ | npm | 완전 | ★★☆☆☆ | 엔터프라이즈 폼/테이블 풍부하나 디자인 언어 강해 Toss·Tailwind와 충돌 | [github](https://github.com/ant-design/ant-design) |
| **Flowbite React** | components | **MIT** ✅ | npm | 완전 | ★★★☆☆ | Tailwind 네이티브. Pro 템플릿은 유료지만 **코어 무료**. 보조 후보 | [github](https://github.com/themesberg/flowbite-react) |
| **DaisyUI** | components (Tailwind plugin) | **MIT** ✅ | npm (플러그인) | 완전 | ★★★☆☆ | 순수 Tailwind 플러그인(클래스 기반). 가볍지만 **접근성 동작 직접 구현** 필요 → Radix 대체 불가 | [github](https://github.com/saadeghi/daisyui) |
| **Park UI** | components (copy-paste) | **MIT** ✅ | copy-paste | 완전 | ★★★☆☆ | Ark UI 기반, Tailwind/Panda 선택. shadcn 택하면 중복 | [github](https://github.com/cschroeter/park-ui) |
| **Cult UI** | components (copy-paste) | **MIT** ✅ (코어) | copy-paste | 완전 | ★★★☆☆ | shadcn+Radix+Motion 애니메이션 78+. **Cult Pro 유료**. 무료 코어만 보조 | [cult-ui.com](https://www.cult-ui.com) |
| **Magic UI** | components (copy-paste) | **MIT** ✅ (코어) | copy-paste | 완전 | ★★★☆☆ | shadcn 동반 애니메이션 150+. **Magic UI Pro 유료**. 무료 코어만 폴리시 | [magicui.design](https://magicui.design) |
| **Aceternity UI** | components (copy-paste) | 무료 코어 + **유료 All-Access** ⚠️ (무료부 라이선스 명시 약함) | copy-paste | 완전 | ★★☆☆☆ | 화려한 모션 200+. 마케팅/랜딩 지향, 대시보드 본문엔 과함. 무료부 개별 확인 | [ui.aceternity.com](https://ui.aceternity.com) |
| **Tabler** | template (admin) | **MIT** ✅ | npm/소스 | 완전 | ★★★☆☆ | 완전 무료 admin. 단 **Bootstrap 기반** → Tailwind와 이질적. 레퍼런스용 | [github](https://github.com/tabler/tabler) |
| **Refine** | framework (admin/CRUD) | **MIT** ✅ | npm | 완전 | ★★★☆☆ | React admin/CRUD headless 메타프레임워크. Autofolio는 이미 Next.js 자체 구축이라 **부분 도입은 과함** | [github](https://github.com/refinedev/refine) |
| **CoreUI (무료 React)** | template (admin) | **MIT** ✅ | npm/소스 | 완전 | ★★☆☆☆ | 무료부 MIT이나 **Bootstrap 기반**. **PRO 유료**(아래) | [github](https://github.com/coreui/coreui-free-react-admin-template) |

### 권장 (Top picks) — 금융 대시보드용

1. **shadcn/ui (코어) + shadcn Blocks** — 1순위. **MIT·copy-paste·런타임 CDN 0**으로 "코드 소유" 원칙과 완전 합치. Radix 접근성 + Recharts 차트 기본. KPI 카드·**데이터테이블**·다이얼로그/시트·survey 폼·탭·**command palette**·toast가 한 생태계. `npx shadcn add dashboard-01`로 사이드바+차트+테이블 셸 즉시.
2. **Tremor (npm 코어) + Tremor Blocks(무료)** — 2순위이자 **금융 대시보드 전용 보강재**. Apache-2.0, Recharts 기반이라 기존 차트와 동일 토대. KPI/stat·spark·DataBar·페이지네이션 테이블 즉시. Blocks 무료화로 비용 0.
   - **shadcn과 공존 전략:** 차트·KPI·금융 위젯은 Tremor, 일반 UI(다이얼로그/폼/command palette)는 shadcn — 둘 다 Tailwind+Radix라 토큰만 `#3182F6`로 통일하면 한 화면에서 일관. 단 **동일 역할(버튼 등) 컴포넌트는 소스를 한쪽으로 고정**해 중복 방지.
3. **Radix UI** — 접근성 프리미티브 표준. shadcn/Tremor가 이미 의존 → **토대 확정**. 커스텀 인터랙션(거래 확인 시트 등) 직접 구축 시 사용.
4. **(선택) Kibo UI / Origin UI** — **고급 데이터테이블·Kanban·복잡 입력** 필요 시만 핀셋 추가. 둘 다 copy-paste·MIT. **Origin UI는 컴포넌트 디렉터리(MIT)만** 복사(루트 AGPL 금지).
5. **(선택) Magic UI / Motion Primitives 무료 코어** — KPI 숫자 카운트업 등 마이크로 모션 폴리시용.

> **비권장(스택 충돌):** Mantine·Chakra·MUI·Ant Design·HeroUI는 모두 MIT라 "쓸 수는" 있으나 자체 스타일 엔진/디자인 언어가 **기존 Tailwind 셋업과 싸우는 제2의 디자인시스템**. 신규 admin 백지 시작이 아니면 채택하지 말 것. Tabler·CoreUI 무료는 **Bootstrap 기반**이라 Tailwind와 이질적 → 레퍼런스용.

### 제외 (유료 / 클로즈드) — EXCLUDE

- **Tailwind Plus (구 Tailwind UI)** — 유료(개인 $299/팀 $979 평생). 상용 가능하나 **새 UI 키트로 재배포 금지**. 무료 대안 충분 → 제외. [tailwindcss.com/plus](https://tailwindcss.com/plus)
- **MUI X Pro / Premium** — 유료(코어 MUI는 MIT지만 X Pro는 상용). Recharts/Tremor로 대체. [mui.com/pricing](https://mui.com/pricing)
- **CoreUI PRO** — 유료($127/dev·년~). Bootstrap 기반 이중 비정합. [coreui.io/pricing](https://coreui.io/pricing)
- **Creative Tim Material Dashboard PRO** — 유료(무료부 MIT). MUI/Material 언어가 Toss 톤과 이질. [creative-tim.com](https://www.creative-tim.com/product/material-dashboard-react)
- **Cruip 유료 템플릿** — 유료($49–$129). 무료 일부 있으나 핵심은 상용. [cruip.com](https://cruip.com)
- **각 카피페이스트 라이브러리의 Pro 블록** — Magic UI Pro / Aceternity All-Access / Cult Pro 등 유료(주로 랜딩). **무료 코어만** 사용.

> 검증 메모: ⚠️ **HeroUI** README(MIT) vs 사이드바(Apache) 표기 불일치(둘 다 허용형). ⚠️ **Origin UI** 루트 AGPL-3.0(컴포넌트 디렉터리만 MIT). ⚠️ **Aceternity 무료부** 라이선스 문구 약함 → 개별 확인.

---

## B. 애니메이션·Lottie·로더 (확장)

> **핵심 원칙: "런타임 라이브러리(코드)"의 라이선스와 "애니메이션 에셋(JSON/.riv/아이콘)"의 라이선스는 별개다.** lottie-web·Rive 런타임이 MIT라고 해서 거기서 받은 개별 애니메이션이 무료인 것은 아니다 — **에셋은 마켓플레이스별·파일별로 따로 검증**. 핀테크 톤엔 절제(짧게·드물게).

| 자원 | 유형(runtime/asset/loader) | 라이선스(검증) | 귀속 | 자체호스팅 | 적합 표면 | 주의 | URL |
|---|---|---|---|---|---|---|---|
| **lottie-web** | runtime | **MIT** ✅ | 고지만 | ✅ JSON 번들 | Lottie 재생 전반 | 무겁다(~250KB) | [LICENSE](https://github.com/airbnb/lottie-web/blob/master/LICENSE.md) |
| **lottie-react** | runtime | **MIT** ✅ | 고지만 | ✅ | React Lottie 재생(가장 단순) | lottie-web 무게 상속 | [npm](https://registry.npmjs.org/lottie-react) |
| **@lottiefiles/dotlottie-react** | runtime | **MIT** ✅ | 고지만 | ✅ `.lottie` 번들 | 압축 멀티 애니메이션 | LottieFiles 차세대 플레이어(JS 런타임=MIT) | [LICENSE](https://github.com/LottieFiles/dotlottie-web/blob/main/LICENSE) |
| **@rive-app/react-canvas** | runtime | **MIT** ✅ | 고지만 | ✅ `.riv` 번들 | 인터랙티브 상태머신 애니메이션(경량) | 런타임만 MIT. `.riv` 파일은 별도(아래) | [LICENSE](https://github.com/rive-app/rive-react/blob/main/LICENSE) |
| **LottieFiles 플랫폼** | **asset** | **per-asset 혼합** ⚠️ | **파일마다 다름** | ✅ JSON 다운로드 | success/coins/growth/loading 소스 | ⚠️ **파일별 라이선스 확인 필수.** Simple License는 **파생물 share-alike** + "경쟁 서비스용 수집 금지" | [license](https://lottiefiles.com/page/license) |
| **Rive Community** | **asset** | **CC BY 4.0(전체 균일)** ⚠️ | **필수(제작자 크레딧)** | ✅ `.riv` 다운로드 | 인터랙티브 success/loader/empty | ⚠️ 상용 OK·share-alike 아님. 단 **모든** 커뮤니티 파일에 CC BY 4.0 균일 적용 → 출처표기 의무 | [ToS](https://rive.app/docs/legal/terms-of-service) |
| **Lordicon** | **asset** | **Free=비상용+출처표기 / PRO=유료** ❌ | Free: 필수 | ✅(PRO) | 로딩/토글/알림 마이크로 아이콘 | ❌ **Free는 상용 불가.** 상용은 PRO 구독 필수 | [licenses](https://lordicon.com/licenses) |
| **useAnimations** | runtime+**asset** | 코드 **MIT** / 아이콘 **CC BY 4.0 + 재배포금지** ⚠️ | 아이콘: 필수 | 기술적 ✅ / 라이선스 △ | loading·토글 마이크로 인터랙션 | ⚠️ "MIT라 무료"가 아님. 유료 SaaS면 컴플라이언스 검토. 대안 react-spinners/SVG-Loaders | [github](https://github.com/useAnimations/react-useanimations) |
| **canvas-confetti** | runtime | **ISC** ✅ | 고지만 | ✅ | **체결 성공/축하** 컨페티 | 절제(짧게·드물게) | [npm](https://registry.npmjs.org/canvas-confetti) |
| **@number-flow/react** | runtime | **MIT** ✅ | 고지만 | ✅ | **PnL/대표 KPI 숫자 카운트업**(자릿수 롤) | `"use client"` 경계. SSR/CSP nonce 지원 | [github](https://github.com/barvian/number-flow) |
| **react-countup** | runtime | **MIT** ✅ | 고지만 | ✅ | 보조 KPI·합계 단순 카운트업 | countup.js 래퍼(자릿수 롤 없음) | [github](https://github.com/glennreyes/react-countup) |
| **countup.js** | runtime | **MIT** ✅ | 고지만 | ✅ (0 deps) | 프레임워크 비의존 카운트업 코어 | React는 보통 react-countup 경유 | [github](https://github.com/inorganik/countUp.js) |
| **Motion / Framer Motion** | runtime | **MIT** ✅ | 고지만 | ✅ | 차트 진입·카드/리스트·페이지 전환 | 강력하나 번들 큼. 단순 전환엔 과할 수 있음 | [npm](https://registry.npmjs.org/motion) |
| **@formkit/auto-animate** | runtime | **MIT** ✅ | 고지만 | ✅ (~1.7KB, 0 deps) | 리스트 add/remove/reorder·**빈 상태 전환**·필터 토글 | `useAutoAnimate()` 훅. 로더 아님 | [github](https://github.com/formkit/auto-animate) |
| **react-loading-skeleton** | loader/skeleton | **MIT** ✅ | 고지만 | ✅ | **카드/리스트/테이블 스켈레톤** 정석 | `<SkeletonTheme>`로 다크/라이트 | [github](https://github.com/dvtng/react-loading-skeleton) |
| **react-spinners** | loader/spinner | **MIT** ✅ | 고지만 | ✅ | 버튼 인라인 스피너·소형 로딩 | named import 트리셰이킹 | [github](https://github.com/davidhu2000/react-spinners) |
| **SVG-Loaders** (Sam Herbert) | loader (SVG) | **MIT** ✅ | 고지만 | ✅ SVG 번들 | 손맛 SVG 스피너·빈 상태 | `fill=currentColor`로 테마 대응 | [github](https://github.com/SamHerbert/SVG-Loaders) |
| **CSS Loaders (Temani Afif)** css-loaders.com | loader (CSS) | **미명시 = 미검증** ⚠️ | 불명 | ✅ 기술적 | 순수 CSS 스피너(0 deps) | ⚠️ 사이트·GitHub 어디에도 라이선스 없음(검색의 "CC0" 미확인) → 보류 | [css-loaders.com](https://css-loaders.com/) |
| ↳ **대체: `cssloaders/cssloaders.github.io`** | loader (CSS) | **MIT** ✅ | 고지만 | ✅ 복붙 | 동일 용도 순수 CSS 로더 | 위 컬렉션의 안전한 MIT 대체 | [github](https://github.com/cssloaders/cssloaders.github.io) |

### 권장 (Recommendation)

1. **Lottie 런타임 — 표면별 2-트랙.** 벡터·인터랙티브가 핵심이면 **Rive(`@rive-app/react-canvas`, MIT)**(`.riv` 경량·상태머신, ⚠️에셋 CC BY 4.0 출처표기 수용 필요). AE에서 뽑은 JSON이면 **`@lottiefiles/dotlottie-react`(MIT)** 또는 단순 **`lottie-react`(MIT)**. 둘 다 런타임 깨끗, JSON만 self-host. 절제 톤엔 **체결 성공 1–2개 + 핵심 로더에만** Lottie/Rive, 나머지는 CSS/SVG.
2. **무료 핀테크 애니메이션을 "안전하게" 구하는 경로** — LottieFiles/Rive Community에서 받되 **파일마다 라이선스 개별 확인**. LottieFiles는 "Lottie Simple License(무료·상용)"로 명시된 것만, Premium·"free with attribution"은 회피/크레딧. Rive 파일은 **전부 CC BY 4.0**(제작자 크레딧 노출). **출처표기 부담이 크면 핵심 애니메이션은 사내 제작(AE→Lottie/Rive)으로 자산화** → 라이선스 리스크 0 + 브랜드 일관성.
3. **숫자 카운트업 → `@number-flow/react`(MIT).** PnL/대표 KPI 헤드라인(`+₩1,240,000`)에 자릿수 롤이 "라이브 시세" 질감 + `Intl.NumberFormat`로 KRW·부호·로케일 네이티브. React 19/Next 16 SSR(+CSP nonce) 대응. 자릿수 롤 불필요한 보조엔 **react-countup(MIT)**.
4. **로더 — 에셋 라이선스 함정 없는 MIT/공개 조합.** 콘텐츠 자리표시 **react-loading-skeleton(MIT)**, 버튼 인라인 **react-spinners(MIT)** 또는 손맛 **SVG-Loaders(MIT)**, 0 deps 순수 CSS는 **`cssloaders/cssloaders.github.io`(MIT)**(css-loaders.com 원본은 미명시 보류). 리스트/빈 상태 전환은 **@formkit/auto-animate(MIT)**. 범용 모션은 **Motion(MIT)**(번들 큼, 필요 표면만). 체결 축하는 **canvas-confetti(ISC)**(짧게).

### 제외 / 주의

- ❌ **Lordicon (Free) — 상용 제외.** 비상용 전용 + 출처표기. 상용은 **PRO 구독 필수**.
- ⚠️ **useAnimations 아이콘 — 보류.** 코드 MIT지만 아이콘은 CC BY 4.0 + 재배포 금지("resalable software엔 그래픽 미포함"). 유료 SaaS 충돌 소지 → 대안 react-spinners/SVG-Loaders.
- ⚠️ **LottieFiles / Rive Community 에셋 — "런타임 MIT ≠ 에셋 무료".** 절대 일괄 "무료" 취급 금지. 파일별(LottieFiles)·CC BY 4.0 균일 출처표기(Rive) 확인.
- ⚠️ **css-loaders.com (원본) — 라이선스 미명시(미검증).** 상용 채택 보류, MIT 포크로 대체.
- ℹ️ **lottie-web 계열 번들 큼(~250KB).** 단순 로더에 Lottie 쓰지 말고 CSS/SVG로.
