---
type: task
id: TASK-016
status: 열림
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 중
est_hours: 4
est_tokens: 50000
tags: [kis, fundamental, research]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-016 KIS 기업 재무정보 (PER·PBR·EPS·시가총액)

작업 ID: TASK-016
상태: 열림
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

Research Agent가 종목을 분석할 때 PER·PBR·EPS·시가총액 등 기본 재무 지표를 KIS에서 직접 수신하면 외부 API 의존 없이 밸류에이션 근거를 확보할 수 있다. `inquire-price` 응답에 per, pbr, eps, hts_avls 필드가 포함되어 있으나 현재 파싱되지 않고 있다.

## 구현 범위

- `inquire-price` 응답의 미파싱 필드 추출: per, pbr, eps, hts_avls(시가총액)
- `inquire-finance-ratio` 엔드포인트 별도 호출 구현
- `KisClient.get_fundamental(symbol)` 메서드로 통합 제공
- Research Agent 프롬프트/컨텍스트 빌더에 재무 데이터 주입 경로 추가
- 분석 화면 종목 상세 패널에 재무 지표 표시

## 완료 기준

- [ ] `get_fundamental()` 구현 및 단위 테스트
- [ ] per/pbr/eps/hts_avls 파싱 검증 (실제 응답 샘플 기반)
- [ ] Research Agent 컨텍스트 빌더 연결 확인
