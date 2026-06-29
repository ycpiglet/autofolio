# Hosting Platform Research — autofolio (2026-06-29)

> 목적: autofolio(상용 유료 멤버십, **24/7 항상 켜진** 거래 워커 + KIS WebSocket + Postgres)를
> 어디에 배포할지 — 무료 한도/함정, 장기 유료 최소 스택, 장기 무료 방법.
> 모든 수치는 2026-06-29 공식 페이지에서 검증. 출처는 하단.

## 핵심 한 줄
autofolio는 **항상 켜진 백엔드**가 필수라 "무료 서버리스"가 안 맞고, **상용**이라 라이선스가 걸린다.
관리형 3종(Railway+Supabase Pro+Vercel Pro ≈ **$60–70/mo**) 대신 **VPS 한 대(Hetzner €3.99/mo ≈ $4.4)에 전부**
올리면 ~15배 저렴. 완전 무료는 **Oracle Cloud Always Free VM + Cloudflare/Netlify 무료**(단 운영 리스크).

---

## 1) DB (Postgres)

| 제공자 | 무료 한도 | 정지/슬립 | 유료 진입가 | 항상켜짐·상용 적합 |
|---|---|---|---|---|
| **Supabase Free** | 2 프로젝트·500MB·5GB egress·50K MAU | **1주 비활성 시 자동 정지**(수동 복구) | — | **불가** (워커가 죽음) |
| **Supabase Pro** | 8GB·250GB egress·100K MAU·일일백업 | **정지 없음** | **$25/mo** (+$10 compute 크레딧 포함) | **적합** |
| Neon Free | 100 CU-h·0.5GB | **5분 후 scale-to-zero(비활성화 불가)** | — | 불가 |
| Neon Launch | 사용량 | scale-to-zero 끌 수 있음 | ~$19–22/mo | 적합(이전 필요) |
| Aiven Developer | 1CPU·1GB RAM·8GB | **항상켜짐** | $5/mo | 가능하나 RAM 1GB로 빠듯 |

**가장 큰 함정**: Supabase Free는 1주 비활성 → 자동 정지. 항상 켜진 워커엔 치명적.
**무료 "관리형" 항상켜짐 Postgres는 2026년 기준 존재하지 않음.** → 자가호스팅(아래 VPS/Oracle)만이 무료 항상켜짐.

## 2) 프론트엔드 (Next.js, /api → 백엔드 프록시)

| 제공자 | 무료 한도 | **무료에서 상용 OK?** | App Router | 유료 진입가 |
|---|---|---|---|---|
| **Vercel Hobby** | 100GB BW·1M fn·1M edge req | **❌ 금지**(ToS: 개인·비상업만) | 네이티브 | **$20/seat/mo** |
| **Cloudflare Workers** | 무제한 static BW·100K req/day | **✅ 허용**(카드정보 직수집만 제한—Stripe.js면 무관) | OpenNext GA 1.0(2026-02) | **$5/mo**(10M req) |
| **Netlify** | 100GB BW·300 build-min/mo | **✅ 허용**(스태프 확인) | OpenNext 지원 | $9–20/mo |
| Vercel Pro | 1TB BW·10M edge req | ✅ | 네이티브 | $20/seat/mo |

**가장 큰 함정**: **Vercel Hobby(무료)는 상용 금지.** 유료 제품 프로덕션엔 약관 위반 →
Vercel Pro($20)로 가거나, **Cloudflare/Netlify(무료에서 상용 OK)** 로 이전.
> 현재 autofolio 프론트는 Vercel Hobby(`autofolio-black.vercel.app`)에 떠 있음 — staging은 OK, **유료 런칭 전 이전/업그레이드 필요**.

## 3) 백엔드 (FastAPI + 24/7 워커) — 결정 기준 = "안 잔다"

