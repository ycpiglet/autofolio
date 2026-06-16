"""Investor profile survey service.

Personalization only: this module does not provide legal suitability advice and
does not mutate live order, broker, or risk-policy paths.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.database.sqlite_db import get_connection

SURVEY_VERSION = "investor-profile-v1"
AXES = (
    "risk_capacity",
    "risk_tolerance",
    "knowledge",
    "experience",
    "time_horizon",
    "automation_comfort",
)


class SurveyValidationError(ValueError):
    """Raised when a survey submission is incomplete or invalid."""


@dataclass(frozen=True)
class ProfileGate:
    allowed: bool
    status: str
    message: str


_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS investor_profiles (
    username TEXT PRIMARY KEY,
    survey_version TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    risk_type TEXT NOT NULL DEFAULT '미완료',
    knowledge_level TEXT NOT NULL DEFAULT '미확인',
    risk_capacity_score REAL NOT NULL DEFAULT 0,
    risk_tolerance_score REAL NOT NULL DEFAULT 0,
    knowledge_score REAL NOT NULL DEFAULT 0,
    experience_score REAL NOT NULL DEFAULT 0,
    time_horizon_score REAL NOT NULL DEFAULT 0,
    automation_comfort_score REAL NOT NULL DEFAULT 0,
    recommended_max_equity_pct INTEGER NOT NULL DEFAULT 0,
    recommended_autonomy_level TEXT NOT NULL DEFAULT 'L0',
    needs_advanced_survey INTEGER NOT NULL DEFAULT 0,
    satisfaction_focus TEXT NOT NULL DEFAULT '[]',
    last_checkin_at TEXT,
    satisfaction_score INTEGER,
    confidence_score INTEGER,
    stress_score INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);
CREATE TABLE IF NOT EXISTS investor_survey_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    survey_version TEXT NOT NULL,
    response_json TEXT NOT NULL,
    scores_json TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_investor_survey_responses_user_created
ON investor_survey_responses(username, created_at);
CREATE TABLE IF NOT EXISTS investor_override_acknowledgements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    symbol TEXT,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    acknowledgement_text TEXT NOT NULL,
    profile_version TEXT NOT NULL,
    profile_snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_investor_override_ack_user_created
ON investor_override_acknowledgements(username, created_at);
CREATE TABLE IF NOT EXISTS investor_checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    satisfaction_score INTEGER NOT NULL,
    confidence_score INTEGER NOT NULL,
    stress_score INTEGER NOT NULL,
    automation_adjustment TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_investor_checkins_user_created
ON investor_checkins(username, created_at);
"""


_QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "investment_goal",
        "title": "투자 목적",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "preserve", "label": "원금 보존", "scores": {"risk_tolerance": 0, "time_horizon": 1}},
            {"value": "income", "label": "정기 현금흐름", "scores": {"risk_tolerance": 1, "time_horizon": 2}},
            {"value": "growth", "label": "장기 성장", "scores": {"risk_tolerance": 2, "time_horizon": 3}},
            {"value": "opportunity", "label": "단기 기회", "scores": {"risk_tolerance": 3, "time_horizon": 1}},
            {"value": "learning", "label": "학습과 실험", "scores": {"risk_tolerance": 2, "knowledge": 1}},
        ],
    },
    {
        "id": "time_horizon",
        "title": "투자 가능 기간",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "under_6m", "label": "6개월 미만", "scores": {"time_horizon": 0, "risk_capacity": 0}},
            {"value": "one_year", "label": "1년 전후", "scores": {"time_horizon": 1, "risk_capacity": 1}},
            {"value": "three_years", "label": "3년 전후", "scores": {"time_horizon": 3, "risk_capacity": 2}},
            {"value": "five_plus", "label": "5년 이상", "scores": {"time_horizon": 4, "risk_capacity": 3}},
        ],
    },
    {
        "id": "capital_need",
        "title": "투자금 성격",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "near_term_need", "label": "곧 필요할 수 있는 자금", "scores": {"risk_capacity": 0}},
            {"value": "partial_buffer", "label": "일부는 필요할 수 있음", "scores": {"risk_capacity": 1}},
            {"value": "separate_savings", "label": "생활비와 분리된 여유자금", "scores": {"risk_capacity": 3}},
            {"value": "long_term_pool", "label": "장기 운용 전용 자금", "scores": {"risk_capacity": 4}},
        ],
    },
    {
        "id": "loss_response",
        "title": "손실 구간 행동",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "sell_5", "label": "-5% 전후에서 대부분 정리", "scores": {"risk_tolerance": 0}},
            {"value": "reduce_10", "label": "-10%에서 일부 축소", "scores": {"risk_tolerance": 1}},
            {"value": "hold_20", "label": "-20%도 계획이면 보유", "scores": {"risk_tolerance": 3}},
            {"value": "add_30", "label": "-30%에서도 근거가 있으면 추가", "scores": {"risk_tolerance": 4}},
        ],
    },
    {
        "id": "volatility_preference",
        "title": "변동성 선호",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "low", "label": "낮은 변동과 낮은 기대수익", "scores": {"risk_tolerance": 0}},
            {"value": "balanced", "label": "중간 수준의 변동", "scores": {"risk_tolerance": 2}},
            {"value": "high", "label": "높은 변동과 높은 기대수익", "scores": {"risk_tolerance": 4}},
        ],
    },
    {
        "id": "experience",
        "title": "경험한 투자 상품",
        "kind": "multi",
        "required": True,
        "options": [
            {"value": "deposit", "label": "예적금", "scores": {"experience": 0}},
            {"value": "fund_etf", "label": "펀드/ETF", "scores": {"experience": 1, "knowledge": 1}},
            {"value": "domestic_stock", "label": "국내주식", "scores": {"experience": 1, "knowledge": 1}},
            {"value": "overseas_stock", "label": "해외주식", "scores": {"experience": 2, "knowledge": 1}},
            {"value": "leveraged", "label": "레버리지/인버스", "scores": {"experience": 2, "knowledge": 2}},
            {"value": "derivatives", "label": "파생상품", "scores": {"experience": 3, "knowledge": 2}},
        ],
    },
    {
        "id": "knowledge_diversification",
        "title": "분산투자 이해",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "single_is_safer", "label": "확신 있는 한 종목 집중이 항상 더 안전", "scores": {"knowledge": 0}},
            {"value": "reduces_single_risk", "label": "개별 종목 리스크를 줄일 수 있음", "scores": {"knowledge": 3}},
            {"value": "guarantees_profit", "label": "분산하면 손실이 나지 않음", "scores": {"knowledge": 0}},
        ],
    },
    {
        "id": "knowledge_drawdown",
        "title": "최대낙폭 이해",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "largest_drop", "label": "고점 대비 최대 하락폭", "scores": {"knowledge": 3}},
            {"value": "daily_loss", "label": "하루 손실액", "scores": {"knowledge": 1}},
            {"value": "tax_cost", "label": "매매 수수료와 세금", "scores": {"knowledge": 0}},
        ],
    },
    {
        "id": "knowledge_order_type",
        "title": "주문 방식 이해",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "limit_controls_price", "label": "지정가는 가격을 제한하지만 체결 안 될 수 있음", "scores": {"knowledge": 3}},
            {"value": "market_controls_price", "label": "시장가는 가격을 정확히 지정함", "scores": {"knowledge": 0}},
            {"value": "same", "label": "시장가와 지정가는 거의 같음", "scores": {"knowledge": 0}},
        ],
    },
    {
        "id": "automation_preference",
        "title": "자동화 선호",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "alerts_only", "label": "알림만 받고 직접 판단", "scores": {"automation_comfort": 0}},
            {"value": "suggestions", "label": "제안까지 받고 직접 승인", "scores": {"automation_comfort": 1}},
            {"value": "condition_save", "label": "조건 저장까지 자동화", "scores": {"automation_comfort": 2}},
            {"value": "paper_auto", "label": "모의 자동화까지 허용", "scores": {"automation_comfort": 3}},
            {"value": "limited_live", "label": "한도 내 실거래 자동화도 검토", "scores": {"automation_comfort": 4}},
        ],
    },
    {
        "id": "approval_preference",
        "title": "승인 방식",
        "kind": "single",
        "required": True,
        "options": [
            {"value": "every_time", "label": "매번 사람 승인", "scores": {"automation_comfort": 0}},
            {"value": "playbook", "label": "정해진 조건 안에서만 자동 승인", "scores": {"automation_comfort": 2}},
            {"value": "stop_on_loss", "label": "손실/이상징후 때만 멈춤", "scores": {"automation_comfort": 3}},
        ],
    },
    {
        "id": "product_preference",
        "title": "선호 상품",
        "kind": "multi",
        "required": True,
        "options": [
            {"value": "cash", "label": "현금성"},
            {"value": "etf", "label": "ETF"},
            {"value": "large_cap", "label": "대형주"},
            {"value": "dividend", "label": "배당주"},
            {"value": "growth", "label": "성장주", "scores": {"risk_tolerance": 1}},
            {"value": "theme", "label": "테마주", "scores": {"risk_tolerance": 1}},
            {"value": "leveraged", "label": "레버리지/인버스", "scores": {"risk_tolerance": 2, "knowledge": 1}},
        ],
    },
    {
        "id": "discomfort",
        "title": "불편한 상황",
        "kind": "multi",
        "required": True,
        "options": [
            {"value": "frequent_trading", "label": "잦은 거래"},
            {"value": "long_drawdown", "label": "긴 손실 구간"},
            {"value": "intraday_volatility", "label": "큰 일중 변동"},
            {"value": "weak_explanation", "label": "설명 부족"},
            {"value": "too_many_alerts", "label": "알림 과다"},
        ],
    },
    {
        "id": "satisfaction_focus",
        "title": "만족 기준",
        "kind": "multi",
        "required": True,
        "options": [
            {"value": "absolute_return", "label": "절대수익"},
            {"value": "benchmark", "label": "시장 대비 성과"},
            {"value": "low_volatility", "label": "낮은 변동성"},
            {"value": "plan_adherence", "label": "계획 준수"},
            {"value": "explainability", "label": "이해 가능한 설명"},
            {"value": "time_saved", "label": "시간 절약"},
        ],
    },
    {
        "id": "final_ack",
        "title": "최종 확인",
        "kind": "acknowledgement",
        "required": True,
        "options": [
            {
                "value": "acknowledged",
                "label": "수익 보장이나 투자 권유가 아니며, 자동화는 내가 정한 한도와 승인 흐름 안에서만 동작함을 확인합니다.",
            }
        ],
    },
]


