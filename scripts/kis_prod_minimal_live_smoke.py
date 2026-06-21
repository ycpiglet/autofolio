#!/usr/bin/env python3
"""Prod entrypoint for the KIS minimal live-order smoke.

Requires same-day paper evidence plus explicit real-order confirmation.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.kis_minimal_order_smoke import main


if __name__ == "__main__":
    raise SystemExit(main(default_env="prod", locked_env=True))
