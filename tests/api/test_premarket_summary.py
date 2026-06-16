"""Premarket summary service/API tests."""
from __future__ import annotations

from pathlib import Path


def test_generate_summary_writes_markdown(tmp_path, mock_backend, monkeypatch):
    import app.services.premarket_summary as ps

    monkeypatch.setattr(ps, "PREMARKET_DIR", tmp_path)
    result = ps.generate_summary(target_date="2026-06-16", save=True, limit_symbols=2)

    path = Path(result["path"])
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "프리마켓 핵심 요약" in content
    assert "정규장 시작 전" in content
    assert "리서치·금융 전문가 에이전트" in content
    assert "005930" in content


def test_load_summary_returns_latest(tmp_path, mock_backend, monkeypatch):
    import app.services.premarket_summary as ps

    monkeypatch.setattr(ps, "PREMARKET_DIR", tmp_path)
    ps.generate_summary(target_date="2026-06-15", save=True)
    ps.generate_summary(target_date="2026-06-16", save=True)

    loaded = ps.load_summary()
    assert loaded is not None
    assert loaded["date"] == "2026-06-16"
    assert loaded["file"] == "PREMARKET_20260616.md"
    assert loaded["highlights"]


def test_premarket_summary_api_requires_session(client):
    resp = client.get("/api/agents/premarket/summary")
    assert resp.status_code == 401


def test_premarket_summary_api_loads_file(guest_client, tmp_path, mock_backend, monkeypatch):
    import app.services.premarket_summary as ps

    monkeypatch.setattr(ps, "PREMARKET_DIR", tmp_path)
    ps.generate_summary(target_date="2026-06-16", save=True)

    resp = guest_client.get("/api/agents/premarket/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["date"] == "2026-06-16"
    assert body["file"] == "PREMARKET_20260616.md"
    assert "프리마켓 핵심 요약" in body["content"]
    assert body["agents"]


def test_premarket_summary_api_404_when_missing(guest_client, tmp_path, monkeypatch):
    import app.services.premarket_summary as ps

    monkeypatch.setattr(ps, "PREMARKET_DIR", tmp_path)
    resp = guest_client.get("/api/agents/premarket/summary")
    assert resp.status_code == 404
