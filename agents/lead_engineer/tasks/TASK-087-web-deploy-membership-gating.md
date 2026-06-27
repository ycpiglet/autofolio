---
type: task
id: TASK-087
display_id: TASK-087
task_uid: 8f3c1d92-4b07-4e6a-9c2a-7d5e0a1f9b3c
registered_at: 2026-06-18T23:46:54+09:00
created_at: 2026-06-18T23:46:54+09:00
updated_at: 2026-06-27T03:40:18+09:00
status: 진행 중
owner: Lead Engineer
assignees: [Lead Engineer, Backend Engineer, CI/CD Engineer, Compliance Officer, UI/UX Designer]
priority: High
difficulty: 상
est_hours: 24
est_tokens: 200000
tags: [deploy, web, auth, membership, payment, multitenant, compliance, supabase, vercel]
gate: Owner direct request; NO live order, NO secret commit, NO production DB apply, NO external deploy without explicit approval
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-013
created: 2026-06-18
---

# TASK-087 웹 배포 + 구매자 한정 회원제(게이팅·결제승인·멀티테넌트)

작업 ID: TASK-087
상태: 진행 중
Owner: Lead Engineer
요청 시각: 2026-06-18T23:46:54+09:00
기록 시각: 2026-06-18T23:46:54+09:00
요청자: Owner
수행자: Lead Engineer
의도: Autofolio를 웹 주소로 배포하고, "구매(입금)한 사람만 로그인" 가능한 회원제로 전환한다.
대상: 웹 배포, 구매자 한정 회원제, 인증/결제/멀티테넌트/컴플라이언스 계획
방법: 대기 TASK 기록으로만 등록하고, 배포/secret/production DB/live order 변경은 별도 승인 전까지 보류한다.
감사 로그: AUDIT-2026-06-18-013

## 배경 / 대화에서 확정된 사실 (2026-06-18 Owner 대화)

- **제품 포지션(확정 방향)**: "각 유저가 자기 KIS 키·자기 LLM 토큰(Claude/Codex)·자기 Google/Telegram으로
  스스로 돌리는 자기만의 프로그램". 우리는 **소프트웨어를 판매**하는 것이지, 우리가 대신 운용/추천/일임하지 않는다.
  → 이 포지션이면 금융투자업 인가가 아니라 **사업자등록 + 통신판매업 신고** 영역(가능성 높음).
- **법적 위험선(반드시 지킬 것)**:
  - 우리가 종목을 임의로 추천/배포하거나 자동승인을 우리가 대신 굴리면 → 유사투자자문/투자자문/투자일임 영역(신고·등록·인가).
  - 추천은 "유저 본인 AI/설정이 생성", 우리는 도구/프레임워크만 제공, "투자자문 아님" 고지 유지.
  - 결정·키·실행 통제권이 **유저에게** 있도록 설계(이 앱의 승인 흐름·한도·킬스위치가 이를 뒷받침).
- **선행 확인 항목(블로커 후보)**:
  - [ ] **KIS OpenAPI 이용약관**의 멀티유저/상용 사용 허용 여부 확인 (최우선).
  - [ ] 핀테크 전문 변호사 + 금감원 **비조치의견서/유권해석** — "SW 판매 vs 유사투자자문" 경계, 특히 추천 기능.
- **결제/입금 확인(확정 방향)**: 판매 적을 때 가상계좌 PG는 출혈 큼 → **MVP는 수동 승인**(은행앱 입금 확인 후
  관리자 화면 승인). 사업자등록 후 농협 오픈API/오픈뱅킹 입금내역 자동조회로 자동승인 업그레이드. 매칭은
  고유금액/입금자명 코드로 해결.
