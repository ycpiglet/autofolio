"""Portfolio metadata repository tests."""
from __future__ import annotations

from app.database.repositories import Repository
from app.database.sqlite_db import initialize_database


def test_portfolio_group_crud_roundtrip(tmp_path):
    db_path = tmp_path / "portfolio-groups.db"
    initialize_database(db_path)
    repo = Repository(db_path)

    created = repo.create_portfolio_group(
        name="코어",
        symbols=["005930", "005930", "069500"],
        description="core holdings",
    )

    assert created["name"] == "코어"
    assert created["symbols"] == ["005930", "069500"]

    group_id = created["group_id"]
    updated = repo.update_portfolio_group(
        group_id,
        name="코어 ETF",
        symbols=["069500"],
    )

    assert updated is not None
    assert updated["name"] == "코어 ETF"
    assert updated["symbols"] == ["069500"]
    assert repo.delete_portfolio_group(group_id) is True
    assert repo.list_portfolio_groups() == []


def test_portfolio_symbol_alias_roundtrip(tmp_path):
    db_path = tmp_path / "portfolio-alias.db"
    initialize_database(db_path)
    repo = Repository(db_path)

    repo.upsert_portfolio_symbol_alias(
        symbol="000660",
        name="SK하이닉스",
        asset_class="주식",
        sector="반도체",
        strategy="성장",
        risk_bucket="코어",
    )

    aliases = repo.list_portfolio_symbol_aliases()
    assert aliases[0]["symbol"] == "000660"
    assert aliases[0]["name"] == "SK하이닉스"
    assert aliases[0]["sector"] == "반도체"
