"""연동 테스트 커넥터 (best-effort, 실제 API 호출).

자격증명이 없거나 네트워크가 막혀도 예외 없이 (성공여부, 메시지)를 돌려준다.
실제 키가 들어오면 '1원 인증' 대신 이 테스트 호출 성공이 곧 연동 검증이다.
"""
from __future__ import annotations

import requests

# 환경별 KIS 기본 베이스URL (실전/모의)
KIS_BASE = {
    "실전": "https://openapi.koreainvestment.com:9443",
    "모의": "https://openapivts.koreainvestment.com:29443",
    "mock": "https://openapivts.koreainvestment.com:29443",
}


def test_kis(app_key: str, app_secret: str, env: str = "모의") -> tuple[bool, str]:
    """KIS 접근토큰 발급으로 자격증명 검증."""
    if not app_key or not app_secret:
        return False, "App Key/Secret 미입력 (데모 저장만)"
    base = KIS_BASE.get(env, KIS_BASE["모의"])
    try:
        r = requests.post(
            f"{base}/oauth2/tokenP",
            json={"grant_type": "client_credentials", "appkey": app_key, "appsecret": app_secret},
            timeout=8,
        )
        if r.status_code == 200 and "access_token" in r.json():
            return True, "토큰 발급 성공 — 연동 확인"
        return False, f"실패: HTTP {r.status_code} {r.text[:120]}"
    except Exception as exc:  # noqa: BLE001
        return False, f"네트워크/오류: {exc}"


def test_telegram(token: str, chat_id: str = "") -> tuple[bool, str]:
    if not token:
        return False, "봇 토큰 미입력"
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8)
        if r.status_code == 200 and r.json().get("ok"):
            return True, "봇 확인됨"
        return False, f"실패: HTTP {r.status_code}"
    except Exception as exc:  # noqa: BLE001
        return False, f"네트워크/오류: {exc}"