- **CTA/회원가입 정정(2026-06-19 Owner clarification)**: v1 CTA는 waitlist/demo가 아니라 **검증된 사람만 회원가입 승인**이다.
  선별 신청자에게 가격과 무통장입금 안내를 보여주고, Owner가 은행앱/관리자 증거로 수동 입금 확인하거나
  고유 코드/입금자명/금액 패턴으로 입금 인식이 되면 계정을 승인한다. 실제 계좌번호와 입금 기록은 repo에
  커밋하지 않고 runtime/admin 설정 또는 Owner-only 운영 정보로 관리한다.
- **배포 스택(추천 확정)**: 프런트=**Vercel**, 백엔드(FastAPI)+엔진 워커=**Railway**(또는 Render Starter; Render
  Free는 sleep으로 엔진 부적합), DB+Auth+Storage=**Supabase(Postgres)**. SQLite/로컬 vault → Supabase 이전이 핵심 선결.

## 범위

포함:

- 인증 전환: 현재 `auth_service.login_or_register`(없으면 자동가입)를 폐기 → `register`(가입신청=PENDING)
  / `login`(승인된 회원만). `members` 상태머신: `pending → 입금대기 → active → expired/rejected`.
- 안전 하위 구현 완료: TASK-099에서 unknown local ID/PW가 기본값으로 owner session을 자동 생성하지 않도록 막았다.
  first-run/dev 자동가입은 `AUTOFOLIO_LOCAL_AUTO_REGISTER=1` 명시 opt-in일 때만 허용된다.
- 로컬 프로토타입 완료: TASK-100에서 encrypted local vault 기반 가입신청 API, Owner-only 목록/상세 API,
  Owner+CSRF 상태전이 API, `/signup` 화면을 추가했다. 이 프로토타입은 실제 로그인 계정이나 subscription grant를
  생성하지 않는다.
- 로컬 관리자 UI 완료: TASK-101에서 `/settings`에 `회원 승인` 탭을 추가해 Owner가 local 신청 목록을 보고
  검증대기, 입금대기, 활성, 거절, 만료 상태로 전환할 수 있게 했다. 이후 TASK-102에서 같은 화면의
  입금확인 액션이 local account grant까지 수행하도록 확장됐다.
- 로컬 계정 grant 완료: TASK-102에서 Owner가 입금 확인 시 로그인 ID와 임시 비밀번호를 입력해 local `member`
  계정과 subscription grant를 생성할 수 있게 했다. 임시 비밀번호는 plaintext로 응답/저장하지 않는다. production
  DB, multi-tenant isolation, deploy, real payment recognition은 여전히 별도 gate다.
- 로컬 입금 인식 보조 완료: TASK-103에서 Owner가 `/settings`에 은행앱/CSV에서 복사한 입금내역 텍스트를 붙여넣어
  deposit_pending 신청과 입금코드/금액/신청자 정보를 대조할 수 있게 했다. raw pasted statement는 저장하지 않고,
  인식 결과는 자동활성화가 아니라 Owner 명시 승인 evidence(`code_assisted_deposit_match`)로만 사용한다.
- 로컬 권한 경계 보강 완료: TASK-104에서 `member`와 `owner`를 인가 dependency level에서 분리했다. member는
  자기 비밀번호/투자 프로필/위험고지 acknowledgement 같은 session-derived self-service만 가능하고, engine/trade/settings/
  membership admin 같은 global control mutation은 owner-only로 유지된다. production user_id isolation은 아직 별도 gate다.
- 게스트 데모 기본 차단 완료: TASK-105에서 `/api/auth/login`의 `guest=true` session 발급을 기본 403으로 바꾸고
  `AUTOFOLIO_GUEST_DEMO_ENABLED=1` 로컬/dev opt-in일 때만 허용했다. 로그인 화면의 게스트 CTA도 제거해 공개 진입은
  승인된 계정 로그인 또는 가입 승인 신청으로 한정된다.
- 제품 read scope 기본 차단 완료: TASK-106에서 포트폴리오/마켓/분석/매매/엔진/에이전트/stream/매뉴얼/계정/
  프로필 read API를 `require_app_user`로 올렸다. anonymous는 401, guest는 403, 승인 `member`/`owner`는 200으로
  분리된다. production user_id isolation은 아직 별도 gate다.
