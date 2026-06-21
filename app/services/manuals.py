"""Manual asset loader for in-app product guidance."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


MANUAL_ROOT = Path(__file__).resolve().parents[2] / "docs" / "manuals"


@dataclass(frozen=True)
class ManualAsset:
    slug: str
    metadata: dict[str, Any]
    content: str

    @property
    def title(self) -> str:
        return str(self.metadata.get("title") or self.slug)

    @property
    def visibility(self) -> str:
        return str(self.metadata.get("visibility") or "public")

    @property
    def order(self) -> int:
        raw = self.metadata.get("order", 999)
        try:
            return int(raw)
        except (TypeError, ValueError):
            return 999


def list_manuals(*, include_private: bool = False) -> list[dict[str, Any]]:
    assets = [_load_manual(path) for path in _manual_paths()]
    visible = [
        asset
        for asset in assets
        if include_private or asset.visibility == "public"
    ]
    return [_summary(asset) for asset in sorted(visible, key=lambda item: (item.order, item.slug))]


def get_manual(slug: str, *, include_private: bool = False) -> dict[str, Any]:
    safe_slug = _safe_slug(slug)
    path = MANUAL_ROOT / f"{safe_slug}.md"
    if not path.exists():
        raise FileNotFoundError(safe_slug)
    asset = _load_manual(path)
    if asset.visibility != "public" and not include_private:
        raise PermissionError(safe_slug)
    return {
        **_summary(asset),
        "content": asset.content,
        "metadata": asset.metadata,
    }


def _manual_paths() -> list[Path]:
    if not MANUAL_ROOT.exists():
        return []
    return sorted(path for path in MANUAL_ROOT.glob("*.md") if path.is_file())


def _load_manual(path: Path) -> ManualAsset:
    raw = path.read_text(encoding="utf-8")
    metadata, content = _split_frontmatter(raw)
    return ManualAsset(slug=path.stem, metadata=metadata, content=content.strip())


def _split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        return {}, raw
    end = raw.find("\n---\n", 4)
    if end == -1:
        return {}, raw
    header = raw[4:end]
    content = raw[end + len("\n---\n") :]
    return _parse_simple_yaml(header), content


def _parse_simple_yaml(header: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for line in header.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        metadata[key.strip()] = _parse_scalar(value.strip())
    return metadata


def _parse_scalar(value: str) -> Any:
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [
            item.strip().strip('"').strip("'")
            for item in inner.split(",")
            if item.strip()
        ]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def _summary(asset: ManualAsset) -> dict[str, Any]:
    return {
        "slug": asset.slug,
        "title": asset.title,
        "description": asset.metadata.get("description", ""),
        "audience": asset.metadata.get("audience", "all"),
        "visibility": asset.visibility,
        "ui_section": asset.metadata.get("ui_section", "manuals"),
        "risk_level": asset.metadata.get("risk_level", "low"),
        "requires_ack": bool(asset.metadata.get("requires_ack", False)),
        "ack_kind": asset.metadata.get("ack_kind"),
        "version": asset.metadata.get("version", "manuals-v1"),
        "order": asset.order,
    }


def _safe_slug(slug: str) -> str:
    safe = "".join(ch for ch in slug if ch.isalnum() or ch in {"-", "_"})
    if not safe or safe != slug:
        raise FileNotFoundError(slug)
    return safe