def username_from_session(session: dict[str, Any]) -> str:
    """Stable per-user key for this single-owner product."""
    return str(session.get("username") or "owner")


def survey_definition() -> dict[str, Any]:
    return {
        "version": SURVEY_VERSION,
        "questions": [_public_question(question) for question in _QUESTIONS],
    }


def get_profile(username: str) -> dict[str, Any]:
    _ensure_tables()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM investor_profiles WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None:
        return _default_profile(username)
    return _row_to_profile(dict(row))


def investor_profile_completed(username: str) -> bool:
    profile = get_profile(username)
    return bool(profile.get("completed"))


def action_gate(username: str, action: str) -> ProfileGate:
    """Return whether an action requiring profile context may proceed."""
    profile = get_profile(username)
    if not profile.get("completed"):
        return ProfileGate(
            allowed=False,
            status="profile_required",
            message="투자 프로필 설문 완료 후 사용할 수 있습니다.",
        )
    if action == "auto_trading" and profile["risk_type"] == "안정형":
        return ProfileGate(
            allowed=False,
            status="profile_override_recommended",
            message="안정형 프로필에서는 자동매매 ON 전 추가 확인이 필요합니다.",
        )
    return ProfileGate(allowed=True, status="passed", message="passed")


def submit_survey(username: str, answers: dict[str, Any]) -> dict[str, Any]:
    normalized = _validate_answers(answers)
    scores = _score_answers(normalized)
    profile = _build_profile(username, normalized, scores)
    _ensure_tables()
    response_json = _json(normalized)
    scores_json = _json(scores)
    profile_json = _json(profile)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO investor_profiles(
                username, survey_version, completed, risk_type, knowledge_level,
                risk_capacity_score, risk_tolerance_score, knowledge_score,
                experience_score, time_horizon_score, automation_comfort_score,
                recommended_max_equity_pct, recommended_autonomy_level,
                needs_advanced_survey, satisfaction_focus, updated_at, completed_at
            )
            VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(username) DO UPDATE SET
                survey_version = excluded.survey_version,
                completed = 1,
                risk_type = excluded.risk_type,
                knowledge_level = excluded.knowledge_level,
                risk_capacity_score = excluded.risk_capacity_score,
                risk_tolerance_score = excluded.risk_tolerance_score,
                knowledge_score = excluded.knowledge_score,
                experience_score = excluded.experience_score,
                time_horizon_score = excluded.time_horizon_score,
                automation_comfort_score = excluded.automation_comfort_score,
                recommended_max_equity_pct = excluded.recommended_max_equity_pct,
                recommended_autonomy_level = excluded.recommended_autonomy_level,
                needs_advanced_survey = excluded.needs_advanced_survey,
                satisfaction_focus = excluded.satisfaction_focus,
                updated_at = CURRENT_TIMESTAMP,
                completed_at = CURRENT_TIMESTAMP
            """,
            (
                username,
                SURVEY_VERSION,
                profile["risk_type"],
                profile["knowledge_level"],
                scores["risk_capacity"],
                scores["risk_tolerance"],
                scores["knowledge"],
                scores["experience"],
                scores["time_horizon"],
                scores["automation_comfort"],
                profile["recommended_max_equity_pct"],
                profile["recommended_autonomy_level"],
                int(profile["needs_advanced_survey"]),
                _json(profile["satisfaction_focus"]),
            ),
        )
        conn.execute(
            """
            INSERT INTO investor_survey_responses(
                username, survey_version, response_json, scores_json, profile_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, SURVEY_VERSION, response_json, scores_json, profile_json),
        )
    return get_profile(username)