- 사용자 연동 토큰 하네스 완료: TASK-107에서 승인된 owner/member가 `/settings > 계정/연결`에서 자기 LLM/SNS provider
  token/account label/scopes/enabled status를 local encrypted vault에 저장/삭제할 수 있게 했다. API 응답은 `secret_set`과
  masked hint만 반환하고 token 원문을 echo하지 않는다. 실제 provider 호출, OAuth callback, production secret storage,
  KIS per-user broker credential activation은 아직 별도 gate다.
- 운영 전환 체크 완료: TASK-108에서 Owner-only `/api/membership/readiness`와 `/settings > 회원 승인` readiness panel을
  추가했다. Local flow는 pass로 표시되지만 Supabase/RLS, production secret storage, payment recognition, per-user engine/safety,
  KIS terms, external deploy는 block/watch로 남아 `can_launch=false`를 유지한다.
- Supabase/RLS production contract 완료: TASK-109에서 적용 전 production entity/RLS/user_id/secret/payment/engine 계약을
  `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json`/`.md`로 고정하고 `scripts/membership_contract_gate.py --check`로
  검증 가능하게 했다. 이는 design contract이며 실제 Supabase schema/RLS 적용이나 production isolation 증거는 아니다.
- 신청자 상태/입금안내 조회 완료: TASK-110에서 public `POST /api/membership/requests/status`와 `/signup` 상태 확인 panel을
  추가했다. 신청자는 request id와 contact가 일치할 때만 applicant-safe status를 보고, Owner가 `deposit_pending`으로 넘긴 후
  가격/입금코드/런타임 계좌 안내를 볼 수 있다. Owner notes/events, account grant, subscription grant는 공개 응답에서 제외된다.
- 입금 증거 보존 정책 완료: TASK-111에서 `MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json`/`.md`와
  `scripts/membership_payment_policy_gate.py`를 추가해 raw statement, full account number, payment secret,
  unredacted private identifier 보존을 금지하고 최소 masked audit field만 허용했다. 실제 결제수단 선택,
  production retention 구현, refund/receipt/tax 처리는 여전히 별도 gate다.
- 결제 인식 방식 결정 패킷 완료: TASK-117에서 `MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json`/`.md`와
  `scripts/membership_payment_recognition_decision_gate.py`를 추가해 MVP 결제 인식은 manual bank-app check +
  code-assisted deposit match로 고정했다. CSV import는 retention/delete/redaction test 후 후보, PG/가상계좌
  webhook은 provider setup/webhook verification/refund/receipt/tax/privacy review 후 scale upgrade,
  Open Banking transaction inquiry는 participation/security/function/credential/consent가 필요한 R3 lane으로
  분리했다. 실제 은행/PG/Open Banking 계정, credential, API call, real payment data 처리는 없다.
- tenant isolation matrix 완료: TASK-114에서 `MEMBERSHIP-TENANT-ISOLATION-MATRIX.json`/`.md`와
  `scripts/membership_tenant_isolation_gate.py`를 추가해 public/member/owner/worker route group, tenant surface,
  `auth.uid()` ownership, secret redaction, applicant lookup non-disclosure, staging cross-user test target을 적용 전
  matrix로 고정했다. 실제 Supabase schema/RLS 적용이나 production cross-user isolation 증거는 아니다.
- production secret policy 완료: TASK-112에서 `MEMBERSHIP-PRODUCTION-SECRET-POLICY.json`/`.md`와
  `scripts/membership_secret_policy_gate.py`를 추가해 user-owned LLM/SNS/OAuth/KIS token category,
  forbidden exposure, metadata-only response, redaction, lifecycle, audit, launch gate를 적용 전 policy로 고정했다.
  실제 secret storage 구현, secret read/write, OAuth/provider validation, KIS credential activation 증거는 아니다.
