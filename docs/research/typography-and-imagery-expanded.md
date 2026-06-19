# 타이포그래피(한글·숫자) + 이미지·배경·그라데이션 (확장 리서치, 2026-06-19)

> 리서치/큐레이션만. **코드·의존성 변경 0.** 적용은 별도 승인 후.
> Autofolio는 **self-host(런타임 CDN 0)** — 폰트는 서브셋 woff2 자체 서빙, 이미지/배경은 다운로드/생성 후 직접 호스팅(핫링크·런타임 API 금지). 브랜드 Toss-blue `#3182F6` + Pretendard.
> 라이선스는 공식 LICENSE/OFL 파일·파운드리 페이지에서 **검증일 2026-06-19** 확인(일부 숫자 기능은 폰트 바이너리 직접 검사). 불확실 항목 ⚠️. 관련: [개요](./2026-06-19-open-source-visual-assets-expanded.md).

---

## A. 타이포그래피 — 한글·숫자 폰트 (확장)

> **선정 기준(자체호스팅 전제):** 라이선스가 **임베딩 + 재배포 + (서브셋용) 수정**을 허용해야 한다. 진짜 SIL OFL 1.1은 이 모든 권리를 부여(유일 제약=폰트 단독 유료 판매 금지, 우리에겐 무영향). 한국 기업 "무료" 폰트 중 일부는 *웹폰트 임베딩·재배포·수정을 금지*하는 커스텀 라이선스라 자체호스팅을 깨뜨린다 → 제외.
>
> ⚠️ **핵심 결론:** 조사한 한글 5종 + 라틴/모노 11종은 **전부 정식 SIL OFL 1.1 → 제외 0**. 고위험으로 지목됐던 **Spoqa Han Sans Neo·Gmarket Sans**도 실제 LICENSE/공식 페이지 검증 결과 자체호스팅에 문제없는 정식 OFL이었다.

### 1) 한글 UI 폰트

