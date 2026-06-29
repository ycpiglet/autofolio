from __future__ import annotations

import pytest

from app.research.insights import generate_insight_candidates
from app.research.live_fetchers import fetch_official_rss_feed, parse_official_rss_items
from app.research.policy import PolicyReason


RSS_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Official Notices</title>
    <item>
      <title>Market volatility notice</title>
      <link>https://example.test/notices/1</link>
      <pubDate>Mon, 29 Jun 2026 09:00:00 +0900</pubDate>
      <description><![CDATA[<p>Official notice summary.</p>]]></description>
      <guid>notice-1</guid>
    </item>
  </channel>
</rss>
"""


ATOM_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Official Atom Feed</title>
  <entry>
    <title>Atom disclosure update</title>
    <link href="https://example.test/atom/1" />
    <updated>2026-06-29T10:00:00+09:00</updated>
    <summary>Atom summary.</summary>
  </entry>
</feed>
"""


def test_parse_official_rss_items_parses_rss_without_network() -> None:
    items = parse_official_rss_items(RSS_SAMPLE, feed_url="https://example.test/rss.xml")

    assert len(items) == 1
    assert items[0]["title"] == "Market volatility notice"
    assert items[0]["summary"] == "Official notice summary."
    assert items[0]["url"] == "https://example.test/notices/1"
    assert items[0]["as_of_date"] == "2026-06-29"


def test_parse_official_rss_items_parses_atom_without_network() -> None:
    items = parse_official_rss_items(ATOM_SAMPLE, feed_url="https://example.test/atom.xml")

    assert len(items) == 1
    assert items[0]["title"] == "Atom disclosure update"
    assert items[0]["summary"] == "Atom summary."
    assert items[0]["url"] == "https://example.test/atom/1"
    assert items[0]["as_of_date"] == "2026-06-29"


def test_fetch_official_rss_feed_requires_approval_before_fetch() -> None:
    called = {"fetch": 0}

    def fail_fetch(url: str, timeout: float) -> str:  # noqa: ARG001
        called["fetch"] += 1
        raise AssertionError("fetch should not run before approval")

    result = fetch_official_rss_feed(
        source_id="regulator_rss",
        feed_url="https://example.test/rss.xml",
        approval_ref=None,
        fetch_text=fail_fetch,
    )

    assert result.allowed is False
    assert result.policy.reason is PolicyReason.OWNER_APPROVAL_REQUIRED
    assert called["fetch"] == 0


def test_fetch_official_rss_feed_converts_approved_feed_to_documents() -> None:
    result = fetch_official_rss_feed(
        source_id="regulator_rss",
        feed_url="https://example.test/rss.xml",
        approval_ref="Owner-approved official RSS source",
        collected_at="2026-06-29T10:30:00Z",
        fetch_text=lambda url, timeout: RSS_SAMPLE,  # noqa: ARG005
    )

    assert result.allowed is True
    assert result.warnings == ()
    assert len(result.documents) == 1
    doc = result.documents[0]
    assert doc.source_id == "regulator_rss"
    assert doc.title == "Market volatility notice"
    assert doc.url == "https://example.test/notices/1"
    assert doc.metadata["event_type"] == "official_feed_update"

    candidates = generate_insight_candidates(result.documents)
    assert len(candidates) == 1
    assert candidates[0].not_investment_advice is True


def test_fetch_official_rss_feed_blocks_embedded_credentials() -> None:
    result = fetch_official_rss_feed(
        source_id="regulator_rss",
        feed_url="https://user:pass@example.test/rss.xml",
        approval_ref="Owner-approved official RSS source",
        fetch_text=lambda url, timeout: RSS_SAMPLE,  # noqa: ARG005
    )

    assert result.allowed is False
    assert result.policy.reason is PolicyReason.FORBIDDEN_BOUNDARY
    assert "credentials" in result.policy.message


_XXE_PAYLOAD = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE rss [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<rss version="2.0">
  <channel>
    <title>&xxe;</title>
    <item><title>Injected</title></item>
  </channel>
</rss>
"""

_BILLION_LAUGHS_PAYLOAD = """\
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<rss version="2.0">
  <channel><title>&lol9;</title></channel>
</rss>
"""


def test_parse_official_rss_items_rejects_xxe_payload() -> None:
    """External-entity (XXE) XML must be rejected with ValueError, not expanded."""
    with pytest.raises(ValueError):
        parse_official_rss_items(_XXE_PAYLOAD)

    # Confirm the file content was NOT read into memory
    result_str = str(_XXE_PAYLOAD)
    assert "root:" not in result_str


def test_parse_official_rss_items_rejects_billion_laughs_payload() -> None:
    """Entity-expansion (billion-laughs) XML must be rejected with ValueError."""
    with pytest.raises(ValueError):
        parse_official_rss_items(_BILLION_LAUGHS_PAYLOAD)


def test_fetch_official_rss_feed_blocks_unenabled_source_id() -> None:
    result = fetch_official_rss_feed(
        source_id="dart",
        feed_url="https://example.test/rss.xml",
        approval_ref="Owner-approved official source",
        fetch_text=lambda url, timeout: RSS_SAMPLE,  # noqa: ARG005
    )

    assert result.allowed is False
    assert result.policy.reason in {PolicyReason.METHOD_NOT_ALLOWED, PolicyReason.FORBIDDEN_BOUNDARY}