- production secret store implementation plan 완료: TASK-118에서
  `MEMBERSHIP-PRODUCTION-SECRET-STORE-IMPLEMENTATION-PLAN.json`/`.md`와
  `scripts/membership_secret_store_plan_gate.py`를 추가해 runtime/Edge Function secret lane,
  Supabase Vault or equivalent KMS lane, tenant metadata table, future write/rotate/disable/delete API boundary,
  staging tests를 적용 전 plan으로 고정했다. 실제 secret storage 구현, secret read/write, OAuth/provider
  validation, KIS credential activation, production DB apply, deploy 증거는 아니다.
- per-user engine/safety contract 완료: TASK-113에서 `MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json`/`.md`와
  `scripts/membership_engine_safety_gate.py`를 추가해 engine state, queue, kill switch, risk limit,
  circuit breaker, append-only order intent, order/execution log, notification scope, worker context를
  user_id 단위로 분리해야 한다는 적용 전 contract로 고정했다. 실제 OrderFlow, SafetyChecker, KIS broker,
  risk gate, production DB, deploy, live execution 변경은 아니다.
- Supabase staging field map 완료: TASK-116에서 `MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`/`.md`를 추가해
  membership, integration, payment evidence, portfolio, engine, trading, notification, audit surface를
  Supabase Auth owner field, RLS policy name, Data API exposure order, UPDATE `USING`/`WITH CHECK`,
  staging cross-user test, advisor checklist로 매핑했다. 실제 SQL migration, `schema.sql` 변경,
  Supabase project mutation, staging/prod DB apply는 아니다.
- staging deploy preflight checklist 완료: TASK-119에서 `MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`/`.md`와
  `scripts/membership_staging_deploy_preflight_gate.py`를 추가해 Vercel frontend, Railway backend, Supabase staging
  targets, env placeholder inventory, local checks, smoke plan, rollback plan, forbidden actions, launch gates를
  적용 전 checklist로 고정했다. TASK-120에서 `.env.example`와 sanitized env inventory gate를 추가해 local template
  blocker는 해소했다. TASK-121에서 Dockerfile `${PORT:-8000}` binding과 `/api/health` readiness gate를 추가해
  local Railway port/healthcheck blocker도 해소했다. TASK-122에서
  `MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json`/`.md`와
  `scripts/membership_staging_storage_decision_gate.py`를 추가해 external/member staging의 source of truth를
  Supabase Postgres/Auth/RLS로 고정하고 local vault, SQLite, Railway volume, runtime filesystem은 internal smoke
  또는 non-tenant artifact 보조로만 제한했다. 현재 actual deploy blocker는 external platform env write,
  Supabase staging project/migration/RLS/advisors/cross-user test 미적용, backup/restore review, KIS/payment external boundary다.
  실제 deploy, env write, public URL publication, Supabase migration/apply, secret/KIS/payment activation은 없다.
- Supabase staging migration/RLS review packet 완료: TASK-123에서
  `MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW.json`/`.md`와
  `scripts/membership_supabase_migration_review_gate.py`를 추가해 table groups, owner fields, authenticated grants,
  append-only rule, update `WITH CHECK` requirement, Data API review order, cross-user tests, rollback/apply review
  checklist를 local review packet으로 고정했다. 이는 migration file이나 executable SQL이 아니며, actual Supabase
  project selection, migration creation/apply, advisors, Data API grant review, live cross-user tests는 계속 Owner/R3이다.
- Supabase backup/apply evidence checklist 완료: TASK-124에서
  `MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json`/`.md`와
  `scripts/membership_supabase_apply_evidence_gate.py`를 추가해 future Owner/R3 apply lane의 backup/restore,
  apply log/status, advisors, Data API grant, cross-user, deploy-smoke prerequisite evidence를 고정했다. 이는
  actual Supabase project selection, migration/apply, backup download/restore, advisors, grant changes, deploy가 아니다.