| 폰트 | 언어 | 라이선스(검증) | 웹폰트 임베드·자체호스팅? | tabular 숫자 | 적합도 | URL |
|---|---|---|---|---|---|---|
| **Pretendard** (baseline) | 한·라 | **OFL 1.1** (verbatim) ✓ | **YES** | tnum 지원 | 기준점(현행) | [LICENSE](https://github.com/orioncactus/pretendard/blob/main/LICENSE) |
| **Wanted Sans** 원티드 산스 | 한·라 | **OFL 1.1** (레포 OFL.txt verbatim) ✓ | **YES** — "embed, modify, redistribute, and sell" | tnum 지원(가변) | ★ 최상위 KR 대안 | [OFL.txt](https://github.com/wanteddev/wanted-sans/blob/main/OFL.txt) |
| **SUIT** 수트 | 한·라 | **OFL** (파운드리 선언; ⚠️ 레포에 OFL.txt 없음) | **YES** (웹폰트·임베딩·재배포 허용) | **tnum 기본 + ss01 대체숫자** | ★ 최상위 KR 대안 | [sun.fo/suit](https://sun.fo/suit) · [github](https://github.com/sunn-us/SUIT) |
| **Spoqa Han Sans Neo** | 한·라·일 | **OFL 1.1** (레포 LICENSE verbatim·클린) ✓ | **YES** | tnum 지원(정적) | 양호 | [LICENSE](https://github.com/spoqa/spoqa-han-sans/blob/main/LICENSE) |
| **Gmarket Sans** 지마켓 산스 | 한·라 | **OFL** (공식 선언; ⚠️ 인라인 OFL.txt 없음) | **YES** — 영리·비영리 자유 사용·웹폰트·재배포 허용 | tnum 지원(정적 3종) | 양호(제목/브랜드) | [corp.gmarket.com/fonts](https://corp.gmarket.com/fonts) |
| **IBM Plex Sans KR** | 한·라 | **OFL 1.1** (Reserved "Plex") ✓ | **YES** | tnum 지원 | 양호 | [LICENSE](https://github.com/IBM/plex/blob/master/LICENSE.txt) |
| **Noto Sans KR** | 한·라 | **OFL 1.1** ✓ | **YES** | tnum 지원(가변) | 안전 폴백 | [google/fonts](https://github.com/google/fonts/tree/main/ofl/notosanskr) |
| **Freesentation** 프리젠테이션 | 한·라 | **OFL 1.1** ✓ | **YES** | tnum 지원(가변 9웨이트) | 양호(모던) | [noonnu](https://noonnu.cc/) |
| **Paperlogy** 페이퍼로지 | 한·라 | **OFL 1.1** ✓ (9웨이트) | **YES** | tnum 지원 | 양호(디스플레이) | [noonnu](https://noonnu.cc/) |

> ⚠️ **문서화 주의(채택 무방, 감사 추적용):** **SUIT·Gmarket Sans**는 1차 출처에 조항별 OFL.txt가 동봉돼 있지 않다 → 채택 시 **vendored 폰트 폴더에 표준 SIL OFL 1.1 전문을 직접 복사**하고 파운드리 URL을 출처로 명기(Gmarket은 2026-06-19자 페이지 아카이브 권장). Pretendard·Wanted Sans·Spoqa·IBM Plex·Noto는 레포에 OFL 전문 동봉돼 추가 조치 불필요.
> **가변폰트:** Pretendard·Wanted Sans·SUIT·Freesentation은 Variable(단일 wght 파이프라인 유리). Spoqa·Gmarket은 정적(웨이트별 서브셋).

### 2) 라틴·숫자·모노 (금융 수치 컬럼용)

| 폰트 | 언어 | 라이선스(검증) | 임베드·자체호스팅? | tabular 숫자 | 적합도 | URL |
|---|---|---|---|---|---|---|
| **Inter** | 라(확장) | **OFL 1.1** ✓ | **YES** | **YES** (`tnum`) + **slashed-zero(`zero`)** 둘 다 ✓ | ★ 비례숫자 최상위 | [LICENSE](https://github.com/rsms/inter/blob/master/LICENSE.txt) |
| **Geist (Sans)** | 라(확장) | **OFL 1.1** ✓ | **YES** | `tnum` ✓ / **slashed-zero 없음** | 높음 | [LICENSE](https://github.com/vercel/geist-font/blob/main/LICENSE.txt) |
| **Geist Mono** | 라(확장) | **OFL 1.1** ✓ | **YES** | YES(모노). 0 토글 미확인 | 높음 (Geist 페어링) | [LICENSE](https://github.com/vercel/geist-font/blob/main/LICENSE.txt) |
| **JetBrains Mono** | 라·키·그 | **OFL 1.1** ✓ (Apache→OFL 이전 완료) | **YES** | YES(모노). 기본 점0 + **`zero`로 slashed 지원** | ★ 높음(워크호스) | [OFL.txt](https://github.com/JetBrains/JetBrainsMono/blob/master/OFL.txt) |
| **IBM Plex Mono** | 라(확장) | **OFL 1.1** ✓ | **YES** | YES(모노). slashed-zero는 `"zero"`/`ss03` 옵트인 | 높음 | [LICENSE](https://github.com/IBM/plex/blob/master/LICENSE.txt) |
| **Roboto Mono** | 라(확장) | **OFL 1.1** ✓ (⚠️ **Apache 아님**·재라이선스) | **YES** | YES(모노). **기본 점0**(slashed 없음) | 높음 | [OFL.txt](https://github.com/googlefonts/RobotoMono/blob/main/OFL.txt) |
| **Reddit Mono** | 라·베 | **OFL 1.1** ✓ | **YES** | YES — **duplexed tabular**(웨이트 무관 폭 불변) + **기본 slashed-zero** | ★ 높음(라이브 테이블 최적) | [google/fonts](https://github.com/google/fonts/tree/main/ofl/redditmono) |
| **Space Mono** | 라(확장) | **OFL 1.1** ✓ | **YES** | YES(모노). 디스플레이 점0 | 중간(2웨이트) | [google/fonts](https://github.com/google/fonts/tree/main/ofl/spacemono) |
| **DM Mono** | 라 | **OFL 1.1** ✓ | **YES** | YES(모노). 0 스타일 미확인 | 중간(정적) | [google/fonts](https://github.com/google/fonts/tree/main/ofl/dmmono) |
| **DM Sans** | 라 | **OFL 1.1** ✓ | **YES** | **NO** (tnum 부재) | **낮음(숫자열 부적합)** | [google/fonts](https://github.com/google/fonts/tree/main/ofl/dmsans) |
| **Commit Mono** | 라·그 | **OFL 1.1** ✓ (⚠️ **이중**: 루트 LICENSE=MIT는 웹코드용, **폰트는 `LICENSE-FONT`=OFL**) | **YES** — "embed, modify, redistribute, sell" | YES(모노). 0 대체자 기본 OFF | 높음 | [LICENSE-FONT](https://github.com/eigilnikolajsen/commit-mono/blob/main/LICENSE-FONT) |

> ⚠️ **브리프 가정 대비 정정:** (1) **Roboto Mono = OFL 1.1**(Apache 아님). (2) **DM Sans = tabular 미지원** → 머니/PnL 셀 금지. (3) **Geist Sans = `tnum` 있으나 slashed-zero 없음**(Inter는 둘 다). (4) **Commit Mono = 루트 MIT 아니라 `LICENSE-FONT`(OFL) 동봉 필요**. (5) **IBM Plex Mono slashed-zero는 `"zero"` 옵트인**(기본 아님).

### 권장 (Top picks) — 타이포

**한글 UI (Pretendard 보완·대체):**
- **1순위 — Wanted Sans 또는 SUIT.** 둘 다 정식 OFL·가변폰트·자체호스팅 가능한 모던 핀테크 UI 폰트. **SUIT는 `tnum` 기본 + ss01 대체숫자** 내장 → 한글 본문과 숫자 테이블을 한 폰트로 끌고 갈 수 있어 금융 화면에 매력적(OFL.txt 직접 vendoring). **Wanted Sans**는 레포에 OFL 전문 동봉돼 감사 추적이 가장 깨끗 + 가변.
- 보조/폴백: **IBM Plex Sans KR**·**Noto Sans KR**(가장 안전 폴백). Freesentation/Paperlogy/Spoqa/Gmarket도 전부 OFL이라 브랜드·제목용 혼용 가능.

**금융 테이블 숫자/모노:**
- **비례 숫자 UI → Inter.** `tnum`+slashed-`zero`를 **모두** 갖춘 유일 후보. 라이브 갱신 숫자 지터 방지 최적(CSS `font-variant-numeric: tabular-nums` 필수).
- **머니/PnL 모노 컬럼 → Reddit Mono(duplexed tabular + 기본 slashed-0, 단일 가변) 또는 JetBrains Mono(0/O 구분 문서화 가장 탄탄, 가변).** 대안: Roboto Mono(기본 점0)·IBM Plex Mono(`"zero"` slash)·Geist Mono(Geist 페어링).

**운영 메모:** ① 비례 폰트는 `font-variant-numeric: tabular-nums` 줘야 tabular 작동. ② IBM Plex/JetBrains Mono는 slashed-zero에 `font-feature-settings: "zero"`, Commit Mono는 서브셋에 0 대체자 구워넣기. ③ 서브셋 시 미사용 스크립트(키릴·그리스·베트남어) 제외, **Latin + Latin-Ext + 숫자 + 금융기호**만 남겨 woff2 최소화.

### 제외 / 주의 — 타이포

- **제외(EXCLUDE): 없음.** 조사한 한글 5종·라틴 11종은 전부 SIL OFL 1.1로 자체호스팅 서브셋 woff2 임베딩 + 상용 + 재배포 허용(공통 OFL 조건: 저작권+라이선스 고지 유지, 폰트 단독 유료 판매 금지).
- ⚠️ **숫자 부적합 — DM Sans:** OFL이나 tabular 부재 → 머니/PnL 컬럼 사용 금지(라벨/본문만).
- ⚠️ **문서화 보강 — SUIT·Gmarket Sans:** 정식 OFL이나 1차 출처에 OFL.txt 없음 → 표준 전문 직접 동봉 + 파운드리 URL 명기.
- ⚠️ **이중 라이선스 — Commit Mono:** 폰트 권리는 `LICENSE-FONT`(OFL)에 있으니 배포 시 동봉.
- ⚠️ **미검증(시각 확인 권장):** DM Mono·Space Mono·Geist Mono 기본 0 글리프 스타일, Geist Mono `zero` 토글.

---

## B. 이미지·배경·그라데이션·패턴 (확장)

> **금융 제품 톤:** 신뢰감엔 **온브랜드(`#3182F6`) 자체생성 SVG 그라데이션·패턴**을 기본으로, 사진은 랜딩/마케팅 한정. 생성형 그라데이션이 진부한 스톡 사진보다 UI에 거의 항상 낫다. 전부 다운로드/생성 후 자체호스팅(핫링크·런타임 API 금지).

### 1) 사진 (Stock Photos — 랜딩/마케팅 한정)

| 자원 | 유형 | 라이선스(검증) | 귀속 | 자체호스팅 | 적합 표면 | 주의 | URL |
|---|---|---|---|---|---|---|---|
| **Unsplash** | 사진 | Unsplash License — 상업 무료 ✅ | 불필요 | 가능 | 랜딩 히어로 | ⚠️ "경쟁 스톡 서비스 복제용 수집" 금지(제품 UI 무관)·인물/상표 컷 개별 검수 | [license](https://unsplash.com/license) |
| **Pexels** | 사진/영상 | Pexels License — 상업 무료 ✅ | 불필요 | 가능 | 랜딩 히어로 | ⚠️ 미변형 재판매·타 스톡 재배포 금지·상표/인물 제약 | [license](https://www.pexels.com/license/) |
| **Pixabay** | 사진/영상/벡터 | Pixabay Content License ✅ | 불필요 | 가능 | 랜딩·보조 | ⚠️ 스톡으로 재판매 금지·**AI생성/모델릴리스 미검증 → 인물·상표 신중** | [license](https://pixabay.com/service/license/) |
| **Burst (Shopify)** | 사진 | CC0 + Burst License ✅ | 불필요 | 가능 | 랜딩(커머스 톤) | ⚠️ 사진 단독 판매 금지·컬렉션 작음 | [licenses](https://www.shopify.com/stock-photos/licenses) |
| **Openverse** (CC 애그리게이터) | 사진 검색 | 작품별 상이(CC0/CC-BY/PD) ✅ | **작품별**(CC-BY 다수) | 가능(원본 확인 후) | 특정 주제 보강 | ⚠️ **라이선스 미보증 → 사용자 책임.** UI 일괄 사용 비권장 | [about](https://openverse.org/about) |
| StockSnap/Kaboompics/Gratisography 등 | 사진 | 대체로 CC0류이나 **자산별 상이** — ⚠️ 개별 검증 | 사이트별 | 가능 | 랜딩 보조 | ⚠️ 한 곳으로 충분(아래 권장). 추가 시 재검증 | (각 공식 페이지) |

### 2) 배경·그라데이션·패턴 (SVG/CSS, 자체호스팅 — 금융 UI 권장)

| 자원 | 유형 | 라이선스(검증) | 귀속 | 자체호스팅 | 적합 표면 | 주의 | URL |
|---|---|---|---|---|---|---|---|
| **Tailwind 그라데이션 유틸** | CSS 그라데이션 | **MIT** (이미 스택 내장) | 불필요 | N/A(코드) | 모든 표면 — **1순위** | 자산 파일 불필요. `#3182F6` 토큰 온브랜드 즉시 | [docs](https://tailwindcss.com/docs/gradient-color-stops) |
| **CSS grainy-gradient 기법** | CSS+SVG noise | 기법(라이선스 불요) | 불필요 | 가능 | 히어로/배경 질감 | 외부 자산 0. 그라데이션 위 노이즈로 "비싼" 질감 | (W3C SVG 필터) |
| **Haikei** (Blobmaker·Get Waves 통합) | SVG 생성기(그라데이션/웨이브/블롭/메시) | 생성물 상업 자유, 크레딧 불필요 ✅ | 불필요 | 가능(SVG export) | auth/랜딩 배경·블롭/웨이브 | ⚠️ "유사 생성 서비스" 제공만 금지(제품 UI 무관). 색을 `#3182F6`로 지정 | [haikei.app](https://haikei.app/) |
| **SVGBackgrounds.com** (무료 세트) | SVG 배경/패턴 | 비독점·전세계, 개인·상업 가능 ✅ | 불필요(무료 세트) | 가능 | 랜딩/섹션 배경 | ⚠️ 재배포는 Extended만(제품 내 사용 무관). 무료 세트만 | [license](https://www.svgbackgrounds.com/license/) |
| **pattern.css** | CSS 패턴 라이브러리 | **MIT** (npm 검증) ✅ | 불필요 | 가능(CSS 번들) | 카드/플레이스홀더 배경 | 의존성 0, Tailwind 충돌 없음 | [npm](https://www.npmjs.com/package/pattern.css) |
| **Hero Patterns** | SVG 타일 패턴 | **CC BY 4.0** ✅ | ⚠️ **필수(귀속)** | 가능 | 미세 섹션/카드 배경 | ⚠️ 푸터/`/credits`에 "Hero Patterns by Steve Schoger (CC BY 4.0)" 표기 가능하면 사용, 아니면 **제외** | [heropatterns.com](https://www.heropatterns.com/) |
| **Magic Pattern** (magicpattern.design) | SVG/CSS 패턴 생성기 | ⚠️ **무료 내보내기 상업 사용 금지(사전 서면 동의 필요)**(Terms §9) | — | — | — | ⚠️ **제외 권장** | [terms](https://www.magicpattern.design/terms) |
| **Transparent Textures** | 반복 텍스처 PNG | ⚠️ **라이선스 페이지 부재 — 미검증** | 불명 | 가능 | 미세 배경 질감 | ⚠️ 통합 라이선스 명문 없음 → 비권장(Haikei/SVGBackgrounds 대체) | [transparenttextures.com](https://www.transparenttextures.com/) |
| Cool Backgrounds | 생성기(Trianglify 등) | ⚠️ **통합 라이선스 부재 — 미검증** | 불명 | 가능 | 랜딩 배경 | ⚠️ 하위 도구별 상이. Haikei로 대체 → 비권장 | [coolbackgrounds.io](https://coolbackgrounds.io/) |
| meshgradient 생성기류 | 메시 그라데이션 | ⚠️ **생성기별 상이 — 미검증** | 사이트별 | 가능 | 히어로/auth 배경 | ⚠️ Haikei 메시로 라이선스 명확 대안 → Haikei 우선 | (각 공식 페이지) |

### 권장 (Top picks) — 이미지

**랜딩 사진:** **Pexels(귀속 불필요·상업 명확)** 1순위 + **Unsplash** 보조. 둘이면 충분("경쟁 스톡 복제"만 회피). 인물/상표/로고 컷은 개별 검수.

**온브랜드 그라데이션·패턴 — 코드 우선:**
1. **auth/랜딩 배경** → **Tailwind 그라데이션 유틸 + grainy-gradient(SVG noise)**. 자산 0, `#3182F6` 즉시. 더 표현적 메시는 **Haikei**를 `#3182F6` 계열로 생성해 SVG 1장 저장.
2. **은은한 섹션 배경** → **SVGBackgrounds 무료 세트** 또는 **pattern.css(MIT)**. (Hero Patterns는 **CC-BY 귀속 표기 동선**이 있을 때만, 없으면 대체.)
3. **장식 블롭/웨이브 액센트** → **Haikei**(통합 Blobmaker·Get Waves). 단색/저채도 `#3182F6`로 절제(푸터 웨이브·카드 블롭).

> 결론: **자체생성 SVG(Tailwind+Haikei)로 색을 직접 통제**하는 편이 톤이 들쭉날쭉한 스톡 배경보다 금융 신뢰 톤에 맞고 런타임 CDN 0 원칙과도 부합.

### 제외 / 주의 — 이미지

- ❌ **Magic Pattern (magicpattern.design)** — 무료 내보내기 상업 사용 사전 서면 동의 없이 금지 → 유료 핀테크 부적합. Haikei/SVGBackgrounds로 대체.
- ⚠️ **Hero Patterns — CC-BY(귀속 의무).** 표기 동선 있을 때만, 없으면 제외하고 SVGBackgrounds/pattern.css 대체.
- ⚠️ **Openverse — 라이선스 미검증 애그리게이터.** UI 일괄 사용 비권장, 필요 개별 작품만 홈 컬렉션 확인 후.
- ⚠️ **AI 출처 주의.** Pixabay 등 AI생성 혼재 + 모델릴리스 미검증. 인물/유명 장소/상표 컷 회피·개별 검수.
- ⚠️ **재판매/재배포 제약(공통).** Unsplash·Pexels·Pixabay·Burst·SVGBackgrounds 모두 **자산을 다시 배포/판매하는 형태 금지**(제품 UI 사용엔 무관, 기록용).
- ⚠️ **미검증 — 보류:** Transparent Textures·Cool Backgrounds·meshgradient류 → Haikei/Tailwind/SVGBackgrounds로 대체 가능, 도입 시 재검증.
