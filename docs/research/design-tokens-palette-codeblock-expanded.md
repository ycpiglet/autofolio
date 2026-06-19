# 디자인 토큰 — 색 팔레트 Ready-to-Paste 코드블록 (2026-06-19)

> 리서치 산출물. **E4/E5/E6(색 분리·히트맵/트리맵·다크모드)의 가속용 참조 코드** — 결정된 hex/구조를 그대로 `web/src/lib/design-tokens.ts`에 붙여넣을 수 있는 형태로 제공. **이 문서는 코드 변경이 아니다**(레퍼런스). 실제 토큰 파일은 동시 세션이 작업 중이라 충돌 회피로 여기 보관. 채택 시 기존 구조에 맞춰 병합.
> 근거·검증: [데이터viz 컬러 확장](./dataviz-libraries-and-color-expanded.md). 원칙: **PnL 의미색과 categorical 색의 hue 정체성은 절대 겹치지 않게 분리.**

## 1. categorical (Okabe-Ito CUD, 색맹 안전) — PnL과 네임스페이스 분리

```ts
// design-tokens.ts — categorical 시리즈 색(배분 도넛/스택 등). PnL 의미색 재사용 금지.
export const categoricalPalette = {
  catBlue:   "#0072B2", // 브랜드 계열 앵커(CVD-safe)
  catOrange: "#E69F00",
  catGreen:  "#009E73", // PnL green(#34C759)과 구분
  catPurple: "#CC79A7",
  catSky:    "#56B4E9", // ⚠️ 흰 배경 대비 ~1.9:1 → 채움+테두리에만
  catVermil: "#D55E00",
  catYellow: "#F0E442", // ⚠️ 흰 배경 ~1.1:1 → 어두운 채움에만
} as const;

export const categoricalOrder = [
  categoricalPalette.catBlue, categoricalPalette.catOrange, categoricalPalette.catGreen,
  categoricalPalette.catPurple, categoricalPalette.catVermil, categoricalPalette.catSky,
  categoricalPalette.catYellow,
] as const;
```
> `chartSeriesPalette`/`compactChartSeriesPalette`가 `categoricalOrder`를 가리키게 하고, 기존 `primary/negative/positive` 재사용을 제거. `pnlColorTokens`·`candleSeriesColors`·`equityAreaColors`는 불변.

## 2. PnL diverging 램프 (KR: 빨강=상승 / 파랑=하락, 색맹 안전 RdBu, 중립 midpoint)

```ts
// ColorBrewer RdBu 5-class를 KR 부호 규약에 매핑(down→up). ⚠️ 채택 시 NOTICE에 Cynthia Brewer 크레딧.
export const pnlDivergingRampKR = [
  "#0571b0", // 큰 하락
  "#92c5de",
  "#f7f7f7", // 보합(중립)
  "#f4a582",
  "#ca0020", // 큰 상승
] as const;

/** value를 ±maxAbs로 클램프해 5-class 이산 색 반환. 비색 신호(▲/▼·부호)와 병행 필수(WCAG 1.4.1). */
export function pnlDivergingColor(value: number, maxAbs: number): string {
  if (maxAbs <= 0 || value === 0) return pnlDivergingRampKR[2];
  const t = Math.max(-1, Math.min(1, value / maxAbs)); // -1..1
  // -1..1 → index 0..4 (0=큰하락 … 4=큰상승)
  const idx = Math.round((t + 1) * 2);
  return pnlDivergingRampKR[idx];
}
```
> Western 토글(상승=초록)에서는 RdBu 대신 `초록(#1a9850)–#f7f7f7–빨강(#d73027)` 사용하되 **색은 보조, ▲/▼·부호가 1차 신호**(RdYlGn 류 적록 회피).

## 3. sequential (트리맵 집중도·강도 히트맵) — Viridis(CC0) / Blues(브랜드)

```ts
// 부호 없는 크기(집중도/강도)는 sequential. Viridis=지각균일·CC0, Blues=브랜드 정합.
export const sequentialViridis = ["#440154","#3B528B","#21908C","#5DC863","#FDE725"] as const; // CC0
export const sequentialBlues   = ["#eff3ff","#c6dbef","#9ecae1","#6baed6","#4292c6","#2171b5","#084594"] as const;

/** 0..1 정규화 값 → sequential 색(이산). 밝은 끝 타일엔 어두운 글자(명도 기준 대비 전환). */
export function sequentialColor(t: number, ramp: readonly string[] = sequentialViridis): string {
  const x = Math.max(0, Math.min(1, t));
  return ramp[Math.round(x * (ramp.length - 1))];
}
```

## 4. dark-mode 브랜드 blue (Radix blue dark scale)

```ts
// light=브랜드 #3182F6(=Tailwind blue-500). dark는 Radix blue dark로 매핑(대비 확보).
export const brandBlueDark = {
  solid9:  "#0090ff", // 버튼/라인 솔리드 강조
  solid10: "#3b9eff", // 더 밝은 솔리드
  text11:  "#70b8ff", // 다크 배경 본문 대비 충족
  title12: "#c2e6ff", // 제목/하이라이트
  bg2:     "#111927", // 미묘한 배경 틴트
  border6: "#104d87", // 보더
} as const;
```
> 데이터 인코딩 색은 항상 §1~§3의 CVD 검증 팔레트에서. dark UI scale은 표면/chrome 전용.

## 5. 대비 체크(WCAG, 채택 전 [WebAIM](https://webaim.org/resources/contrastchecker/)로 확정)

- 데이터 색 vs 배경 ≥ **3:1**(SC 1.4.11): ⚠️ 흰 배경에서 `#F0E442`(~1.1)·`#56B4E9`(~1.9)·diverging 중립 `#f7f7f7`·viridis 밝은 끝 `#FDE725` 미달 → **셀/타일 경계선** 또는 어두운 배경 병용.
- 차트 텍스트 ≥ **4.5:1**(SC 1.4.3): 수치 라벨은 muted(`#8B95A1`) 대신 더 진한 회색(예 `#4E5968`). 모든 수치 `tabular-nums`.
