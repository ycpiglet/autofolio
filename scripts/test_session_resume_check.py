"""Unit tests for session_resume_check pure functions (crash-recovery auditor).

All tests run against tmp_path temp dirs and pass explicit `now` floats for
determinism. They never touch the real repo runtime dirs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_resume_check as src  # noqa: E402


# --- helpers ---

def _write_claim(claims_dir: Path, name: str, *, expires_at, pid=1234,
                 message_id=None) -> Path:
    claims_dir.mkdir(parents=True, exist_ok=True)
    path = claims_dir / name
    payload = {
        "message_id": message_id or name.replace(".claim", ""),
        "pid": pid,
        "expires_at": expires_at,
        "path": message_id or name.replace(".claim", ""),
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _write_message(inbox_dir: Path, name: str, *, status: str,
                   message_id: str) -> Path:
    inbox_dir.mkdir(parents=True, exist_ok=True)
    path = inbox_dir / name
    text = (
        "---\n"
        f"id: {message_id}\n"
        "from: lead-engineer\n"
        "to: qa\n"
        f"status: {status}\n"
        "---\n\n"
        "body text\n"
    )
    path.write_text(text, encoding="utf-8")
    return path


def _write_session(sessions_dir: Path, agent_id: str, *, status: str,
                   started_at: str, role="qa", task_id="TASK-001") -> Path:
    sessions_dir.mkdir(parents=True, exist_ok=True)
    path = sessions_dir / f"{agent_id}.json"
    payload = {
        "agent_id": agent_id,
        "role": role,
        "task_id": task_id,
        "status": status,
        "started_at": started_at,
        "stopped_at": None,
        "context_packet": {},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# --- scan_stale_claims ---

def test_scan_stale_claims_fresh_not_flagged(tmp_path):
    now = 1000.0
    claims = tmp_path / "claims"
    _write_claim(claims, "MSG-fresh.claim", expires_at=now + 600)
    (claims / ".gitkeep").parent.mkdir(parents=True, exist_ok=True)
    (claims / ".gitkeep").write_text("", encoding="utf-8")
    out = src.scan_stale_claims(claims, now)
    assert out == []


def test_scan_stale_claims_past_is_flagged(tmp_path):
    now = 1000.0
    claims = tmp_path / "claims"
    _write_claim(claims, "MSG-old.claim", expires_at=now - 120, pid=77)
    out = src.scan_stale_claims(claims, now)
    assert len(out) == 1
    entry = out[0]
    assert entry["file"] == "MSG-old.claim"
    assert entry["pid"] == 77
    assert entry["age_seconds"] == 120
    assert entry["age_seconds"] > 0


def test_scan_stale_claims_ignores_gitkeep(tmp_path):
    now = 1000.0
    claims = tmp_path / "claims"
    claims.mkdir(parents=True, exist_ok=True)
    (claims / ".gitkeep").write_text("", encoding="utf-8")
    out = src.scan_stale_claims(claims, now)
    assert out == []


# --- scan_claimed_stale_messages ---

def test_scan_claimed_stale_messages_flags_missing_claim(tmp_path):
    now = 1000.0
    inbox = tmp_path / "inbox"
    claims = tmp_path / "claims"
    claims.mkdir(parents=True, exist_ok=True)
    _write_message(inbox, "MSG-a.md", status="claimed", message_id="MSG-a")
    out = src.scan_claimed_stale_messages(inbox, claims, now)
    assert len(out) == 1
    assert out[0]["message_id"] == "MSG-a"
    assert out[0]["reason"] == "missing-claim"


def test_scan_claimed_stale_messages_flags_stale_claim(tmp_path):
    now = 1000.0
    inbox = tmp_path / "inbox"
    claims = tmp_path / "claims"
    _write_message(inbox, "MSG-b.md", status="claimed", message_id="MSG-b")
    _write_claim(claims, "MSG-b.claim", expires_at=now - 60, message_id="MSG-b")
    out = src.scan_claimed_stale_messages(inbox, claims, now)
    assert len(out) == 1
    assert out[0]["message_id"] == "MSG-b"
    assert out[0]["reason"] == "stale-claim"


def test_scan_claimed_stale_messages_open_not_flagged(tmp_path):
    now = 1000.0
    inbox = tmp_path / "inbox"
    claims = tmp_path / "claims"
    claims.mkdir(parents=True, exist_ok=True)
    _write_message(inbox, "MSG-open.md", status="open", message_id="MSG-open")
    out = src.scan_claimed_stale_messages(inbox, claims, now)
    assert out == []


def test_scan_claimed_stale_messages_fresh_claim_not_flagged(tmp_path):
    now = 1000.0
    inbox = tmp_path / "inbox"
    claims = tmp_path / "claims"
    _write_message(inbox, "MSG-c.md", status="claimed", message_id="MSG-c")
    _write_claim(claims, "MSG-c.claim", expires_at=now + 600, message_id="MSG-c")
    out = src.scan_claimed_stale_messages(inbox, claims, now)
    assert out == []


# --- scan_dead_sessions ---

def test_scan_dead_sessions_missing_dir_returns_empty(tmp_path):
    out = src.scan_dead_sessions(tmp_path / "nope", 1000.0, 3600.0)
    assert out == []


def test_scan_dead_sessions_old_active_flagged(tmp_path):
    sessions = tmp_path / "sessions"
    # started_at far in the past relative to now_iso reference
    _write_session(sessions, "agent_aaaaaaaaaaaa", status="active",
                   started_at="2000-01-01T00:00:00+09:00")
    # now epoch well after 2000
    now = 4_000_000_000.0
    out = src.scan_dead_sessions(sessions, now, max_age_seconds=3600.0)
    assert len(out) == 1
    assert out[0]["agent_id"] == "agent_aaaaaaaaaaaa"
    assert out[0]["status"] == "active"
    assert out[0]["age_seconds"] > 3600.0


def test_scan_dead_sessions_recent_active_not_flagged(tmp_path):
    sessions = tmp_path / "sessions"
    # build started_at very close to now epoch
    import datetime as dt
    now = 1_700_000_000.0
    started = dt.datetime.fromtimestamp(now - 60, dt.timezone.utc).isoformat()
    _write_session(sessions, "agent_bbbbbbbbbbbb", status="active",
                   started_at=started)
    out = src.scan_dead_sessions(sessions, now, max_age_seconds=3600.0)
    assert out == []


def test_scan_dead_sessions_stopping_not_flagged(tmp_path):
    sessions = tmp_path / "sessions"
    _write_session(sessions, "agent_cccccccccccc", status="stopping",
                   started_at="2000-01-01T00:00:00+09:00")
    now = 4_000_000_000.0
    out = src.scan_dead_sessions(sessions, now, max_age_seconds=3600.0)
    assert out == []


# --- check_pointer_freshness ---

def _write_pointer(path: Path, *, updated_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "schema: agent-runtime-next-session-pointer/v1\n"
        f"updated_at: {updated_at}\n"
        "updated_by: lead-engineer\n"
        "current_state:\n"
        "  signal: pass\n"
        "  score: 95\n"
        "  summary: >\n"
        "    First summary line that should be the head.\n"
        "    Second line that should be ignored for the head.\n"
    )
    path.write_text(text, encoding="utf-8")


def test_check_pointer_freshness_recent_not_stale(tmp_path):
    pointer = tmp_path / "NEXT-SESSION-POINTER.yml"
    _write_pointer(pointer, updated_at="2026-06-21T10:00:00+09:00")
    out = src.check_pointer_freshness(
        pointer, now_iso="2026-06-21T11:00:00+09:00", max_age_hours=24.0)
    assert out["exists"] is True
    assert out["stale"] is False
    assert out["signal"] == "pass"
    assert str(out["score"]) == "95"
    assert isinstance(out["summary_head"], str) and out["summary_head"]
    assert "First summary line" in out["summary_head"]
    assert out["age_hours"] is not None and out["age_hours"] < 2


def test_check_pointer_freshness_old_is_stale(tmp_path):
    pointer = tmp_path / "NEXT-SESSION-POINTER.yml"
    _write_pointer(pointer, updated_at="2026-06-19T10:00:00+09:00")
    out = src.check_pointer_freshness(
        pointer, now_iso="2026-06-21T11:00:00+09:00", max_age_hours=24.0)
    assert out["stale"] is True
    assert out["age_hours"] > 24


def test_check_pointer_freshness_missing(tmp_path):
    pointer = tmp_path / "does-not-exist.yml"
    out = src.check_pointer_freshness(
        pointer, now_iso="2026-06-21T11:00:00+09:00", max_age_hours=24.0)
    assert out["exists"] is False


# --- check_ralph_consistency ---

def _write_ralph(path: Path, *, active: str, started_at: str, iteration=0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "---\n"
        f"active: {active}\n"
        f"iteration: {iteration}\n"
        "session_id: null\n"
        f'started_at: "{started_at}"\n'
        "---\n\n"
        "body\n"
    )
    path.write_text(text, encoding="utf-8")


def test_check_ralph_consistency_active_old_has_warnings(tmp_path):
    ralph = tmp_path / "ralph-loop.local.md"
    _write_ralph(ralph, active="true", started_at="2026-06-01T00:00:00Z")
    pointer = {"summary_head": "TASK-169 done", "updated_at": "2026-06-21T10:00:00+09:00"}
    # now epoch ~ 2026-06-21
    now = 1_781_000_000.0
    out = src.check_ralph_consistency(ralph, pointer, now)
    assert out["exists"] is True
    assert out["active"] is True
    assert out["warnings"], "expected warnings for active stale loop"


def test_check_ralph_consistency_inactive_no_blind_resume_warning(tmp_path):
    ralph = tmp_path / "ralph-loop.local.md"
    _write_ralph(ralph, active="false", started_at="2026-06-01T00:00:00Z")
    pointer = {"summary_head": "TASK-169 done"}
    now = 1_781_000_000.0
    out = src.check_ralph_consistency(ralph, pointer, now)
    assert out["active"] is False
    joined = " ".join(out["warnings"]).lower()
    assert "blind" not in joined and "resume" not in joined


# --- render_report ---

def test_render_report_clean_contains_ok():
    report = {
        "resume": {
            "summary_head": "all good",
            "pointer": {"updated_at": "x", "age_hours": 1.0, "signal": "pass",
                        "score": "95"},
            "status_head": "status line",
            "ralph": {"active": False, "iteration": 0},
        },
        "crash_scan": {
            "stale_claims": [],
            "claimed_stale_messages": [],
            "candidate_dead_sessions": [],
        },
        "warnings": [],
        "clean": True,
    }
    text = src.render_report(report)
    assert "OK" in text
    assert "SESSION RESUME CHECK" in text


def test_render_report_with_warnings_lists_them():
    report = {
        "resume": {
            "summary_head": "needs attention",
            "pointer": {"updated_at": "x", "age_hours": 99.0, "signal": "pass",
                        "score": "95"},
            "status_head": "status line",
            "ralph": {"active": True, "iteration": 7},
        },
        "crash_scan": {
            "stale_claims": [{"file": "MSG-x.claim"}],
            "claimed_stale_messages": [],
            "candidate_dead_sessions": [],
        },
        "warnings": ["something is stale", "loop is active"],
        "clean": False,
    }
    text = src.render_report(report)
    assert "something is stale" in text
    assert "loop is active" in text
    assert "OK" not in text.split("WARNINGS")[0] or "WARNINGS" in text


# --- _parse_iso_epoch ---

def test_parse_iso_epoch_z_equals_offset():
    # Z and +00:00 denote the same instant -> same epoch.
    assert (src._parse_iso_epoch("2026-06-20T11:57:37Z")
            == src._parse_iso_epoch("2026-06-20T11:57:37+00:00"))


def test_parse_iso_epoch_offset_equals_equivalent_utc():
    # +09:00 11:57:37 is the same instant as +00:00 02:57:37.
    plus_nine = src._parse_iso_epoch("2026-06-20T11:57:37+09:00")
    utc = src._parse_iso_epoch("2026-06-20T02:57:37+00:00")
    assert isinstance(plus_nine, float)
    assert plus_nine == utc


def test_parse_iso_epoch_naive_treated_as_utc():
    # A naive timestamp (no offset) parses without raising; code treats it as UTC.
    naive = src._parse_iso_epoch("2026-06-20T11:57:37")
    assert isinstance(naive, float)
    assert naive == src._parse_iso_epoch("2026-06-20T11:57:37+00:00")


def test_parse_iso_epoch_strips_surrounding_quotes():
    # Quoted timestamps are handled the same as unquoted (function strips quotes).
    assert (src._parse_iso_epoch('"2026-06-20T11:57:37Z"')
            == src._parse_iso_epoch("2026-06-20T11:57:37Z"))


@pytest.mark.parametrize("value", ["not-a-date", "", None, 123])
def test_parse_iso_epoch_returns_none_for_bad_input(value):
    # None (no exception) for unparseable / empty / non-str inputs.
    assert src._parse_iso_epoch(value) is None


# --- sub-step checkpoints ---

def test_append_checkpoint_then_read_round_trips(tmp_path):
    cps = tmp_path / "checkpoints"
    src.append_checkpoint(cps, task="TASK-1", step="write tests",
                          status="started", next_action="implement",
                          agent="lead-engineer",
                          now_iso="2026-06-21T10:00:00+09:00")
    latest = src.read_latest_checkpoints(cps)
    assert len(latest) == 1
    rec = latest[0]
    assert rec["task"] == "TASK-1"
    assert rec["step"] == "write tests"
    assert rec["status"] == "started"
    assert rec["next"] == "implement"
    assert rec["agent"] == "lead-engineer"
    assert rec["ts"] == "2026-06-21T10:00:00+09:00"
    assert rec["open"] is True


def test_read_latest_checkpoints_last_line_wins(tmp_path):
    cps = tmp_path / "checkpoints"
    src.append_checkpoint(cps, task="TASK-2", step="step one",
                          status="started", now_iso="2026-06-21T10:00:00+09:00")
    src.append_checkpoint(cps, task="TASK-2", step="step two",
                          status="started", now_iso="2026-06-21T11:00:00+09:00")
    src.append_checkpoint(cps, task="TASK-2", step="step three",
                          status="done", now_iso="2026-06-21T12:00:00+09:00")
    latest = src.read_latest_checkpoints(cps)
    assert len(latest) == 1
    assert latest[0]["step"] == "step three"
    assert latest[0]["status"] == "done"
    assert latest[0]["open"] is False


@pytest.mark.parametrize("status,expected_open", [
    ("started", True),
    ("blocked", True),
    ("done", False),
    ("closed", False),
    ("completed", False),
])
def test_read_latest_checkpoints_open_flag(tmp_path, status, expected_open):
    cps = tmp_path / "checkpoints"
    src.append_checkpoint(cps, task="TASK-open", step="x", status=status,
                          now_iso="2026-06-21T10:00:00+09:00")
    latest = src.read_latest_checkpoints(cps)
    assert len(latest) == 1
    assert latest[0]["open"] is expected_open


def test_checkpoint_file_sanitizes_messy_task_id(tmp_path):
    cps = tmp_path / "checkpoints"
    path = src._checkpoint_file(cps, "TASK 9/abc:x")
    # No path separators leaked into the filename, single safe stem, .jsonl.
    assert path.parent == cps
    assert path.suffix == ".jsonl"
    name = path.name
    assert "/" not in name and "\\" not in name and ":" not in name
    assert " " not in name
    assert name == "TASK_9_abc_x.jsonl"


def test_checkpoint_file_empty_falls_back_to_task(tmp_path):
    cps = tmp_path / "checkpoints"
    path = src._checkpoint_file(cps, "///")
    assert path.name == "task.jsonl"


def test_read_latest_checkpoints_missing_dir_returns_empty(tmp_path):
    assert src.read_latest_checkpoints(tmp_path / "nope") == []


def test_read_latest_checkpoints_skips_empty_and_unparseable(tmp_path):
    cps = tmp_path / "checkpoints"
    cps.mkdir(parents=True, exist_ok=True)
    # A file with only blank/garbage lines yields no record.
    (cps / "GARBAGE.jsonl").write_text("\n\nnot json\n\n", encoding="utf-8")
    # A dotfile is ignored.
    (cps / ".hidden.jsonl").write_text(
        '{"task":"H","status":"started"}\n', encoding="utf-8")
    assert src.read_latest_checkpoints(cps) == []


def _write_checkpoint_line(cps: Path, task: str, *, status: str,
                           ts="2026-06-21T10:00:00+09:00") -> None:
    cps.mkdir(parents=True, exist_ok=True)
    rec = {"ts": ts, "task": task, "step": "s", "status": status,
           "next": "n", "agent": "a"}
    (cps / f"{task}.jsonl").write_text(
        json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")


def _make_root_with_checkpoints(tmp_path):
    cps = tmp_path / "agents" / "runtime" / "checkpoints"
    _write_checkpoint_line(cps, "TASK-OPEN", status="started")
    _write_checkpoint_line(cps, "TASK-DONE", status="done")
    return tmp_path


def test_build_report_includes_only_open_checkpoints(tmp_path):
    root = _make_root_with_checkpoints(tmp_path)
    report = src.build_report(
        root, now_epoch=1_781_000_000.0,
        now_iso="2026-06-21T11:00:00+09:00",
        max_session_age_seconds=3600.0, pointer_max_age_hours=24.0)
    cps = report["resume"]["checkpoints"]
    tasks = [c["task"] for c in cps]
    assert tasks == ["TASK-OPEN"]
    assert all(c["open"] for c in cps)


def test_build_report_no_checkpoints_dir_empty_list(tmp_path):
    report = src.build_report(
        tmp_path, now_epoch=1_781_000_000.0,
        now_iso="2026-06-21T11:00:00+09:00",
        max_session_age_seconds=3600.0, pointer_max_age_hours=24.0)
    assert report["resume"]["checkpoints"] == []


def test_render_report_contains_in_flight_line_when_open():
    report = {
        "resume": {
            "summary_head": "x",
            "pointer": {"updated_at": "x", "age_hours": 1.0, "signal": "pass",
                        "score": "95"},
            "status_head": "s",
            "ralph": {"active": False, "iteration": 0},
            "checkpoints": [{
                "ts": "2026-06-21T10:00:00+09:00", "task": "TASK-7",
                "step": "build", "status": "started", "next": "test",
                "open": True,
            }],
        },
        "crash_scan": {
            "stale_claims": [], "claimed_stale_messages": [],
            "candidate_dead_sessions": [],
        },
        "warnings": [],
        "clean": True,
    }
    text = src.render_report(report)
    assert "IN-FLIGHT:" in text
    assert "TASK-7" in text
    assert "step 'build'" in text


def test_render_report_no_in_flight_when_no_checkpoints():
    report = {
        "resume": {
            "summary_head": "x",
            "pointer": {"updated_at": "x", "age_hours": 1.0, "signal": "pass",
                        "score": "95"},
            "status_head": "s",
            "ralph": {"active": False, "iteration": 0},
            "checkpoints": [],
        },
        "crash_scan": {
            "stale_claims": [], "claimed_stale_messages": [],
            "candidate_dead_sessions": [],
        },
        "warnings": [],
        "clean": True,
    }
    text = src.render_report(report)
    assert "IN-FLIGHT:" not in text


def test_checkpoints_do_not_make_clean_report_unclean(tmp_path):
    # An in-flight checkpoint is normal, not an anomaly: a report that is clean
    # WITHOUT a checkpoint must stay clean=True once an open checkpoint is added.
    # Set up an otherwise-clean root (a fresh pointer so there is no
    # pointer-missing/stale warning, and no claims/sessions to flag).
    pointer = tmp_path / "agents" / "project" / "NEXT-SESSION-POINTER.yml"
    _write_pointer(pointer, updated_at="2026-06-21T10:30:00+09:00")
    kwargs = dict(now_epoch=1_781_000_000.0,
                  now_iso="2026-06-21T11:00:00+09:00",
                  max_session_age_seconds=3600.0, pointer_max_age_hours=24.0)

    baseline = src.build_report(tmp_path, **kwargs)
    assert baseline["clean"] is True, "fixture root should be clean to start"

    cps = tmp_path / "agents" / "runtime" / "checkpoints"
    _write_checkpoint_line(cps, "TASK-INFLIGHT", status="started")
    report = src.build_report(tmp_path, **kwargs)
    assert report["resume"]["checkpoints"], "expected the open checkpoint"
    assert report["clean"] is True
    assert report["warnings"] == []


def test_main_checkpoint_subcommand_writes_file_and_returns_zero(tmp_path, capsys):
    rc = src.main(["checkpoint", "--root", str(tmp_path), "--task", "TASK-X",
                   "--step", "build", "--status", "started"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "checkpoint recorded" in out
    jsonl = tmp_path / "agents" / "runtime" / "checkpoints" / "TASK-X.jsonl"
    assert jsonl.is_file()
    latest = src.read_latest_checkpoints(jsonl.parent)
    assert latest and latest[0]["task"] == "TASK-X"
    assert latest[0]["step"] == "build"


def test_main_checkpoint_root_before_subcommand_writes_to_that_root(tmp_path):
    # Regression: `--root X checkpoint ...` (root BEFORE the subcommand) must
    # write under X, not the default repo root. argparse SUPPRESS keeps the
    # top-level --root from being clobbered by the subparser default.
    rc = src.main(["--root", str(tmp_path), "checkpoint", "--task", "TASK-Y",
                   "--step", "scope", "--status", "started"])
    assert rc == 0
    jsonl = tmp_path / "agents" / "runtime" / "checkpoints" / "TASK-Y.jsonl"
    assert jsonl.is_file(), "checkpoint must honor --root placed before the subcommand"


def test_main_audit_still_works_without_subcommand(tmp_path, capsys):
    # No subcommand -> audit path, prints the RESUME CHECK block, exits 0.
    rc = src.main(["--root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "SESSION RESUME CHECK" in out