def record_override_acknowledgement(
    username: str,
    *,
    action: str,
    reason: str,
    acknowledgement_text: str,
    symbol: str | None = None,
) -> dict[str, Any]:
    _ensure_tables()
    profile = get_profile(username)
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO investor_override_acknowledgements(
                username, symbol, action, reason, acknowledgement_text,
                profile_version, profile_snapshot_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                symbol,
                action,
                reason,
                acknowledgement_text,
                profile.get("survey_version") or SURVEY_VERSION,
                _json(profile),
            ),
        )
        ack_id = int(cur.lastrowid)
    return {"id": ack_id, "status": "recorded"}


def record_checkin(
    username: str,
    *,
    trigger_type: str,
    satisfaction_score: int,
    confidence_score: int,
    stress_score: int,
    automation_adjustment: str,
    notes: str | None = None,
) -> dict[str, Any]:
    if not investor_profile_completed(username):
        raise SurveyValidationError("투자 프로필 설문 완료 후 체크인을 저장할 수 있습니다.")
    _validate_score("satisfaction_score", satisfaction_score)
    _validate_score("confidence_score", confidence_score)
    _validate_score("stress_score", stress_score)
    if automation_adjustment not in {"lower", "same", "raise"}:
        raise SurveyValidationError("automation_adjustment must be lower, same, or raise")
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO investor_checkins(
                username, trigger_type, satisfaction_score, confidence_score,
                stress_score, automation_adjustment, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                trigger_type,
                satisfaction_score,
                confidence_score,
                stress_score,
                automation_adjustment,
                notes,
            ),
        )
        checkin_id = int(cur.lastrowid)
        conn.execute(
            """
            UPDATE investor_profiles
            SET last_checkin_at = CURRENT_TIMESTAMP,
                satisfaction_score = ?,
                confidence_score = ?,
                stress_score = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (satisfaction_score, confidence_score, stress_score, username),
        )
    return {"id": checkin_id, "status": "recorded", "profile": get_profile(username)}


def _ensure_tables() -> None:
    with get_connection() as conn:
        conn.executescript(_TABLE_SQL)


def _validate_answers(answers: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(answers, dict):
        raise SurveyValidationError("answers must be an object")
    normalized: dict[str, Any] = {}
    for question in _QUESTIONS:
        qid = question["id"]
        if question.get("required") and qid not in answers:
            raise SurveyValidationError(f"{qid} is required")
        value = answers.get(qid)
        options = {option["value"] for option in question.get("options", [])}
        kind = question["kind"]
        if kind == "single":
            if value not in options:
                raise SurveyValidationError(f"{qid} has an invalid option")
            normalized[qid] = value
        elif kind == "multi":
            if not isinstance(value, list) or not value:
                raise SurveyValidationError(f"{qid} requires at least one option")
            invalid = [item for item in value if item not in options]
            if invalid:
                raise SurveyValidationError(f"{qid} has invalid option(s): {invalid}")
            normalized[qid] = sorted(set(value), key=value.index)
        elif kind == "acknowledgement":
            if value not in (True, "acknowledged"):
                raise SurveyValidationError(f"{qid} must be acknowledged")
            normalized[qid] = "acknowledged"
    return normalized


def _score_answers(answers: dict[str, Any]) -> dict[str, float]:
    totals = {axis: 0.0 for axis in AXES}
    max_totals = {axis: 0.0 for axis in AXES}
    for question in _QUESTIONS:
        option_map = {option["value"]: option for option in question.get("options", [])}
        values = answers.get(question["id"])
        selected = values if isinstance(values, list) else [values]
        if question["kind"] == "multi":
            for option in question.get("options", []):
                for axis, value in option.get("scores", {}).items():
                    max_totals[axis] += max(0.0, float(value))
        else:
            axis_max = {axis: 0.0 for axis in AXES}
            for option in question.get("options", []):
                for axis, value in option.get("scores", {}).items():
                    axis_max[axis] = max(axis_max[axis], float(value))
            for axis, value in axis_max.items():
                max_totals[axis] += max(0.0, value)
        for value in selected:
            option = option_map.get(value)
            if not option:
                continue
            for axis, score in option.get("scores", {}).items():
                totals[axis] += float(score)
    return {
        axis: round((totals[axis] / max_totals[axis]) * 100, 1) if max_totals[axis] else 0.0
        for axis in AXES
    }


def _build_profile(username: str, answers: dict[str, Any], scores: dict[str, float]) -> dict[str, Any]:
    composite = (
        scores["risk_capacity"] * 0.25
        + scores["risk_tolerance"] * 0.25
        + scores["time_horizon"] * 0.15
        + scores["experience"] * 0.15
        + scores["knowledge"] * 0.10
        + scores["automation_comfort"] * 0.10
    )
    risk_type = _risk_type(composite)
    knowledge_level = _knowledge_level(scores["knowledge"], scores["experience"])
    satisfaction_focus = _labels_for_answers("satisfaction_focus", answers.get("satisfaction_focus", []))
    return {
        "username": username,
        "survey_version": SURVEY_VERSION,
        "completed": True,
        "risk_type": risk_type,
        "knowledge_level": knowledge_level,
        "scores": scores,
        "recommended_max_equity_pct": _equity_cap(risk_type),
        "recommended_autonomy_level": _autonomy_level(risk_type),
        "needs_advanced_survey": scores["knowledge"] >= 70 or scores["experience"] >= 70,
        "satisfaction_focus": satisfaction_focus,
        "last_checkin_at": None,
        "satisfaction_score": None,
        "confidence_score": None,
        "stress_score": None,
    }


def _risk_type(composite: float) -> str:
    if composite < 25:
        return "안정형"
    if composite < 45:
        return "안정추구형"
    if composite < 65:
        return "위험중립형"
    if composite < 82:
        return "적극투자형"
    return "공격투자형"


def _knowledge_level(knowledge: float, experience: float) -> str:
    blended = knowledge * 0.7 + experience * 0.3
    if blended < 25:
        return "입문"
    if blended < 50:
        return "기초"
    if blended < 75:
        return "경험자"
    return "전문가"


def _equity_cap(risk_type: str) -> int:
    return {
        "안정형": 20,
        "안정추구형": 40,
        "위험중립형": 60,
        "적극투자형": 80,
        "공격투자형": 100,
    }[risk_type]


def _autonomy_level(risk_type: str) -> str:
    return {
        "안정형": "L1",
        "안정추구형": "L1",
        "위험중립형": "L2",
        "적극투자형": "L3",
        "공격투자형": "L3",
    }[risk_type]


def _row_to_profile(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "username": row["username"],
        "survey_version": row["survey_version"],
        "completed": bool(row["completed"]),
        "risk_type": row["risk_type"],
        "knowledge_level": row["knowledge_level"],
        "scores": {
            "risk_capacity": float(row["risk_capacity_score"]),
            "risk_tolerance": float(row["risk_tolerance_score"]),
            "knowledge": float(row["knowledge_score"]),
            "experience": float(row["experience_score"]),
            "time_horizon": float(row["time_horizon_score"]),
            "automation_comfort": float(row["automation_comfort_score"]),
        },
        "recommended_max_equity_pct": int(row["recommended_max_equity_pct"]),
        "recommended_autonomy_level": row["recommended_autonomy_level"],
        "needs_advanced_survey": bool(row["needs_advanced_survey"]),
        "satisfaction_focus": _loads_list(row["satisfaction_focus"]),
        "last_checkin_at": row["last_checkin_at"],
        "satisfaction_score": row["satisfaction_score"],
        "confidence_score": row["confidence_score"],
        "stress_score": row["stress_score"],
        "updated_at": row["updated_at"],
        "completed_at": row["completed_at"],
    }


def _default_profile(username: str) -> dict[str, Any]:
    return {
        "username": username,
        "survey_version": SURVEY_VERSION,
        "completed": False,
        "risk_type": "미완료",
        "knowledge_level": "미확인",
        "scores": {axis: 0.0 for axis in AXES},
        "recommended_max_equity_pct": 0,
        "recommended_autonomy_level": "L0",
        "needs_advanced_survey": False,
        "satisfaction_focus": [],
        "last_checkin_at": None,
        "satisfaction_score": None,
        "confidence_score": None,
        "stress_score": None,
        "updated_at": None,
        "completed_at": None,
    }


def _public_question(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": question["id"],
        "title": question["title"],
        "kind": question["kind"],
        "required": bool(question.get("required")),
        "options": [
            {
                "value": option["value"],
                "label": option["label"],
            }
            for option in question.get("options", [])
        ],
    }


def _labels_for_answers(question_id: str, values: list[str]) -> list[str]:
    question = next(q for q in _QUESTIONS if q["id"] == question_id)
    labels = {option["value"]: option["label"] for option in question["options"]}
    return [labels[value] for value in values if value in labels]


def _loads_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
    except json.JSONDecodeError:
        return []
    return loaded if isinstance(loaded, list) else []


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _validate_score(name: str, value: int) -> None:
    if value < 1 or value > 5:
        raise SurveyValidationError(f"{name} must be between 1 and 5")
