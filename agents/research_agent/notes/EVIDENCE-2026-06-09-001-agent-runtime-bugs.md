---
type: evidence
id: EVIDENCE-2026-06-09-001
status: 완료
author: Research Agent
created: 2026-06-09
created_at: 2026-06-09T22:11:08+09:00
tags: [bug, agent_runtime, upstream, encoding, api-misuse, false-positive]
scope: agent_runtime v0.1.8 버그 3건 — 원인 분석·출처·재현 경로
applies_to: [agent_runtime upstream, Autofolio host]
---

# EVIDENCE-2026-06-09-001 — agent_runtime v0.1.8 버그 3건 분석

> Research Agent 작성. 결정·우선순위·수정 방향은 Lead Engineer 소관.

---

## BUG-001: `AttributeError: 'AgentRuntimeConfig' object has no attribute 'exists'`

### 육하원칙

| 항목 | 내용 |
|------|------|
| **누가(Who)** | `agent_runtime.sync.build_sync_plan()` 호출자 (Autofolio 호스트, lock 재생성 시도) |
| **무엇을(What)** | `build_sync_plan(root, cfg)` 2인자 호출 → `cfg`(`AgentRuntimeConfig`)를 `template_root: Path`로 받아 `.exists()` 호출 → AttributeError |
| **언제(When)** | 2026-06-09 v0.1.5→v0.1.8 업그레이드 중, lock 파일 재생성 시도 시 |
| **어디서(Where)** | `agent_runtime/sync.py:90` → `_template_files(resolved_template_root):42` |
| **왜(Why)** | v0.1.8에서 `build_sync_plan` 시그니처가 **`(root: Path, template_root: Path \| None = None)`** 으로 변경됐는데, 호출부(Autofolio 수동 lock 스크립트)가 v0.1.5 관례인 `build_sync_plan(root, config)` 로 호출 — **공개 API 시그니처 변경에 대한 마이그레이션 가이드 없음** |
| **어떻게(How)** | `load_config(root)` → `AgentRuntimeConfig` 반환 → `build_sync_plan(root, cfg)` 전달 → 내부에서 `cfg.exists()` 호출 → AttributeError |

### 근본원인
`build_sync_plan`은 내부에서 `load_config`를 자체 호출한다. 호출자가 별도로 `load_config` 후 결과를 `build_sync_plan`에 전달하는 것은 **올바르지 않은 API 사용**이다. 그러나:
- 공개 API 문서(`README.md`, `AGENT_RUNTIME.md`)에 이 점이 명시되지 않음
- v0.1.5→v0.1.8 마이그레이션 가이드(CHANGELOG, MIGRATION-COMPAT-MAP)가 배포되지 않아 호출자가 시그니처 변경을 알 수 없었음

### 재현 코드
```python
from agent_runtime.sync import build_sync_plan, load_config
from pathlib import Path
cfg = load_config(Path('.'))
build_sync_plan(Path('.'), cfg)  # AttributeError: 'AgentRuntimeConfig' has no attribute 'exists'
```

### 올바른 호출
```python
from agent_runtime.sync import build_sync_plan
from pathlib import Path
plan = build_sync_plan(Path('.'))  # template_root 미지정 → default_template_root() 사용
```

### 영향
- lock 파일 재생성 스크립트 실패 → 수동으로 ref/version만 패치하는 우회 필요
- **업스트림 책임**: 시그니처 변경 시 CHANGELOG/MIGRATION 필수

---

## BUG-002: `UnicodeEncodeError: 'cp949'` — Windows 콘솔에서 sync diff 출력 불가

### 육하원칙

| 항목 | 내용 |
|------|------|
| **누가(Who)** | `agent_runtime.sync.main()` + `render_diff()` + `print()` — Windows cp949 콘솔 |
| **무엇을(What)** | `sync --diff` 실행 시 `—`(em-dash U+2014) 등 BMP 비ASCII 문자가 diff 출력에 포함 → `sys.stdout`(cp949) 인코딩 에러로 스택트레이스 |
| **언제(When)** | 2026-06-09 v0.1.8 sync --diff 실행 시 |
| **어디서(Where)** | `agent_runtime/sync.py:215` `print(render_diff(plan))` — `main()` 함수 |
| **왜(Why)** | `_diff_update()`가 `difflib.unified_diff()` 결과를 그대로 `print()` 전달. 대상 파일(`REPORTING-FORMAT.md` 등)에 em-dash(—) 포함 → cp949 인코딩 불가 |
| **어떻게(How)** | `render_diff` 반환값(str)을 `print()`가 `sys.stdout.write()` → cp949 codec가 U+2014 변환 불가 → `UnicodeEncodeError` |

