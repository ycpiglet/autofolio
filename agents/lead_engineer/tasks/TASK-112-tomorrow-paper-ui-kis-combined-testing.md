---
type: task
id: TASK-112
display_id: TASK-112
task_uid: 1d8f3a64-9c20-47e5-b6a1-2f70c9e4a5b3
registered_at: 2026-06-19T17:29:42+09:00
created_at: 2026-06-19T17:29:42+09:00
updated_at: 2026-06-19T17:29:42+09:00
status: 대기
owner: Lead Engineer
assignees: [Lead Engineer, KIS API Engineer, UI/UX Designer, QA]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 120000
tags: [kis, paper, ui, playwright, tomorrow-runbook, orderbook, combined-test]
gate: 정규장(09:00~15:20 KST)에서만; paper 우선; 실계좌 실주문은 Owner 명시 확인 + 캡 스크립트로만
trigger_meeting: Owner direct request 2026-06-19
deferred_until: 2026-06-20 정규장 시작(09:00 KST) 또는 다음 개장일
scheduler_ref: 내일 09:05 KST 스케줄 트리거(09:00 개장 직후)
created: 2026-06-19
---

# TASK-112 (내일 런북) 모의 UI + KIS 기능 복합 테스트

작업 ID: TASK-112
상태: 대기 (내일 정규장 시작 시 착수)
Owner: Lead Engineer
요청자: Owner
의도: TASK-111에서 검증한 매매 흐름 위에, **UI에서 KIS 실시간 기능을 유저처럼 복합 조작**해 검증한다(호가/시세/포트폴리오/내역 등). 실주문은 캡 스크립트로만.

## 왜 내일인가
오늘(2026-06-19) 17:29 KST 시점 정규장 마감(15:30) 이후라 KIS 시세/주문이 막힘. 모의/실계좌 라이브 동작은 **정규장(09:00~15:20)** 에서만 의미 있음.

## 착수 전 환경 셋업 (오늘 학습 반영 — 그대로 재현)
1. paper 전용 백엔드(격리 DB) 기동:
   `KIS_ENV=paper DB_PATH=.autofolio/uitest_paper.db .venv/Scripts/python.exe -m uvicorn app.api.main:create_app --factory --host 127.0.0.1 --port 8009`
2. 프런트는 **프로덕션 빌드**로(dev는 HMR 웹소켓 실패로 하이드레이션 깨짐). `API_INTERNAL_URL`을 **빌드에 baked**:
   `API_INTERNAL_URL=http://127.0.0.1:8009 npm --prefix web run build`
   `API_INTERNAL_URL=http://127.0.0.1:8009 npm --prefix web run start -- -p 3009`
3. 검증: `curl http://127.0.0.1:3009/api/profile/survey` → version `investor-profile-v2`면 8009로 정상 프록시.
4. 로그인 `uitest / uitest1234`(자동 owner, 격리 DB에 프로필 이미 완료). 미완료면 API로 설문 제출(signature는 dict: name+confirmation_text="위 항목을 모두 이해했습니다."+data:image/png;base64 ≥120자+signed_at).

## 테스트 항목 (paper, 유저처럼 UI 조작)
- [ ] 매매: 종목검색→매수/매도→목표가/수량→조건 등록→새로고침 지속(TASK-111 회귀).
- [ ] 호가(KIS 실시간): /trade 우측 "호가 조회 종목"에 `005930` 입력→호가 ladder 렌더 확인.
- [ ] 시세/포트폴리오: /home, /portfolio KPI·보유·차트 로드.
- [ ] 내역: /history 조건/주문 내역.
- [ ] 분석/에이전트: /analysis, /agents 렌더 + 제안→/trade prefill 흐름.
- [ ] 엔진 1회 실행(모의): "엔진 1회 실행"으로 조건 평가(모의, 가상자금).
- [ ] 안전장치 UI: 킬스위치/자동매매 토글 표시·동작.

## 실계좌(실주문) — Owner 확인 필수
- 필요 시에만, **캡 스크립트**로: `! .venv/Scripts/python.exe scripts/pp.py` (읽기전용 플랜) → 종목/수량/예상금액 확인 → `! .venv/Scripts/python.exe scripts/pp.py EXECUTE-REAL` (≤5주·≤5,000원·자동청산).
- 자동매매 ON, risk gate 약화, UI에서 실계좌 직접 실주문은 금지(자동청산 안전장치 없음).

## 완료 조건
- [ ] paper UI 복합 시나리오가 정규장에서 통과하고 결과가 EVIDENCE로 기록된다.
- [ ] 발견된 UI/KIS 결함은 별도 TASK로 등록된다.
- [ ] 실주문을 했다면 캡 스크립트 결과(JSON)가 증거로 남고 잔여 포지션 0이 확인된다.

## 비고
- 끝나면 백그라운드 서버(8009/3009) 정리.
- 동시 세션 다수 가동 가능 — 포트/DB 격리 유지.
- 연계: TASK-111(오늘 검증), 메모리 `playwright-prod-mode-verify`.
