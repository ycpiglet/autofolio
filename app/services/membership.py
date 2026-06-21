"""Local membership approval prototype.

This is a local, encrypted-vault implementation for the approval workflow. It
does not create login accounts, write production DB rows, call bank APIs, or
store bank credentials in repository files.
"""
from __future__ import annotations

import os
import re
import secrets
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from app.ui import vault

_VAULT_KEY = "membership_requests"
_KST = timezone(timedelta(hours=9))
_STATUSES = {
    "requested",
    "verification_pending",
    "deposit_pending",
    "active",
    "rejected",
    "expired",
}
_TERMINAL_STATUSES = {"active", "rejected", "expired"}
_MAX_RECOGNITION_LINES = 200
_TRANSITIONS = {
    "requested": {"verification_pending", "deposit_pending", "active", "rejected", "expired"},
    "verification_pending": {"deposit_pending", "active", "rejected", "expired"},
    "deposit_pending": {"active", "rejected", "expired"},
    "active": {"expired"},
    "rejected": set(),
    "expired": set(),
}


def create_request(
    *,
    display_name: str,
    contact: str,
    plan: str = "pilot_monthly",
    referral_source: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Create a request in `requested` state.

    Duplicate open contacts return the existing request instead of creating a
    second pending row. This keeps manual Owner review simple and avoids noisy
    retries from the signup form.
    """
    clean_name = _clean(display_name, "display_name", max_len=80)
    clean_contact = _clean(contact, "contact", max_len=160)
    clean_plan = _clean(plan or "pilot_monthly", "plan", max_len=80)
    clean_source = _clean_optional(referral_source, max_len=120)
    clean_note = _clean_optional(note, max_len=500)

    records = _load_records()
    existing = _find_open_by_contact(records, clean_contact)
    if existing is not None:
        return _response(existing, message="이미 접수된 가입 승인 신청입니다.")

    now = _now()
    record = {
        "request_id": f"mrq_{secrets.token_urlsafe(8)}",
        "status": "requested",
        "display_name": clean_name,
        "contact": clean_contact,
        "plan": clean_plan,
        "referral_source": clean_source,
        "note": clean_note,
        "price_krw": _price_krw(),
        "deposit_code": _deposit_code(),
        "requested_at": now,
        "updated_at": now,
        "verified_at": None,
        "activated_at": None,
        "grant_expires_at": None,
        "deposit_due_at": None,
        "events": [
            {
                "actor": "applicant",
                "action": "requested",
                "previous_status": None,
                "next_status": "requested",
                "evidence_type": "signup_form",
                "note": None,
                "created_at": now,
            }
        ],
    }
    records.append(record)
    _save_records(records)
    return _response(record, message="가입 승인 신청이 접수되었습니다.")


def list_requests(status: str | None = None) -> list[dict[str, Any]]:
    """Return Owner-visible membership requests, newest first."""
    if status and status not in _STATUSES:
        raise ValueError("invalid membership status")
    records = _load_records()
    if status:
        records = [record for record in records if record.get("status") == status]
    return [
        _response(record, message=_message_for(record))
        for record in sorted(records, key=lambda item: item.get("requested_at", ""), reverse=True)
    ]


def transition_request(
    request_id: str,
    *,
    next_status: str,
    actor: str,
    evidence_type: str | None = None,
    note: str | None = None,
    grant_days: int | None = None,
    login_username: str | None = None,
    initial_password: str | None = None,
) -> dict[str, Any]:
    """Move a request through the approval state machine."""
    if next_status not in _STATUSES:
        raise ValueError("invalid membership status")

    records = _load_records()
    index = _find_index(records, request_id)
    if index is None:
        raise KeyError(request_id)

    record = records[index]
    previous = str(record.get("status") or "requested")
    if next_status not in _TRANSITIONS.get(previous, set()):
        raise ValueError(f"cannot transition from {previous} to {next_status}")

    now = _now()
    record["status"] = next_status
    record["updated_at"] = now
    if next_status in {"verification_pending", "deposit_pending", "active"} and not record.get("verified_at"):
        record["verified_at"] = now
    if next_status == "deposit_pending":
        record["deposit_due_at"] = (datetime.now(_KST) + timedelta(days=3)).isoformat()
    if next_status == "active":
        record["activated_at"] = now
        grant_expires_at = None
        if grant_days:
            grant_expires_at = (datetime.now(_KST) + timedelta(days=grant_days)).isoformat()
            record["grant_expires_at"] = grant_expires_at
        record["subscription_grant"] = {
            "plan": record.get("plan") or "pilot_monthly",
            "starts_at": now,
            "ends_at": grant_expires_at,
            "source_event": "manual_owner_activation",
        }
        if initial_password:
            from app.services.auth_service import create_or_update_user

            username = _clean_optional(login_username, max_len=160) or str(record.get("contact") or "")
            ok, msg = create_or_update_user(
                username,
                initial_password,
                role="member",
                source="membership_approval",
                membership_request_id=request_id,
            )
            if not ok:
                raise ValueError(msg)
            record["account_grant"] = {
                "username": username,
                "role": "member",
                "created_at": now,
                "password_set": True,
            }

    record.setdefault("events", []).append(
        {
            "actor": _clean(actor or "owner", "actor", max_len=80),
            "action": "status_change",
            "previous_status": previous,
            "next_status": next_status,
            "evidence_type": _clean_optional(evidence_type, max_len=80),
            "note": _clean_optional(note, max_len=500),
            "created_at": now,
        }
    )
    records[index] = record
    _save_records(records)
    return _response(record, message=_message_for(record))


def get_request(request_id: str) -> dict[str, Any] | None:
    records = _load_records()
    index = _find_index(records, request_id)
    if index is None:
        return None
    record = records[index]
    return _response(record, message=_message_for(record))


def lookup_request_status(request_id: str, contact: str) -> dict[str, Any] | None:
    """Return applicant-safe status when request id and contact match."""
    clean_request_id = _clean(request_id, "request_id", max_len=80)
    clean_contact = _clean(contact, "contact", max_len=160)
    records = _load_records()
    index = _find_index(records, clean_request_id)
    if index is None:
        return None

    record = records[index]
    if str(record.get("contact") or "").strip().lower() != clean_contact.lower():
        return None
    return _applicant_response(record)


def recognize_deposits(source_text: str, *, min_confidence: int = 50) -> dict[str, Any]:
    """Match pasted bank statement text/CSV against deposit-pending requests.

    This helper is intentionally stateless. It does not call bank APIs and does
    not persist pasted bank rows. It returns short masked excerpts for Owner
    review only.
    """
    min_confidence = max(0, min(int(min_confidence), 100))
    lines = _statement_lines(source_text)
    records = [
        record for record in _load_records()
        if str(record.get("status") or "") == "deposit_pending"
    ]

    matches: list[dict[str, Any]] = []
    for record in records:
        best = _best_deposit_match(record, lines)
        if best is not None and int(best["confidence"]) >= min_confidence:
            matches.append(best)

    matches.sort(key=lambda item: (-int(item["confidence"]), item["display_name"]))
    return {
        "matches": matches,
        "scanned_lines": len(lines),
        "candidate_requests": len(records),
        "min_confidence": min_confidence,
    }


def _load_records() -> list[dict[str, Any]]:
    data = vault.load()
    records = data.get(_VAULT_KEY, [])
    if not isinstance(records, list):
        return []
    return deepcopy(records)


def _save_records(records: list[dict[str, Any]]) -> None:
    data = vault.load()
    data[_VAULT_KEY] = records
    vault.save(data)


def _response(record: dict[str, Any], *, message: str) -> dict[str, Any]:
    status = str(record.get("status") or "requested")
    response = {
        "request_id": record["request_id"],
        "status": status,
        "display_name": record.get("display_name") or "",
        "contact": record.get("contact") or "",
        "plan": record.get("plan") or "pilot_monthly",
        "price_krw": int(record.get("price_krw") or _price_krw()),
        "requested_at": record.get("requested_at") or "",
        "updated_at": record.get("updated_at") or record.get("requested_at") or "",
        "verified_at": record.get("verified_at"),
        "activated_at": record.get("activated_at"),
        "grant_expires_at": record.get("grant_expires_at"),
        "deposit_instruction": None,
        "account_grant": record.get("account_grant"),
        "subscription_grant": record.get("subscription_grant"),
        "events": record.get("events") or [],
        "message": message,
    }
    if status in {"deposit_pending", "active"}:
        response["deposit_instruction"] = _deposit_instruction(record)
    return response


def _applicant_response(record: dict[str, Any]) -> dict[str, Any]:
    response = _response(record, message=_message_for(record))
    response["events"] = []
    response["account_grant"] = None
    response["subscription_grant"] = None
    return response


def _deposit_instruction(record: dict[str, Any]) -> dict[str, Any]:
    bank_name = _env("AUTOFOLIO_MEMBERSHIP_BANK_NAME")
    account_holder = _env("AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER")
    account_number = _env("AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT")
    return {
        "price_krw": int(record.get("price_krw") or _price_krw()),
        "currency": "KRW",
        "deposit_code": record.get("deposit_code") or _deposit_code(),
        "bank_name": bank_name or None,
        "account_holder": account_holder or None,
        "account_number": account_number or None,
        "account_configured": bool(bank_name and account_holder and account_number),
        "due_at": record.get("deposit_due_at"),
    }


def _statement_lines(source_text: str) -> list[str]:
    lines: list[str] = []
    for raw in (source_text or "").splitlines():
        cleaned = " ".join(raw.strip().split())
        if cleaned:
            lines.append(cleaned)
        if len(lines) >= _MAX_RECOGNITION_LINES:
            break
    return lines


def _best_deposit_match(record: dict[str, Any], lines: list[str]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for line in lines:
        candidate = _score_deposit_line(record, line)
        if candidate is None:
            continue
        if best is None or int(candidate["confidence"]) > int(best["confidence"]):
            best = candidate
    return best


def _score_deposit_line(record: dict[str, Any], line: str) -> dict[str, Any] | None:
    haystack = line.lower()
    expected_amount = int(record.get("price_krw") or _price_krw())
    amounts = _amounts_from_line(line)
    amount_match = expected_amount in amounts
    deposit_code = str(record.get("deposit_code") or "").strip()
    code_match = bool(deposit_code and deposit_code.lower() in haystack)
    name_match = _needle_present(str(record.get("display_name") or ""), haystack)
    contact_match = _needle_present(str(record.get("contact") or ""), haystack)

    confidence = 0
    reasons: list[str] = []
    if code_match:
        confidence += 70
        reasons.append("deposit_code")
    if amount_match:
        confidence += 25
        reasons.append("amount")
    if name_match:
        confidence += 15
        reasons.append("display_name")
    if contact_match:
        confidence += 10
        reasons.append("contact")

    if not reasons:
        return None
    confidence = min(confidence, 100)
    return {
        "request_id": record.get("request_id") or "",
        "display_name": record.get("display_name") or "",
        "contact": record.get("contact") or "",
        "status": record.get("status") or "deposit_pending",
        "deposit_code": deposit_code,
        "expected_amount_krw": expected_amount,
        "matched_amount_krw": expected_amount if amount_match else (amounts[0] if amounts else None),
        "confidence": confidence,
        "reasons": reasons,
        "matched_text_excerpt": _masked_excerpt(line),
        "suggested_evidence_type": "code_assisted_deposit_match" if confidence >= 80 else "manual_bank_app_check",
    }


def _needle_present(value: str, haystack: str) -> bool:
    needle = value.strip().lower()
    return bool(needle and len(needle) >= 2 and needle in haystack)


def _amounts_from_line(line: str) -> list[int]:
    amounts: list[int] = []
    for match in re.finditer(r"(?<![A-Za-z0-9])\d[\d,]{2,}(?![A-Za-z0-9])", line):
        raw = match.group(0).replace(",", "")
        try:
            amount = int(raw)
        except ValueError:
            continue
        if amount > 0:
            amounts.append(amount)
    return amounts


def _masked_excerpt(line: str) -> str:
    excerpt = line[:140]
    excerpt = re.sub(r"\b\d{2,4}[- ]?\d{2,6}[- ]?\d{2,6}\b", "***", excerpt)
    excerpt = re.sub(r"\b\d{8,}\b", "***", excerpt)
    return excerpt


def _message_for(record: dict[str, Any]) -> str:
    status = str(record.get("status") or "requested")
    if status == "requested":
        return "가입 승인 신청이 접수되었습니다."
    if status == "verification_pending":
        return "Owner 검증 대기 상태입니다."
    if status == "deposit_pending":
        return "입금 확인 대기 상태입니다."
    if status == "active":
        return "계정 승인 상태입니다."
    if status == "rejected":
        return "가입 승인 신청이 거절되었습니다."
    if status == "expired":
        return "가입 승인 신청 또는 결제 대기 상태가 만료되었습니다."
    return "가입 승인 신청 상태를 확인했습니다."


def _find_index(records: list[dict[str, Any]], request_id: str) -> int | None:
    for index, record in enumerate(records):
        if record.get("request_id") == request_id:
            return index
    return None


def _find_open_by_contact(records: list[dict[str, Any]], contact: str) -> dict[str, Any] | None:
    normalized = contact.lower()
    for record in records:
        if str(record.get("contact") or "").lower() != normalized:
            continue
        if record.get("status") not in _TERMINAL_STATUSES:
            return record
    return None


def _clean(value: str, field: str, *, max_len: int) -> str:
    cleaned = " ".join((value or "").strip().split())
    if not cleaned:
        raise ValueError(f"{field} is required")
    if len(cleaned) > max_len:
        raise ValueError(f"{field} is too long")
    return cleaned


def _clean_optional(value: str | None, *, max_len: int) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None
    if len(cleaned) > max_len:
        raise ValueError("field is too long")
    return cleaned


def _price_krw() -> int:
    raw = _env("AUTOFOLIO_MEMBERSHIP_PRICE_KRW") or "20000"
    try:
        price = int(raw)
    except ValueError:
        price = 20000
    return max(price, 0)


def _deposit_code() -> str:
    return f"AF-{secrets.token_hex(3).upper()}"


def _now() -> str:
    return datetime.now(_KST).isoformat()


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()
