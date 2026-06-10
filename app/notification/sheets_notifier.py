"""Google Sheets 포트폴리오 미러 어댑터. [Autofolio]

설정(.env):
  GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service_account.json  # 또는 GOOGLE_CREDS_JSON(JSON 문자열)
  GOOGLE_SHEETS_SPREADSHEET_ID=xxxxxxxxxxxxx

Service Account 생성: Google Cloud Console → IAM → 서비스 계정 → 키 생성(JSON).
Sheets 공유: 스프레드시트 공유 → 서비스 계정 이메일 추가(편집자).
라이브러리: pip install gspread

동작:
- send(text): "알림" 시트에 타임스탬프·메시지 행 추가.
- sync_portfolio(df): "포트폴리오" 시트를 holdings_df()로 갱신.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from app.common.logger import get_logger
from app.notification.base import BaseNotifier

logger = get_logger("autofolio.sheets")


class SheetsNotifier(BaseNotifier):
    """Google Sheets BaseNotifier 구현."""

    def __init__(self, creds_path: str = "", spreadsheet_id: str = "", creds_json: str = ""):
        self._creds_path = creds_path
        self._creds_json = creds_json
        self._spreadsheet_id = spreadsheet_id
        self._gc = None  # lazy init

    @property
    def channel_name(self) -> str:
        return "sheets"

    @property
    def enabled(self) -> bool:
        return bool(self._spreadsheet_id and (self._creds_path or self._creds_json))

    def _client(self):
        if self._gc is None:
            try:
                import gspread
                if self._creds_json:
                    info = json.loads(self._creds_json)
                    self._gc = gspread.service_account_from_dict(info)
                else:
                    self._gc = gspread.service_account(filename=self._creds_path)
            except Exception as exc:  # noqa: BLE001
                logger.error("[sheets] gspread 초기화 실패: %s", exc)
        return self._gc

    def send(self, text: str) -> None:
        if not self.enabled:
            logger.debug("[sheets] 자격증명 미설정 — 스킵")
            return
        gc = self._client()
        if gc is None:
            return
        try:
            sh = gc.open_by_key(self._spreadsheet_id)
            ws = _get_or_create_sheet(sh, "알림")
            ws.append_row([datetime.now().isoformat(timespec="seconds"), text[:500]])
        except Exception as exc:  # noqa: BLE001
            logger.warning("[sheets] 알림 기록 실패: %s", exc)

    def sync_portfolio(self, df) -> None:
        """포트폴리오 DataFrame을 '포트폴리오' 시트에 전체 갱신."""
        if not self.enabled or df is None or df.empty:
            return
        gc = self._client()
        if gc is None:
            return
        try:
            sh = gc.open_by_key(self._spreadsheet_id)
            ws = _get_or_create_sheet(sh, "포트폴리오")
            ws.clear()
            ws.update([df.columns.tolist()] + df.astype(str).values.tolist())
            logger.info("[sheets] 포트폴리오 동기화 완료 (%d행)", len(df))
        except Exception as exc:  # noqa: BLE001
            logger.warning("[sheets] 포트폴리오 동기화 실패: %s", exc)


def _get_or_create_sheet(sh, title: str):
    try:
        return sh.worksheet(title)
    except Exception:  # noqa: BLE001
        return sh.add_worksheet(title=title, rows=500, cols=20)


def make_sheets_notifier_from_env() -> SheetsNotifier:
    return SheetsNotifier(
        creds_path=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", ""),
        creds_json=os.getenv("GOOGLE_CREDS_JSON", ""),
        spreadsheet_id=os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", ""),
    )
