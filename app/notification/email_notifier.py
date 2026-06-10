"""Email SMTP 알림 어댑터 — BaseNotifier 구현. [Autofolio]

설정(.env):
  EMAIL_SMTP_HOST=smtp.gmail.com
  EMAIL_SMTP_PORT=587
  EMAIL_USER=you@gmail.com
  EMAIL_APP_PASSWORD=<앱 비밀번호>   # Gmail: 2단계 인증 → 앱 비밀번호 생성
  EMAIL_TO=recipient@example.com    # 수신자 (없으면 EMAIL_USER와 동일)

Gmail 앱 비밀번호: https://myaccount.google.com/apppasswords
"""
from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText

from app.common.logger import get_logger
from app.notification.base import BaseNotifier

logger = get_logger("autofolio.email")

_DEFAULT_SMTP_HOST = "smtp.gmail.com"
_DEFAULT_SMTP_PORT = 587


class EmailNotifier(BaseNotifier):
    """Gmail SMTP BaseNotifier 구현."""

    def __init__(
        self,
        smtp_host: str = _DEFAULT_SMTP_HOST,
        smtp_port: int = _DEFAULT_SMTP_PORT,
        user: str = "",
        app_password: str = "",
        to: str = "",
    ):
        self._host = smtp_host
        self._port = smtp_port
        self._user = user
        self._password = app_password
        self._to = to or user

    @property
    def channel_name(self) -> str:
        return "email"

    @property
    def enabled(self) -> bool:
        return bool(self._user and self._password)

    def send(self, text: str) -> None:
        if not self.enabled:
            logger.debug("[email] 자격증명 미설정 — 스킵")
            return
        try:
            msg = MIMEText(text, "plain", "utf-8")
            msg["Subject"] = f"[Autofolio] {text[:50]}"
            msg["From"] = self._user
            msg["To"] = self._to
            with smtplib.SMTP(self._host, self._port, timeout=10) as s:
                s.ehlo()
                s.starttls()
                s.login(self._user, self._password)
                s.sendmail(self._user, [self._to], msg.as_string())
            logger.info("[email] 발송 완료 → %s", self._to)
        except Exception as exc:  # noqa: BLE001
            logger.warning("[email] 발송 실패: %s", exc)

    def send_engine_summary(self, run: int, executed: int, errors: int) -> None:
        body = (
            f"Autofolio 엔진 실행 #{run}\n"
            f"체결: {executed}건\n"
            f"오류: {errors}건\n"
        )
        if not self.enabled:
            return
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = f"[Autofolio] 엔진 #{run} 요약"
            msg["From"] = self._user
            msg["To"] = self._to
            with smtplib.SMTP(self._host, self._port, timeout=10) as s:
                s.ehlo(); s.starttls(); s.login(self._user, self._password)
                s.sendmail(self._user, [self._to], msg.as_string())
        except Exception as exc:  # noqa: BLE001
            logger.warning("[email] summary 발송 실패: %s", exc)


def make_email_notifier_from_env() -> EmailNotifier:
    return EmailNotifier(
        smtp_host=os.getenv("EMAIL_SMTP_HOST", _DEFAULT_SMTP_HOST),
        smtp_port=int(os.getenv("EMAIL_SMTP_PORT", str(_DEFAULT_SMTP_PORT))),
        user=os.getenv("EMAIL_USER", ""),
        app_password=os.getenv("EMAIL_APP_PASSWORD", ""),
        to=os.getenv("EMAIL_TO", ""),
    )
