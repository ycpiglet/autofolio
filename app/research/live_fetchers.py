"""Policy-gated read-only live fetchers for official research sources."""

from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import fromstring as _safe_fromstring
from typing import Callable
from urllib.parse import urlparse

from app.research.collectors import CollectionResult
from app.research.official_collectors import collect_official_source_items
from app.research.policy import CollectionRequest, PolicyDecision, PolicyReason, evaluate_collection_request
from app.research.source_registry import BodyStoragePolicy, IngestionMethod, get_source

FetchText = Callable[[str, float], str]

_ALLOWED_RSS_SOURCE_IDS = {"regulator_rss", "company_ir"}


def fetch_official_rss_feed(
    *,
    source_id: str,
    feed_url: str,
    approval_ref: str | None,
    timeout: float = 10.0,
    collected_at: str = "",
    fetch_text: FetchText | None = None,
    max_items: int = 20,
) -> CollectionResult:
    """Fetch and normalize an approved official RSS/Atom feed.

    The policy gate is evaluated before any network call. Tests can pass
    ``fetch_text`` to avoid network I/O.
    """

    policy = evaluate_collection_request(
        CollectionRequest(
            source_id=source_id,
            method=IngestionMethod.RSS,
            storage_policy=BodyStoragePolicy.SUMMARY_ONLY,
            approval_ref=approval_ref,
        )
    )
    if not policy.allowed:
        return CollectionResult(policy=policy, documents=(), warnings=(policy.message,))

    boundary_warning = _validate_feed_boundary(source_id=source_id, feed_url=feed_url)
    if boundary_warning:
        blocked = PolicyDecision(
            allowed=False,
            reason=PolicyReason.FORBIDDEN_BOUNDARY,
            message=boundary_warning,
            source=get_source(source_id),
        )
        return CollectionResult(policy=blocked, documents=(), warnings=(boundary_warning,))

    reader = fetch_text or _urllib_fetch_text
    try:
        xml_text = reader(feed_url, timeout)
    except Exception as exc:  # noqa: BLE001
        return CollectionResult(policy=policy, documents=(), warnings=(f"{source_id} RSS fetch failed: {exc}",))

    try:
        items = parse_official_rss_items(
            xml_text,
            feed_url=feed_url,
            default_asset_classes=("market_notice",),
            max_items=max_items,
        )
    except ValueError as exc:
        return CollectionResult(policy=policy, documents=(), warnings=(f"{source_id} RSS parse failed: {exc}",))

    return collect_official_source_items(
        source_id=source_id,
        method=IngestionMethod.RSS,
        approval_ref=approval_ref,
        collected_at=collected_at,
        requested_storage=BodyStoragePolicy.SUMMARY_ONLY,
        items=items,
    )


def parse_official_rss_items(
    xml_text: str,
    *,
    feed_url: str = "",
    default_asset_classes: tuple[str, ...] = ("market_notice",),
    max_items: int = 20,
) -> list[dict[str, object]]:
    """Parse RSS 2.0 or Atom entries into generic official-source items."""

    try:
        root = _safe_fromstring(xml_text)
    except (ET.ParseError, DefusedXmlException) as exc:
        raise ValueError(str(exc)) from exc

    entries = _rss_items(root)
    if not entries:
        entries = _atom_entries(root)

    items: list[dict[str, object]] = []
    for entry in entries[: max(0, int(max_items))]:
        title = _text(entry, "title")
        if not title:
            continue
        link = _rss_link(entry) or feed_url
        published = _first_text(entry, ("pubDate", "published", "updated", "dc:date"))
        summary = _strip_markup(_first_text(entry, ("description", "summary", "content", "content:encoded")))
        as_of = _date_from_feed_time(published)
        items.append(
            {
                "title": title,
                "summary": summary[:500] if summary else title,
                "url": link,
                "published_at": published,
                "as_of_date": as_of,
                "entities": (),
                "symbols": (),
                "asset_classes": default_asset_classes,
                "event_type": "official_feed_update",
                "severity": "LOW",
                "keywords": (),
                "provider_document_id": _text(entry, "guid") or link or title,
                "license_notes": "Official RSS/Atom feed metadata converted under Research Source Policy.",
            }
        )
    return items


def _validate_feed_boundary(*, source_id: str, feed_url: str) -> str:
    if source_id not in _ALLOWED_RSS_SOURCE_IDS:
        return f"RSS live fetch is not enabled for source {source_id!r}."
    parsed = urlparse(feed_url)
    if parsed.scheme not in {"http", "https"}:
        return "RSS feed URL must use http or https."
    if parsed.username or parsed.password:
        return "RSS feed URL must not contain embedded credentials."
    if not parsed.netloc:
        return "RSS feed URL must include a host."
    return ""


def _urllib_fetch_text(url: str, timeout: float) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AutofolioResearchMachine/0.1 read-only official-feed collector",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.1",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 - policy-gated URL
        content_type = response.headers.get_content_charset() or "utf-8"
        data = response.read(1_000_000)
    return data.decode(content_type, errors="replace")


def _rss_items(root: ET.Element) -> list[ET.Element]:
    return list(root.findall("./channel/item")) or [elem for elem in root.iter() if _local_name(elem.tag) == "item"]


def _atom_entries(root: ET.Element) -> list[ET.Element]:
    return [elem for elem in root.iter() if _local_name(elem.tag) == "entry"]


def _text(parent: ET.Element, name: str) -> str:
    local = name.split(":", 1)[-1]
    for child in parent:
        if _local_name(child.tag) == local:
            return str(child.text or "").strip()
    return ""


def _first_text(parent: ET.Element, names: tuple[str, ...]) -> str:
    for name in names:
        value = _text(parent, name)
        if value:
            return value
    return ""


def _rss_link(entry: ET.Element) -> str:
    direct = _text(entry, "link")
    if direct:
        return direct
    for child in entry:
        if _local_name(child.tag) == "link":
            href = child.attrib.get("href")
            if href:
                return href.strip()
    return ""


def _strip_markup(value: str) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _date_from_feed_time(value: str) -> str:
    if not value:
        return ""
    text = value.strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError, OverflowError):
        return ""
    return parsed.date().isoformat()


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag

