# 에셋 큐레이션 매트릭스 — 아이콘·일러스트·브랜드·타이포 (2026-06-19)

> 리서치 기반. 코드 변경 없음. **라이선스는 각 출처 실제 LICENSE/공식 페이지에서 검증(검증일 2026-06-19)**. 채택 전 재확인 권장. 모두 자체호스팅(런타임 CDN 0) 전제.

## 매트릭스
| 에셋 | 유형 | 라이선스(검증) | 귀속 필요? | 자체호스팅 | 적합도 | 통합 노트 | URL |
|---|---|---|---|---|---|---|---|
| **Lucide** (현재) | 아이콘 | **ISC**(core)+MIT(일부) | 공개표기 불요(배포에 고지 유지) | O (inline SVG) | 높음 | 이미 의존성(`lucide-react`). 트리셰이킹. ~1,640+ | [LICENSE](https://github.com/lucide-icons/lucide/blob/main/LICENSE) |
| Phosphor | 아이콘 | **MIT** | 불요 | O | 높음 | ~1,500×6 weight. 배럴 import는 트리셰이킹 깨질 수 있음 | [LICENSE](https://github.com/phosphor-icons/core/blob/main/LICENSE) |
| Tabler | 아이콘 | **MIT** | 불요 | O | 높음 | ~6,100(최다), 작은 nav에선 stroke 다소 복잡 | [LICENSE](https://github.com/tabler/tabler-icons/blob/main/LICENSE) |
| Heroicons | 아이콘 | **MIT** | 불요 | O | 중 | ~316(적음), 핀테크 글리프 부족 | [LICENSE](https://github.com/tailwindlabs/heroicons/blob/master/LICENSE) |
| Remix Icon | 아이콘 | ⚠️ **커스텀 v1.0**(2024 Apache→변경) | 선택 | O | 중상 | **로고/브랜드 사용·팩 재판매 금지**. 표준 OSI 아님 — 채택 전 원문 검토 | [License](https://github.com/Remix-Design/RemixIcon/blob/master/License) |
| **unDraw** | 일러스트 | 커스텀(MIT 정신, SPDX 없음) | **불요** | O | 높음 | 단색 강조 플랫 → `#3182F6`로 리컬러. ⚠️ 팩 재배포·AI학습 금지, 경쟁 서비스화 금지 | [license](https://undraw.co/license) |
| Open Peeps | 일러스트(캐릭터) | **CC0** | 불요 | O | 중 | 공공도메인. 온보딩 페르소나용 | [site](https://www.openpeeps.com/) |
| Humaaans | 일러스트(캐릭터) | **CC0** | 불요 | O | 중 | 공공도메인(Pablo Stanley) | [site](https://www.humaaans.com/) |
| IRA Design | 일러스트 | **MIT**(Creative Tim) | 불요 | O | 중 | 그라데이션은 화려 → outline 세트 선호 | [repo](https://github.com/ira-design/ira-illustrations) |
| DrawKit(무료) | 일러스트 | 커스텀(전유) | 불요 | O(자사 제품 내) | 중상 | ⚠️ 재배포/판매·AI학습·템플릿빌더 금지. 인앱 빈상태는 허용 | [license](https://www.drawkit.com/license) |
| Streamline(무료) | 아이콘+일러스트 | Streamline Free | **필요**(streamlinehq.com 링크) | 기술적 가능 | **제외** | ⚠️ 귀속 강제 + "앱 자산으로 통합" 비권장 → 부적합 | [license](https://help.streamlinehq.com/en/articles/5354376-streamline-free-license) |
| Glaze(glazestock) | 일러스트(스톡) | 작가별·귀속 | **필요** | 위험 | **제외** | ⚠️ 작가별 귀속·큐레이션 스톡(균일 라이브러리 아님)·도메인 오프사이트 리다이렉트 | [about](https://www.glazestock.com/about/) |

## 아이콘 권장
**전 앱 단일 = Lucide(`lucide-react`) 유지** + **사이드바 이모지 → Lucide 교체**(`web/src/components/layout/SidebarNav.tsx`).
- 이유: ISC/MIT·공개귀속 불요·자체호스팅·이미 설치(신규 라이선스/번들/CDN 변경 0). 대시보드·다이얼로그에서 이미 Lucide 사용 → 2번째 패밀리 도입 시 stroke/라운드 불일치.
- 매핑 제안(전부 Lucide 존재): 홈 `Home` · 포트폴리오 `PieChart` · 매매 `ArrowLeftRight` · 내역 `ScrollText`/`ReceiptText` · 분석 `TrendingUp`/`Search` · 에이전트 `Bot` · 알림 `Bell` · 성향 진단 `Compass` · 설정 `Settings`. `<Icon size={18} aria-hidden />`로 렌더, `SidebarNav`의 `icon?: string`을 컴포넌트 참조로 변경.

## 일러스트 권장
현재 없음(Next 플레이스홀더 SVG만). 빈/에러/온보딩:
- **주: unDraw** — 강조색 `#3182F6`로 통일(SVG fill 1곳). 귀속 불요·상업 OK. **준수**: 팩 재배포·AI학습·경쟁서비스화 금지 → 필요한 SVG만 `web/public/illustrations/`에 자체호스팅(핫링크 금지).
- **보조(온보딩 캐릭터): Open Peeps / Humaaans(CC0)** — 의무 0.
- **제외**: Streamline Free(귀속+통합제한), Glaze(작가별 귀속·도메인 불안정). DrawKit/IRA는 가능하나 보조(DrawKit 재배포 금지, IRA 그라데이션 화려).

## 브랜드 방향
- **워드마크**: "Autofolio"를 **Pretendard**(자체호스팅, OFL)·Toss-blue `#3182F6` 유지. tracking `-0.02em`, weight 700, 선택적 투톤("Auto"=foreground/"folio"=brand). 현재 `SidebarNav` 브랜드 블록을 `<Brand />` 단일 컴포넌트로 추출해 nav·인증·헤더 재사용.
- **기하 마크(선택)**: 앱아이콘/파비콘 필요 시 상승 바/면적 모티프 또는 차트라인으로 만든 "A"를 **자체 SVG로 직접 제작**(아이콘팩 글리프를 로고로 쓰지 말 것 — Remix 등 금지).
- **파비콘**: 위 마크/워드마크 "A"에서 자체 SVG+ICO/PNG 생성해 `web/public/`의 Next 플레이스홀더 교체. (RealFaviconGenerator에 자작 아트 투입 또는 SVG 직접 export.)
- 외부 브랜드 에셋은 폰트(Pretendard, OFL)뿐 → 귀속 의무 0.

## 타이포·컬러 정제
- **숫자 `tabular-nums` 전면 확대**: `.kpi`·일부 테이블은 이미 적용. 돈/%/수량을 보이는 모든 표면(주문/내역/배분 비중)에 `tabular-nums` → 라이브 갱신 시 숫자 흔들림 제거. (토스는 금융 가독성용 자체 Toss Product Sans 제작 — [blog](https://blog.toss.im/article/beginning-of-tps), [TDS typography](https://tossmini-docs.toss.im/tds-react-native/foundation/typography/))
- **타입 스케일 명시**: Display 32/700·Title 20/600·Body 14/400·Caption 12/400 + 기존 KPI 26/700. KR 가독성 위해 line-height ~1.5–1.6. 헤딩은 `--font-heading`(=Pretendard).
- **컬러/엘리베이션**: up/down 의미색은 `format.ts`의 `pnlColor` 헬퍼 경유로만. 카드/다이얼로그 위계용 elevation 토큰(3단계) 추가(토스/카카오는 그림자+여백 중심).
- **다크모드 준비**: 다크 표면에서 `#3182F6` 대비 확인(저대비면 다크용 밝은 틴트), `--accent`/`--muted` 다크 대응값 명시. tabular-nums·타입스케일은 그대로 이월.

## 검증 출처
Lucide [LICENSE](https://github.com/lucide-icons/lucide/blob/main/LICENSE) · Phosphor [LICENSE](https://github.com/phosphor-icons/core/blob/main/LICENSE) · Tabler [LICENSE](https://github.com/tabler/tabler-icons/blob/main/LICENSE) · Heroicons [LICENSE](https://github.com/tailwindlabs/heroicons/blob/master/LICENSE) · Remix [License v1.0](https://github.com/Remix-Design/RemixIcon/blob/master/License) · unDraw [license](https://undraw.co/license) · Open Peeps · Humaaans · IRA [repo](https://github.com/ira-design/ira-illustrations) · DrawKit [license](https://www.drawkit.com/license) · Streamline [license](https://help.streamlinehq.com/en/articles/5354376-streamline-free-license) · Glaze [about](https://www.glazestock.com/about/) · Toss TPS/TDS.
