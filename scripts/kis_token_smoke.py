#!/usr/bin/env python3
"""KIS OAuth 토큰 발급 스모크 — paper/prod '연동(자격증명)' 확인. [Autofolio 호스트 스크립트]

토큰 발급(grant_type=client_credentials)만 호출한다. **주문/조회/체결은 전혀 하지 않으므로
실전(prod) 계좌로도 안전**하다(앱키·시크릿이 유효한지 = 연동되는지 확인용). 실제 시세·주문은
app/brokers/kis/kis_client.py 구현(P1.1b) 이후.

사용:
  python scripts/kis_token_smoke.py                # paper + prod 둘 다 시도(키 있는 것만)
  python scripts/kis_token_smoke.py --env paper    # 모의만
  python scripts/kis_token_smoke.py --env prod     # 실전만(토큰만이라 안전)
  python scripts/kis_token_smoke.py --json

자격증명(.env) — paper·prod를 한 번에 테스트하려면 환경별 키를 따로 둔다(같은 .env 공존):
  KIS_PAPER_APP_KEY=...      # 없으면 KIS_APP_KEY 로 폴백
  KIS_PAPER_APP_SECRET=...   # 없으면 KIS_APP_SECRET
  KIS_PROD_APP_KEY=...
  KIS_PROD_APP_SECRET=...
  # 선택 override: KIS_PAPER_BASE_URL / KIS_PROD_BASE_URL / KIS_TOKEN_PATH(기본 /oauth2/tokenP)

종료코드: 0=시도한 환경 전부 토큰 OK · 1=하나라도 실패 · 2=시도할 자격증명 없음.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:  # 윈도우 콘솔(cp949)에서 한글 출력 안전
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.config.settings import Settings  # noqa: E402
from app.brokers.kis.kis_auth import KisAuth  # noqa: E402
from app.common.errors import ConfigurationError, BrokerError  # noqa: E402

DEFAULT_BASE = {
    "paper": "https://openapivts.koreainvestment.com:29443",
    "prod": "https://openapi.koreainvestment.com:9443",
}
DEFAULT_TOKEN_PATH = "/oauth2/tokenP"


def _cred(env: str, suffix: str) -> str:
    """환경별(KIS_PAPER_APP_KEY 등) 우선, 없으면 generic(KIS_APP_KEY) 폴백."""
    return os.getenv(f"KIS_{env.upper()}_APP_{suffix}") or os.getenv(f"KIS_APP_{suffix}", "")


def _settings_for(env: str) -> Settings:
    base = os.getenv(f"KIS_{env.upper()}_BASE_URL") or os.getenv("KIS_BASE_URL") or DEFAULT_BASE[env]
    token_path = os.getenv("KIS_TOKEN_PATH") or DEFAULT_TOKEN_PATH
    return Settings(
        kis_env=env,
        kis_app_key=_cred(env, "KEY"),
        kis_app_secret=_cred(env, "SECRET"),
        kis_base_url=base,
        kis_token_path=token_path,
    )


def smoke_one(env: str) -> dict:
    s = _settings_for(env)
    out: dict = {"env": env, "base_url": s.kis_base_url}
    if not s.kis_app_key or not s.kis_app_secret:
        out.update(status="skip", detail=f"키 없음 (KIS_{env.upper()}_APP_KEY 또는 KIS_APP_KEY 미설정)")
        return out
    try:
        token = KisAuth(s).get_access_token()
        # 토큰은 베어러 비밀이라 본문은 출력하지 않는다(길이만 보고).
        out.update(status="ok", token_len=len(token or ""))
    except (ConfigurationError, BrokerError) as e:
        out.update(status="fail", detail=str(e))
    except Exception as e:  # 네트워크/SSL/타임아웃 등
        out.update(status="fail", detail=f"{type(e).__name__}: {e}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KIS OAuth 토큰 발급 스모크(paper/prod)")
    ap.add_argument("--env", choices=["paper", "prod", "both"], default="both")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    envs = ["paper", "prod"] if args.env == "both" else [args.env]
    results = [smoke_one(e) for e in envs]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        tag = {"ok": "[ OK ]", "fail": "[FAIL]", "skip": "[SKIP]"}
        for r in results:
            line = f"{tag.get(r['status'], '[ ?? ]')} {r['env']:5s} {r['base_url']}"
            if r["status"] == "ok":
                line += f"  -> 토큰 발급 성공 (len={r['token_len']})"
            else:
                line += f"  -> {r.get('detail', '')}"
            print(line)

    attempted = [r for r in results if r["status"] != "skip"]
    failed = [r for r in attempted if r["status"] != "ok"]
    if not attempted:
        print("\n시도할 자격증명이 없습니다. .env 에 KIS_APP_KEY/SECRET(또는 KIS_PAPER_*/KIS_PROD_*)를 넣어주세요.")
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
