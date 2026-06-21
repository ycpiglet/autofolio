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
