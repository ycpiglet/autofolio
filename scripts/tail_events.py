"""Tail logs/events.jsonl and pretty-print new JSON events as they arrive.

Usage:
    python scripts/tail_events.py
    python scripts/tail_events.py --file logs/events.jsonl

Press Ctrl-C to stop.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_DEFAULT_LOG = Path("logs") / "events.jsonl"


def _pretty(record: dict) -> str:
    ts = record.get("ts", "?")
    level = record.get("level", "INFO")
    logger_name = record.get("logger", "")
    raw_msg = record.get("msg", "")

    # The message written by log_event() is itself a JSON string.
    try:
        payload = json.loads(raw_msg)
    except (json.JSONDecodeError, TypeError):
        payload = {"msg": raw_msg}

    event = payload.pop("event", None)
    extra = record.get("extra", {})
    if extra:
        payload.update(extra)

    # Build the formatted line.
    header = f"{ts}  [{level:<5}]  {logger_name}"
    if event:
        header += f"  event={event}"

    details = "  ".join(f"{k}={v!r}" for k, v in payload.items())
    return f"{header}\n    {details}" if details else header


def tail(path: Path) -> None:
    print(f"Tailing {path}  (Ctrl-C to stop)\n", flush=True)

    # Open in read mode; seek to end so we only show *new* lines.
    with path.open("r", encoding="utf-8") as fh:
        fh.seek(0, 2)  # SEEK_END
        while True:
            line = fh.readline()
            if line:
                line = line.rstrip("\n")
                if line:
                    try:
                        record = json.loads(line)
                        print(_pretty(record), flush=True)
                    except json.JSONDecodeError:
                        # Malformed line — print raw.
                        print(line, flush=True)
            else:
                time.sleep(0.5)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pretty-tail logs/events.jsonl")
    parser.add_argument(
        "--file",
        default=str(_DEFAULT_LOG),
        help="Path to the JSONL events file (default: logs/events.jsonl)",
    )
    args = parser.parse_args()

    log_path = Path(args.file)
    if not log_path.exists():
        print(f"[tail_events] File not found: {log_path}", file=sys.stderr)
        print("[tail_events] Waiting for the file to appear...", file=sys.stderr)
        while not log_path.exists():
            time.sleep(0.5)

    try:
        tail(log_path)
    except KeyboardInterrupt:
        print("\n[tail_events] Stopped.", flush=True)


if __name__ == "__main__":
    main()
