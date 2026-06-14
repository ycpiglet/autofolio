---
type: task
id: TASK-065
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: Medium
difficulty: 낮
est_hours: 2
est_tokens: 12000
tags: [ops, logging, maintenance]
gate: -
trigger_meeting: 다음 사이클
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-065 feat: 로그 로테이션 구현 (logger.py)

작업 ID: TASK-065
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: logger.py FileHandler를 RotatingFileHandler로 교체하고 절대 경로 사용
대상: app/utils/logger.py (또는 로거 설정 파일)
방법: RotatingFileHandler(10MB×5) 교체 + 프로젝트 루트 기준 절대 경로 적용 + 기존 구조화 로깅 동작 유지 확인
감사 로그: AUDIT-2026-06-14-001

## 배경

`logger.py`가 `FileHandler`를 사용하여 `trading_app.log`와 `events.jsonl`이 무한 증가.

**위험**: 장기 운영 시 디스크 공간 소진 가능. 현재 CWD 의존 경로로 실행 위치에 따라 로그 파일 위치가 달라짐.

## 수정 방향

1. `FileHandler` → `RotatingFileHandler` 교체:
   ```python
   from logging.handlers import RotatingFileHandler
   handler = RotatingFileHandler(
       log_path,
       maxBytes=10 * 1024 * 1024,  # 10MB
       backupCount=5
   )
   ```
2. 로그 경로를 CWD 의존 대신 프로젝트 루트 기준 절대 경로로 변경:
   ```python
   BASE_DIR = Path(__file__).resolve().parent.parent.parent
   LOG_DIR = BASE_DIR / "logs"
   ```
3. `events.jsonl`도 동일하게 RotatingFileHandler 적용
4. 기존 구조화 로깅 동작 유지 확인

## 완료 기준

- RotatingFileHandler 적용 (10MB × 5 순환)
- 절대 경로 로그 위치
- 기존 구조화 로깅 동작 유지

## Done When

- RotatingFileHandler 적용
- 절대 경로 로그 위치
- 기존 구조화 로깅 동작 유지

## 완료 기록

완료 시각: 2026-06-14T17:09:06+09:00
검토자: Backend Engineer / QA

실측 비용 (시간): ~0.4h (subagent)
실측 비용 (LLM 토큰): ~130k (subagent)

## 증거

- `app/common/logger.py`: `FileHandler` → `RotatingFileHandler(maxBytes=10*1024*1024, backupCount=5)`.
  - `BASE_DIR = Path(__file__).resolve().parents[2]` (app/common/logger.py → app/common → app → repo root).
  - `LOG_DIR = BASE_DIR / "logs"` — 절대 경로, CWD 무관.
  - `trading_app.log` (get_logger) + `events.jsonl` (get_structured_logger) 모두 RotatingFileHandler 적용.
- `tests/unit/test_log_rotation.py` (신규): RotatingFileHandler 타입 검증, maxBytes=10MB, backupCount=5, 절대 경로, logs/ 디렉토리 검증 — 9개 테스트.
- 수정 전: `test_file_handler_is_rotating` FAILED (FileHandler, not RotatingFileHandler).
- 수정 후: 9 passed (test_log_rotation.py), 702 passed (전체).

## 리뷰

- `RotatingFileHandler`는 `FileHandler`의 서브클래스이므로 기존 `isinstance(h, FileHandler)` 검사는 여전히 통과.
- `LOG_DIR.mkdir(parents=True, exist_ok=True)` — 모듈 임포트 시 로그 디렉토리 자동 생성.
- 기존 `_JsonLinesFormatter`, `log_event()`, 로그 포맷/레벨 변경 없음.

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`