- Owner-visible readiness surface sync 완료: TASK-126에서 `/api/membership/readiness`가 TASK-116~TASK-125 R2 증거물을
  pass 항목으로 표시하도록 갱신했다. Supabase schema/RLS, production secret storage, payment recognition,
  per-user engine/safety, KIS terms, external deploy는 계속 block/watch이며 `can_launch=false`를 유지한다.
- 관리자(Owner) 승인 화면 + 수동 입금 승인 플로우. 가입 시 계좌번호 안내 + 고유 입금코드 발급.
- 승인 상태머신: `requested → verification_pending → deposit_pending → active → expired/rejected`.
- 가입신청/입금대기 화면에는 가격, 입금 안내, 입금코드, 승인 대기 상태를 표시하되 실제 운영 계좌번호는 repo
  문서가 아니라 배포 환경 설정/관리자 설정에서 주입한다.
- 멀티테넌트화: `username_from_session()`의 단일 "owner" 전제 제거, 모든 데이터/엔진 루프/안전장치를
  user_id 단위로 격리. 유저별 KIS 키·LLM 토큰은 **유저 본인 입력·통제** 보관(평문 보관 최소화).
- SQLite → Supabase Postgres 마이그레이션. 로컬 vault 폐기/대체.
- 배포 구성: Vercel(web) + Railway(api+worker) + Supabase(db). 환경변수/시크릿 관리, 한국장 시간대 스케줄.
- 약관/고지: "투자자문·일임 아님, 모든 판단·결과 책임은 이용자", 수익보장 광고 금지(설문 동의와 연동).

제외:

- 우리가 종목을 추천/배포하거나 자동승인을 대신 운용하는 기능(법적 확인 전까지 **플래그로 잠금**).
- 가상계좌 PG 자동승인(판매 규모 커진 뒤 별도 태스크).
- 실주문 강제 ON, risk gate 완화, secret 커밋, 승인 없는 외부 배포.

## 완료 조건

- [ ] KIS 약관 + 법적 포지션(변호사/유권해석) 확인 결과가 기록되어 있다.
- [x] 미승인 로컬 계정은 기본값에서 자동가입/owner session 생성이 불가하다(TASK-099).
- [x] local prototype에서 가입신청/입금대기/Owner 승인 상태전이가 동작한다(TASK-100).
- [x] local Owner admin UI에서 가입신청 조회와 수동 승인 상태전이가 가능하다(TASK-101).
- [x] local prototype에서 관리자가 입금 확인 후 local member 계정과 subscription grant를 생성할 수 있다(TASK-102).
- [x] local prototype에서 입금코드/금액 기반 pasted statement recognition aid가 동작한다(TASK-103).
- [x] local prototype에서 member self-service와 Owner/admin global control 권한 경계가 분리되어 있다(TASK-104).
- [x] default login surface에서 guest/demo session issuance와 guest CTA가 차단되어 있다(TASK-105).
- [x] local prototype에서 product read API가 승인된 app user(owner/member) 전용으로 차단되어 있다(TASK-106).
- [x] local prototype에서 승인 사용자가 자기 LLM/SNS integration token status를 write-only/redacted로 관리할 수 있다(TASK-107).
- [x] Owner 화면/API에서 production readiness blocker가 명시적으로 보인다(TASK-108).
- [x] Supabase/RLS production contract asset과 local validation gate가 존재한다(TASK-109).
- [x] 신청자가 request id/contact로 상태와 deposit_pending 입금 안내를 확인할 수 있다(TASK-110).
- [x] payment evidence retention policy와 local validation gate가 존재한다(TASK-111).
- [x] payment recognition decision packet과 local validation gate가 존재한다(TASK-117).
- [x] production secret policy와 local validation gate가 존재한다(TASK-112).
- [x] production secret store implementation plan과 local validation gate가 존재한다(TASK-118).
- [x] per-user engine/safety contract와 local validation gate가 존재한다(TASK-113).
- [x] tenant-isolation route/surface/test matrix와 local validation gate가 존재한다(TASK-114).
- [x] Supabase staging schema/RLS/Data API field map이 존재한다(TASK-116).
- [x] staging deploy preflight checklist와 local validation gate가 존재한다(TASK-119).
- [x] sanitized staging env inventory와 `.env.example` safety gate가 존재한다(TASK-120).
- [x] Railway backend local `$PORT`/`/api/health` readiness gate가 존재한다(TASK-121).
- [x] persistent storage decision packet과 local validation gate가 존재한다(TASK-122).
- [x] Supabase staging migration/RLS review packet과 local validation gate가 존재한다(TASK-123).
- [x] Supabase backup/apply evidence checklist와 local validation gate가 존재한다(TASK-124).
- [x] Owner-visible readiness API가 완료된 R2 증거물과 남은 R3 blocker를 분리해 표시한다(TASK-126).
- [ ] production-ready 계정 활성화/subscription grant가 구현되어 있다.
- [ ] production에서 관리자가 입금 확인 후 해당 계정만 active 된다.
- [ ] 데이터/엔진/안전장치가 user_id 단위로 격리된다(단일 owner 전제 제거).
- [ ] production secret storage/RLS와 실제 user-owned provider execution adapter가 구현되어 있다.
- [x] 자동실행/추천 영업 기능은 기본 OFF 플래그로 잠겨 있다. (A2: `auto_exec_enabled()`·`recommendation_enabled()`·`advice_enabled()` 게이트, `flags.py` 기본 OFF/fail-closed; 전체 스위트 1704 PASS)
- [ ] Vercel + Railway + Supabase 스테이징 배포가 동작한다(프로덕션 배포는 Owner 승인 후).

