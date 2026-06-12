#!/usr/bin/env python3
"""Paper-env only scheduler — runs ``LiveTradingEngine.run_once()`` on a timer.

Safety
------
- **Hard guard**: refuses to start unless ``KIS_ENV == paper`` (resolved via
  ``resolve_settings``) AND the KIS base URL contains ``openapivts`` (the
  virtual trading server hostname).
- Only runs during regular trading hours (09:10-15:20 KST) unless
  ``--dry-run`` is passed.
- ``--dry-run`` mode logs what would run but uses ``MockBrokerClient`` so no
  real orders are sent.

Usage
-----
    python scripts/run_paper_engine.py
    python scripts/run_paper_engine.py --interval 60
    python scripts/run_paper_engine.py --once
    python scripts/run_paper_engine.py --dry-run
    python scripts/run_paper_engine.py --dry-run --once
    python scripts/run_paper_engine.py --dry-run --interval 5

Prerequisites
-------------
- ``.env`` with ``KIS_ENV=paper`` and ``KIS_PAPER_APP_KEY`` / ``KIS_PAPER_APP_SECRET``
  / ``KIS_PAPER_ACCOUNT_NO`` / ``KIS_PAPER_ACCOUNT_PRODUCT_CODE`` set.
- DB initialised: ``python scripts/init_db.py``
- At least one active trade condition and system_state ``auto_trading_enabled=true``.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# --- Project root on sys.path so imports work when run as a script ----------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.common.logger import get_logger  # noqa: E402
from app.config.settings import resolve_settings  # noqa: E402
from app.database.repositories import Repository  # noqa: E402
from app.database.sqlite_db import get_connection  # noqa: E402  # noqa: F401 — used via Repository
from app.engine.live_trading_engine import LiveTradingEngine  # noqa: E402
from app.notification.notifier import make_notifier_from_env  # noqa: E402
from app.risk.safety_checker import SafetyChecker  # noqa: E402
from app.risk.trading_window import is_within_trading_window, now_kst  # noqa: E402

logger = get_logger(__name__)

_DEFAULT_INTERVAL_SEC = 30


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Paper-env only engine scheduler (09:10-15:20 KST)."
    )
    ap.add_argument(
        "--interval",
        type=int,
        default=_DEFAULT_INTERVAL_SEC,
        help=f"Seconds between run_once() calls (default: {_DEFAULT_INTERVAL_SEC}).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Log what would run but use MockBrokerClient — "
            "no real orders are sent. Trading-window check is bypassed."
        ),
    )
    ap.add_argument(
        "--once",
        action="store_true",
        help=(
            "Run one engine tick and exit. In non-dry-run mode, exits without "
            "sending orders if outside the configured trading window."
        ),
    )
    return ap


def _guard_paper_env(cfg) -> None:  # type: ignore[type-arg]
    """Abort with a clear message if not running against the paper endpoint."""
    kis_env_var = os.getenv("KIS_ENV", "").lower()
    if cfg.kis_env != "paper":
        logger.error(
            "Hard guard: resolved KIS_ENV='%s' (env var='%s'). "
            "This script runs paper environment only. Aborting.",
            cfg.kis_env,
            kis_env_var,
        )
        sys.exit(2)
    if "openapivts" not in cfg.kis_base_url:
        logger.error(
            "Hard guard: KIS base URL '%s' does not look like the paper "
            "(virtual trading) endpoint. Aborting.",
            cfg.kis_base_url,
        )
        sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    cfg = resolve_settings("paper")

    if not args.dry_run:
        _guard_paper_env(cfg)

    if args.dry_run:
        from app.brokers.mock.mock_client import MockBrokerClient  # noqa: PLC0415

        broker = MockBrokerClient()
        logger.info(
            "[DRY-RUN] Using MockBrokerClient — no real orders will be sent."
        )
    else:
        from app.brokers.kis.kis_client import KisClient  # noqa: PLC0415

        broker = KisClient(cfg)  # type: ignore[assignment]
        logger.info(
            "[PAPER] KIS paper engine starting. base=%s account=%s-%s interval=%ds",
            cfg.kis_base_url,
            cfg.kis_account_no,
            cfg.kis_account_product_code,
            args.interval,
        )

    repo = Repository(cfg.db_path)
    notifier = make_notifier_from_env()
    if notifier.enabled:
        logger.info("[notify] Telegram 알림 활성 (chat_id 설정됨)")
    engine = LiveTradingEngine(broker=broker, repo=repo, notifier=notifier)

    logger.info(
        "Engine ready. Polling every %d seconds. Press Ctrl-C to stop.",
        args.interval,
    )

    run_count = 0
    try:
        while True:
            now = now_kst()

            in_window = is_within_trading_window(
                now,
                cfg.default_trading_start,
                cfg.default_trading_end,
            )

            if not in_window and not args.dry_run:
                if args.once:
                    logger.info(
                        "Outside trading window (%s-%s KST). One-shot run skipped.",
                        cfg.default_trading_start,
                        cfg.default_trading_end,
                    )
                    return 3
                logger.info(
                    "Outside trading window (%s-%s KST). Sleeping %ds.",
                    cfg.default_trading_start,
                    cfg.default_trading_end,
                    args.interval,
                )
                time.sleep(args.interval)
                continue

            run_count += 1
            logger.info("--- run #%d at %s ---", run_count, now.strftime("%H:%M:%S"))

            if args.dry_run:
                logger.info(
                    "[DRY-RUN] Would call engine.run_once() now "
                    "(in_window=%s, time=%s).",
                    in_window,
                    now.strftime("%H:%M:%S"),
                )
                # Still exercise the engine path so dry-run catches import/config errors.

            try:
                results = engine.run_once()
            except Exception:  # noqa: BLE001
                logger.exception("engine.run_once() raised an unhandled exception.")
                time.sleep(args.interval)
                continue

            for msg in results:
                logger.info("  %s", msg)

            if not results:
                logger.info("  (no active conditions processed)")

            if args.once:
                logger.info("One-shot run complete.")
                return 0

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Interrupted after %d run(s). Exiting.", run_count)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
