---
type: evidence
id: EVIDENCE-2026-06-19-007
title: Membership KIS commercial and multi-user Open API terms review
created_at: 2026-06-19T22:16:54+09:00
owner: Research Agent
related_task: TASK-125
tags: [membership, kis, open-api, terms, compliance, staging]
status: pass
redaction: no secrets, no KIS credentials, no account numbers, no customer data, no external contact
---

# Membership KIS Commercial And Multi-user Open API Terms Review

## Question

Can Autofolio safely proceed toward paid external/member staging with user-owned
KIS integrations, or does the KIS Open API surface require Owner/KIS/legal
confirmation first?

## Sources Checked

Official sources:

- KIS Developers 제휴안내:
  https://apiportal.koreainvestment.com/provider
- KIS Developers 제휴 API 시작하기:
  https://apiportal.koreainvestment.com/provider-doc1
- Korea Investment & Securities eFriend Expert Open API service page:
  https://securities.koreainvestment.com/main/customer/systemdown/OpenAPI.jsp
- Korea Investment & Securities notice for the 2025-06-04 affiliate user terms:
  https://m.koreainvestment.com/main/customer/notice/Notice.jsp?cmd=TF04ga000002&num=44503
- Full Open API service terms PDF for affiliate institution users:
  https://file.koreainvestment.com/updata/namo/09101613%EC%98%A4%ED%94%88API%EC%84%9C%EB%B9%84%EC%8A%A4%EC%9D%B4%EC%9A%A9%EC%95%BD%EA%B4%80_%EC%A0%84%EB%AC%B8.pdf
- FSC/FSS legal interpretation portal, robo-advisor investment-advice question:
  https://better.fsc.go.kr/fsc_new/replyCase/LawreqDetail.do?lawreqIdx=3790&muGpNo=75&muNo=85&stNo=11

## Findings

1. KIS self-owned account material does not prove paid hosted-service clearance.
   The eFriend Expert page describes a customer directly using KIS servers for
   their own algorithm/program, with account and HTS-service prerequisites.

2. Third-party service provision is a separate KIS Developers partnership
   surface. KIS provider guidance describes use of KIS Developers Open API for
   third-party services as a partnership context and calls out capital-markets
   business-scope review.

3. Market-data display is not automatically cleared. KIS provider guidance
   warns that KRX and overseas exchange information-use agreements may be
   required for partner-branded app/screen use.

4. Order API is high-risk for a non-institution software service. KIS provider
   guidance asks parties wanting order API use to check institutional
   finance/investment-discretionary status and notes that non-institution
   workflows can be difficult.

5. The affiliate user terms assume an approved company/institution path. The
   terms define an 이용기관 as a company that has an Open API use contract and
   KIS approval; linked financial service uses a user's Open API authority.

## Applied Repo Decision

- Add `MEMBERSHIP-KIS-COMMERCIAL-TERMS-REVIEW-PACKET.json`/`.md`.
- Keep KIS production/member integration blocked until Owner/KIS/legal
  confirmation exists.
- Keep `KIS_ENV=mock` for external/member staging and do not claim paid KIS
  production integration in marketing.

## Uncertainties

- Whether user-provided personal KIS keys in a paid hosted service still count
  as third-party service or partnership use.
- Whether a local/user-run software distribution changes the KIS terms analysis.
- Exact KRX/overseas market-data rights needed for member-facing screens.
- Exact order API model allowed when the user retains every approval and risk
  control.