## 다음 단계(제안)

1. KIS OpenAPI 약관 확인 + 변호사 질문 리스트 작성(Compliance Officer / Research Agent).
2. member read scope and Owner/admin API boundary decision record.
3. Owner/R3 Supabase staging project selection, migration creation/apply, backup/restore, advisors, Data API grant review, and cross-user tests.
4. Owner/R3 Vercel/Railway/Supabase external env write and staging deploy smoke.
5. production secret storage, payment evidence retention/refund/receipt/tax, KIS terms, and per-user engine/safety implementation review.
6. 새 local R2 후보는 현재 식별되지 않았다. 실제 apply/deploy/secret/payment/KIS/order/risk/prod boundary는 Owner/R3 승인 전 금지한다.

## BUCKET A 클로즈아웃 (R2 production-readiness 코드)

브랜치: `feat/task087-membership-prod-r2`  
완료 시각: 2026-06-27T03:40:18+09:00  
검증: 전체 스위트 1704 PASS · web lint/build GREEN · security/RLS/secret 리뷰 Approved · Opus 전체 브랜치 리뷰 "env-doc 수정 후 ready" — 수정 완료

| 서브태스크 | 내용 | 상태 |
|-----------|------|------|
| A1 | `app/services/flags.py` — 중앙 env 피처-플래그 모듈, 전체 기본 OFF/fail-closed | 완료 |
| A2 | 기본 OFF 락: 자동매매 `auto_exec_enabled()` 킬스위치 우선, 추천/조언 OUTPUT 엔드포인트 `recommendation_enabled()`/`advice_enabled()` 게이트 | 완료 |
| A3 | SSO 역할 하드닝: "allowlisted 이메일=owner" 구멍 폐쇄 → owner(`AUTOFOLIO_OWNER_EMAIL`)/member(승인)/deny, fail-closed | 완료 |
| A4 | `supabase/migrations/*.sql` — membership+trading 마이그레이션 파일 + RLS (미적용; trading 테이블 nullable user_id; apply-time service_role 계약 supabase/README.md) | 완료 |
| A5/A6 | 메타데이터 전용 secret-store 어댑터(`secret_store.py`, vault-backed + inert Supabase stub) + 존재 확인 전용 env 로더(`runtime_config.py`); `integrations.py` 라우팅 | 완료 |
| A7 | 배포 설정(`web/vercel.json`, `railway.json`, preflight CI) + `web/DEPLOY-NOTES.md`. 실제 deploy/secret 없음 | 완료 |
| env-doc | `.env.example`에 신규 플래그 5개 문서화, readiness + runtime_config presence에 노출 | 완료 |

