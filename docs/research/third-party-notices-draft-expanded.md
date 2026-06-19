# 서드파티 NOTICE·귀속 초안 — 추천 픽 (2026-06-19)

> 리서치 산출물. **상용 출시 전 필수 컴플라이언스 자료.** 확장 리서치에서 **추천(채택 후보)** 한 자원만 대상으로, 라이선스 의무를 "그대로 쓸 수 있는" 형태로 정리한다. 채택 시 이 텍스트를 (1) 리포 루트 `THIRD-PARTY-NOTICES.md` 와 (2) 앱 내 `설정 > 정보/오픈소스 고지`(또는 `/credits`)에 반영한다. 검증일 2026-06-19. 코드·의존성 변경 0.
> 관련: [개요](./2026-06-19-open-source-visual-assets-expanded.md) · [라이선스 리스크 레지스터](./2026-06-19-open-source-visual-assets-expanded.md#라이선스-리스크-레지스터-제외주의-종합).

## 의무 유형별 규칙 (먼저 읽기)

| 라이선스 | 배포물 의무 | 화면 귀속 | 비고 |
|---|---|---|---|
| **MIT / ISC / BSD** | 라이선스 전문 + 저작권 고지 **유지**(배포물 내) | 불요 | 가장 단순. `THIRD-PARTY-NOTICES.md`에 텍스트 보존 |
| **Apache-2.0** | LICENSE + **NOTICE 파일 유지**(있으면) | 불요 | 특허 그랜트. MingCute·Material Symbols·Carbon·lightweight-charts·KLineChart·Tremor |
| **SIL OFL 1.1** | 저작권 + OFL 전문 유지, **폰트 단독 유료 판매 금지** | 불요 | Pretendard·Wanted Sans·SUIT·Inter·Reddit Mono… (SUIT·Gmarket은 OFL.txt 직접 동봉) |
| **CC0 / Public Domain** | 의무 없음(크레딧 권장) | 불요 | Open Doodles·DiceBear CC0 스타일·3dicons.co·Viridis/Cividis·Open Color |
| **CC-BY-4.0** | 저작자·라이선스·변경여부 **명시** | **필요(가시 크레딧)** | 채택 시에만. ColorBrewer(특수)·(회피 권장: Solar·Hero Patterns·Rive 에셋·useAnimations 아이콘) |
| **커스텀(무귀속)** | 약관별 — 재배포/AI학습 제한 흔함 | 불요 | unDraw·ManyPixels·Pixeltrue: 무귀속이나 **팩 재배포·AI학습 금지** |

## 추천 픽별 NOTICE 엔트리 (그대로 사용)

### 차트·시각화 (코드)
- **Recharts** — MIT © Recharts Group. (기존)
- **lightweight-charts** — Apache-2.0 © TradingView, Inc. (기존)
- **uPlot** — MIT © Leon Sorokin.
- **KLineChart** — Apache-2.0 © liihuu (KLineChart).
- **Chart.js** — MIT © Chart.js Contributors. / **react-chartjs-2** — MIT © Jeremy Ayerst.
- **@mui/x-charts** (커뮤니티) — MIT © MUI.
- **billboard.js** — MIT © NAVER Corp. & Jae Sung Park.

### 컬러 (팔레트 데이터)
- **ColorBrewer** — ⚠️ **특수 의무**: 채택 시 NOTICE에 *"This product includes color specifications and designs developed by Cynthia Brewer (http://colorbrewer.org/)."* 명시 + **제품명에 "ColorBrewer" 사용 금지**. (RdBu/Blues/YlOrRd 등)
- **Viridis / Cividis / Magma** — CC0 (Stéfan van der Walt & Nathaniel Smith). 의무 없음(크레딧 권장).
- **Radix Colors** — MIT © WorkOS. / **Open Color** — MIT © heeyeun. / **Tailwind** — MIT © Tailwind Labs.
- ⚠️ **Paul Tol 팔레트**: 명시 라이선스 텍스트 부재 → 상용 채택 전 저자 확인, 또는 ColorBrewer/CC0로 치환(동등).

### 아이콘·국기·통화
- **Lucide** — ISC © Lucide Contributors (+ MIT © Cole Bemis/Feather 일부). (기존)
- **MingCute** — Apache-2.0 © MingCute (Richard9394).
- **Tabler Icons** — MIT © Paweł Kuna. (`currency-won`)
- **circle-flags** — MIT © HatScripts. / **flag-icons** — MIT © Panayiotis Lipiridis.
- ⚠️ **상표**: 어떤 라이선스든 **브랜드/카드/거래소 로고는 각 소유자 상표** — Simple Icons·web3icons·ccicons는 출시 전 브랜드별 가이드라인 개별 검토(귀속과 별개).

### 일러스트·캐릭터·아바타·3D
- **unDraw** — 커스텀(무귀속, 상업 OK). ⚠️ 팩 재배포·AI학습 금지 → 실사용 SVG만 self-host.
- **Open Doodles** — CC0 © Pablo Stanley. / **IRA Design** — MIT © Creative Tim.
- **ManyPixels** — 커스텀(무귀속). ⚠️ 팩 재배포 금지. / **Pixeltrue** — 커스텀(무귀속). ⚠️ 원본 재배포 금지.
- **DiceBear** core — MIT © Florian Körner. **스타일별 의무 상이**:
  - 무의무(CC0): Notionists·Lorelei·Open Peeps·Thumbs·Initials·Shapes 등.
  - 커스텀 무귀속: Bottts·Avataaars(© Pablo Stanley, "free for personal and commercial use").
  - ⚠️ **CC-BY 필요(회피 권장)**: Adventurer·Personas·Micah·Big Smile·Fun Emoji.
- **Boring Avatars** — MIT © boringdesigners. / **Big Heads** — MIT © Robert Broersma.
- **3dicons.co** — CC0. / **Microsoft Fluent Emoji** — MIT © Microsoft (NOTICES에 MIT 텍스트 포함, 화면 귀속 불요).

### 컴포넌트·모션
- **shadcn/ui** — MIT © shadcn. / **Radix UI** — MIT © WorkOS. / **Tremor** — Apache-2.0 © Tremor.
- **lottie-react / dotlottie-react / @rive-app/react-canvas / @number-flow/react / react-loading-skeleton / @formkit/auto-animate / Motion** — 전부 MIT. / **canvas-confetti** — ISC © Kiril Vatev.
- ⚠️ **에셋은 별도**: LottieFiles 파일(파일별)·Rive Community 파일(**CC-BY-4.0 균일, 제작자 크레딧 필요**)·Lordicon(상용=PRO) — "런타임 MIT ≠ 에셋 무료".

### 폰트 (OFL — 저작권+OFL 전문 유지)
- **Pretendard** © Kil Hyung-jin. / **Wanted Sans** © Wanted Lab. / **SUIT** © Sun Dolla(OFL.txt 직접 동봉). / **Inter** © Rasmus Andersson. / **Reddit Mono** © Reddit/그외. / **JetBrains Mono** © JetBrains. (모두 SIL OFL 1.1)

### 이미지·배경
- **Pexels / Unsplash 사진** — 각 라이선스(상업 무료·무귀속). ⚠️ 경쟁 스톡 재배포 금지·인물/상표 컷 개별 검수.
- **Haikei / SVGBackgrounds 무료세트 / pattern.css(MIT)** — 무귀속. ⚠️ **Hero Patterns 채택 시 CC-BY 가시 크레딧 필요**(없으면 대체).

## 적용 체크리스트 (채택 시)

1. 리포 루트 `THIRD-PARTY-NOTICES.md` 생성 — 위 엔트리 중 **실제 채택분만** + 각 라이선스 **전문** 보존.
2. CC-BY 채택분(있으면)·ColorBrewer 특수문구 → 앱 내 `설정 > 오픈소스 고지`(가시 크레딧)에도 표기.
3. 상표(브랜드/카드 로고) → **판매 전 금융규제 게이트와 함께** 브랜드별 가이드라인 검토 항목으로 등록.
4. 무귀속이라도 **재배포/AI학습 제한**(unDraw·ManyPixels·Pixeltrue) → "실사용 파일만 self-host, 팩 재배포 금지" 운영 규칙 명문화.