### 근본원인
`sync.py:215` `print(render_diff(plan))` 에 인코딩 핸들링 없음. Windows 기본 콘솔(cp949/cp932)은 UTF-8 파일 내 비ASCII를 `print()` 직접 전달 시 에러. `errors='replace'` 또는 `PYTHONIOENCODING=utf-8` 없이 동작 불가.

### 재현
```powershell
# Windows cp949 콘솔에서
python -c "from agent_runtime.sync import main; import sys; sys.argv=['sync','--diff','--root','.']; main()"
# UnicodeEncodeError: 'cp949' codec can't encode character '—' in position 2302
```

### 우회
```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```
또는 환경변수 `PYTHONIOENCODING=utf-8`.

### 영향
- Windows 사용자 전체 영향 — `sync --diff` 명령이 정상 실행 불가
- **업스트림 버그**: `sync.py main()`에 Windows 콘솔 인코딩 처리 필요

---

## BUG-003: `check_merge_policy_precedence.py` — precedence swap 완료 후 false positive `exit 1`

### 육하원칙

| 항목 | 내용 |
|------|------|
| **누가(Who)** | Autofolio 호스트 스크립트 `scripts/check_merge_policy_precedence.py` |
| **무엇을(What)** | v0.1.8 upgrade + 수동 §4-4 병합 완료 후에도 스크립트가 "ACTION REQUIRED — 교체 필요" + `exit 1` 반환 |
| **언제(When)** | 2026-06-09 v0.1.8 upgrade 완료 직후 |
| **어디서(Where)** | `scripts/check_merge_policy_precedence.py` — `upstream_has_section_35()` 감지 후 항상 `exit 1` |
| **왜(Why)** | 스크립트 설계 시 "업스트림 §3.5 출현 = 교체 필요"만 처리, "이미 교체 완료" 상태를 추적하지 않음. 완료 마커 파일/플래그 없음 |
| **어떻게(How)** | `MERGE-POLICY.md` 상태가 "ADDENDUM"으로 갱신됐지만 스크립트가 읽지 않음 → 업스트림 §6 감지만 보고 exit 1 |

### 근본원인
상태 머신 부재: "감지 필요" / "교체 완료" / "교체 불필요" 3상태 중 "교체 완료" 상태를 표현하는 방법이 없음. 로컬 버그.

### 수정 방향
`MERGE-POLICY.md` 앞 단어로 `ADDENDUM` 감지 시 "이미 완료" → `exit 0`. 또는 `.merge-policy-swapped` 마커 파일.

---

## 요약 (우선순위)

| ID | 버그 | 소속 | 심각도 | 상태 |
|----|------|------|--------|------|
| BUG-001 | build_sync_plan API 시그니처 변경 미문서화 | upstream agent_runtime | Medium | 재현됨 |
| BUG-002 | Windows cp949 UnicodeEncodeError | upstream agent_runtime | High | 재현됨 |
| BUG-003 | precedence check false positive exit 1 | Autofolio host | Low | 수정 예정 |

**BUG-001/002는 upstream Issue + PR 대상. BUG-003은 host 수정.**

### 출처·참조
- 재현 세션: 2026-06-09T19:xx–22:11+09:00 (feat/agent-runtime-v0.1.8-upgrade 브랜치 작업)
- 재현 코드: 이 문서 §BUG-001/002 코드블록
- upstream 코드: `agent_runtime/sync.py:42,90,187,215` (pip installed v0.1.8)
- Autofolio 코드: `scripts/check_merge_policy_precedence.py`
- 관련 PR: [Autofolio #3](https://github.com/ycpiglet/autofolio/pull/3) (v0.1.8 upgrade)