**검증 증거:** 전체 스위트 1704 PASS · web lint/build GREEN · security/RLS/secret/Opus 리뷰 전부 Approved.

## 남은 작업

### BUCKET B — 외부 배포 (Owner/R3 게이트, 이 브랜치 범위 밖)

- **Supabase 프로젝트 선택** — `tag_manual`의 STAR-TEAM 프로젝트 재사용 금지(⚠); 별도 staging 프로젝트 필요.
- 마이그레이션 apply, Supabase RLS/Advisors/Data API grant, cross-user 격리 테스트.
- 플랫폼 env/secrets 설정 (Vercel + Railway + Supabase).
- Vercel + Railway + Supabase 스테이징 배포 스모크.
- 운영 주의: `AUTOFOLIO_OWNER_EMAIL`이 런타임 env에 설정되지 않으면 SSO owner 로그인 403(by design). 배포 전 반드시 설정.

### BUCKET C — KIS/법적/운영 (Owner/외부 게이트)

- KIS OpenAPI 상업적 이용 약관 확인.
- 핀테크 변호사 + 금감원 비조치의견서/유권해석 ("SW 판매 vs 유사투자자문" 경계).
- 사업자등록 + 통신판매업 신고.
- 결제/프라이버시 운영(manual bank-app 확인 → PG/오픈뱅킹 업그레이드 path).

### INIT-MULTITENANT-ENGINE (분리 등록)

멀티테넌트 엔진 격리(원래 A8)는 안전 임계 변경(~44파일/1200-1500 LOC)이므로
`INIT-MULTITENANT-ENGINE` 이니셔티브로 분리 등록됨. `AUTOFOLIO_MULTI_TENANT_ENABLED`
플래그로 기본 OFF 게이팅. 4단계 시퀀스 필요 — 상세는 `agents/project/initiatives/INIT-MULTITENANT-ENGINE.md` 참조.

## 비고

- 동일 세션에서 동시 작업 중인 다른 Autofolio 세션 존재(작업 트리에 다수 동시 변경). 충돌 주의.
- 본 태스크는 Owner 대화 기록 기반 등록이며, 실제 착수는 위 선행 확인(특히 법적/약관) 이후.

## INIT-MULTITENANT-ENGINE 코드 완료 기록 (2026-06-27T15:28:04+09:00)