| 제공자 | 무료(항상켜짐? 슬립?) | 최저 항상켜짐 비용/mo | 상용 | FastAPI+24/7 적합 |
|---|---|---|---|---|
| **Railway**(현재) | 무료티어 없음($5 1회 크레딧). Hobby는 항상켜짐 | **~$15–25**(2서비스 사용량) | ✅ | 적합하나 비용 예측難 |
| **Render** | 무료=**15분 후 슬립**(워커 죽음) | $14(2×$7 Starter) | ✅ | 무료 불가, 유료만 |
| **Fly.io** | 무료티어 없음. `auto_stop` 끄면 항상켜짐 | **~$6–8**(2×shared-1x) | ✅ | 적합(설정 필요) |
| **Oracle Cloud Always Free** | **2 OCPU/12GB ARM VM 평생 무료**(안 잠) | **$0** | ✅ | 무료 최선이나 리스크↓ |
| **Hetzner VPS** | 무료 없음 | **€3.99(~$4.4)** CX23: 2vCPU/4GB/40GB/20TB | ✅ | **최고 가성비**, 한 박스에 전부 |

**함정**: Render 무료=15분 슬립(WebSocket 끊김). Fly는 `auto_stop_machines="off"` 안 하면 슬립.
**Oracle Always Free 리스크**: ① 용량 추첨(A1 프로비저닝 실패 잦음) ② 유휴 회수(7일 CPU·네트워크·메모리 모두 <20%면 회수 — KIS WebSocket 하트비트로 네트워크 유지 필요) ③ ARM(aarch64 — KIS SDK/네이티브 휠 호환 확인) ④ SLA 없음, 정책 무통보 변경(2026-06 자원 절반 축소) ⑤ 가입 시 카드 필요.

---

## 추천 스택 3안

**A. 똑똑한 장기 유료 (월 ~$4.4) — 추천**
- **Hetzner CX23(€3.99/mo) 한 대에 Docker로 전부**: FastAPI + 워커 + Postgres + (원하면)프론트.
- 항상켜짐·상용OK·x86(ARM 문제 없음)·정액(예측가능)·20TB BW. 관리형 3종 대비 ~15배 저렴.
- 단점: 직접 운영(OS 업데이트·백업 스크립트). pg 백업은 cron+pg_dump로.

**B. 완전 무료 장기 (월 $0) — 리스크 감수**
- **Oracle Cloud Always Free VM**(2 OCPU/12GB)에 FastAPI+워커+Postgres 자가호스팅 + **Cloudflare/Netlify 무료** 프론트.
- 단점: Oracle 용량추첨/유휴회수/ARM/무SLA. 상용 핀테크엔 운영 리스크. **Hetzner 폴백 준비 권장.**

**C. 관리형 편의 (월 ~$45–55)**
- Supabase Pro($25) + Cloudflare($5) + Railway($15–25). 운영 최소, 가장 비쌈.
- (현재 trajectory지만 Vercel은 Pro로 바꿔야 상용 합법 → 그러면 +$20.)

**의사결정**: 장기 운용이면 **B(무료)로 시작 → 수익/안정성 필요 시 A(Hetzner)로 이전**(이전 비용 작음).
지금 staging은 현행(Railway+Supabase free+Vercel free) 유지하며 테스트 계속 가능 —
단 **Supabase free 1주 정지 + Vercel Hobby 상용금지**는 프로덕션 전 반드시 해소.

---

## 출처 (2026-06-29 fetch)
- Supabase: https://supabase.com/pricing · Neon: https://neon.com/pricing · Aiven: https://aiven.io/developer-tier
- Vercel Fair Use(상용금지): https://vercel.com/docs/limits/fair-use-guidelines · ToS: https://vercel.com/legal/terms
- Cloudflare Terms: https://www.cloudflare.com/terms/ · Workers 가격: https://developers.cloudflare.com/workers/platform/pricing/ · OpenNext: https://opennext.js.org/cloudflare
- Netlify 상용 확인: https://answers.netlify.com/t/can-we-use-netlify-free-plan-for-commercial-purposes/41545 · 가격: https://www.netlify.com/pricing/
- Railway: https://docs.railway.com/pricing/plans · Render: https://render.com/pricing · Fly: https://fly.io/docs/about/pricing/
- Oracle Always Free: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm · 2026 변경: https://terminalbytes.com/oracle-cloud-free-tier-changes-2026/
- Hetzner: https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ · 계산기: https://costgoat.com/pricing/hetzner