`INIT-MULTITENANT-ENGINE` 이니셔티브(앱↔per-user 배선) **코드 완료**. Phases 1-4 전부 머지됨
(PRs #127 / #128 / #129 / #130). 전체 pytest **1766 passed / 0 failed**.
`AUTOFOLIO_MULTI_TENANT_ENABLED` 플래그는 모든 환경에서 **OFF 유지**
(`agents/project/MULTITENANT-FLAG-ENABLE-READINESS.md` 준비 항목 + Owner 명시 승인 전까지).

이에 따른 앱-티어 배포 잔여 선결 조건은 다음 세 가지로 정리된다:

1. **SQLite → Supabase Postgres 백엔드 스왑** — 로컬 SQLite/vault를 `autofolio-staging` Supabase로
   전환하는 코드 레이어(앱 연결 배선). Railway/Render 배포 전 필수.
2. **백엔드 호스트** — Railway(또는 Render) 외부 계정 env/secret 설정 + 배포 스모크. 외부 계정
   접근권이 없어 자율 진행 불가(Owner/R3 게이트).
3. **Flag-ON 준비 항목 + Owner 승인** — `MULTITENANT-FLAG-ENABLE-READINESS.md` 기재 항목 클리어
   후 Owner 명시 결정 필요.

BUCKET C(KIS 약관 · 비조치의견서 · 사업자등록 · 결제/개인정보)는 변동 없이 Owner/외부 게이트 유지.

## BUCKET B 진행 — Supabase staging 적용 (2026-06-27T11:19:52+09:00)

Owner 승인(신규 프로젝트 + mock 스테이징 자동실행) 하에 BUCKET B의 DB 티어를 실행:
- 신규 Supabase 프로젝트 `autofolio-staging`(`rpdophwfgrwctaochewf`, ap-northeast-2) 생성.
  기존 INACTIVE STAR-TEAM 프로젝트(`xkkbgjvywtbwyaoyvwmq`)는 비파괴(미접촉).
- `supabase/migrations/0001~0003` 적용 → 22 테이블 / 33 RLS 정책 / RLS 미적용 0 / 보안 advisors 0 lints.
- 증거·잔여 런북: `agents/project/MEMBERSHIP-STAGING-DEPLOY-EVIDENCE.md`.
- 잔여(앱 티어): 백엔드 호스트(Railway/Render — 외부 계정), 앱↔Supabase 배선(= INIT-MULTITENANT-ENGINE),
  Vercel `web/` 배포. 공개 상용 런칭은 BUCKET C(법률) 게이트. `can_launch=false` 유지.
- secret 미커밋(공개 URL/anon만). KIS_ENV=mock. 실주문/결제 없음.

## Postgres DB-Layer 호환 + Multitenant Readiness 마감 (2026-06-27T18:13:55+09:00)

PRs #132–#135 (이번 세션 추가 5건 포함 전체 12건: #124–#135) 완료 — 전체 pytest **1833 passed / 0 failed**.

### 완료 항목

| PR | 내용 | 검증 |
|----|------|------|
| #132 | `app/database/pg_db.py` config-gated Postgres 어댑터 (`DATABASE_URL`; 기본 SQLite 동일; psycopg optional) | pytest 통과 |
| #133 | SQL 방언 호환 — boolean/KST-date/ON CONFLICT 포터블 + `supabase/migrations/0004_aux_tables.sql` | MCP live-verified vs `autofolio-staging` (whitelist + system_state-global + boolean upsert) |
| #134 | Multitenant flag-ON 준비 — owner-only per-user re-enable/status 엔드포인트 + `_user_ctx`/`_user_run_locks` TTL/LRU 한정 + ghost-lock TOCTOU 수정. 전부 flag-gated | pytest 통과 |
| #135 | `investor_profile.py` PG 준비 (PG 환경에서 SQLite table-init 스킵) | MCP live-verified (investor_profiles upsert + checkin RETURNING on real PG) |

`MULTITENANT-FLAG-ENABLE-READINESS.md` 항목 (a)(b)(d) → **COMPLETE**.

### 잔여 (Owner/외부 게이트 — 자율 진행 불가)

- **(c) 유저별 브로커/KIS 자격증명**: 실제 per-user KIS app-key/secret/계정번호가 필요 = Owner 시크릿.
- **앱↔Supabase 라이브 psycopg 연결**: DB 비밀번호(`DATABASE_URL`) = Owner 배포 시 시크릿.
- **백엔드 호스트 Railway/Render**: 외부 계정 접근 = Owner/R3 게이트.
- **Flag-ON 활성화** (`AUTOFOLIO_MULTI_TENANT_ENABLED=1`): 위 항목 + Owner 안전 승인 결정 필요.
- **BUCKET C 법무**: KIS 상용 약관 · 비조치의견서 · 사업자등록 · 결제/개인정보 — 외부 인간 작업.

`can_launch=false` 유지. `DATABASE_URL` 기본 미설정(SQLite). 플래그 기본 OFF.
