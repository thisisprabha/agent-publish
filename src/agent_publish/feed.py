"""Generate RSS feed (feed.xml) for published entries."""

import email.utils
from datetime import datetime, timezone
from pathlib import Path


def _to_rfc822(date_str: str) -> str:
    """Convert YYYY-MM-DD or YYYY-MM-DD HH:MM:SS to RFC-822."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return email.utils.format_datetime(dt.replace(tzinfo=timezone.utc), usegmt=True)
        except ValueError:
            continue
    return date_str


def _item_xml(entry: dict, base_url: str) -> str:
    """Return RSS <item> for a single entry."""
    title = entry["title"]
    slug = entry["slug"]
    url = f"{base_url.rstrip('/')}/{slug}.html" if base_url else f"{slug}.html"
    date = _to_rfc822(entry.get("date", ""))
    return (
        f"  <item>\n"
        f"    <title>{title}</title>\n"
        f"    <link>{url}</link>\n"
        f"    <guid isPermaLink=\"false\">{entry.get('fingerprint', slug)}</guid>\n"
        f"    <pubDate>{date}</pubDate>\n"
        f"  </item>\n"
    )


def generate_rss_feed(
    *,
    entries: list[dict],
    out_dir: Path,
    site_title: str,
    base_url: str,
    description: str = "",
) -> Path:
    """Generate feed.xml into *out_dir*.

    *entries* is a list of dicts with keys: title, slug, date, url, fingerprint.
    """
    now = email.utils.format_datetime(datetime.now(timezone.utc), usegmt=True)
    items = "".join(_item_xml(e, base_url) for e in entries)
    self_link = f"{base_url.rstrip('/')}/feed.xml" if base_url else "feed.xml"
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        f'    <title>{site_title}</title>\n'
        f'    <link>{base_url}</link>\n'
        f'    <description>{description}</description>\n'
        f'    <lastBuildDate>{now}</lastBuildDate>\n'
        '    <generator>agent-publish</generator>\n'
        f'    <atom:link href="{self_link}" rel="self" type="application/rss+xml" />\n'
        f'{items}'
        '  </channel>\n'
        '</rss>\n'
    )
    out_path = out_dir / "feed.xml"
    out_path.write_text(xml, encoding="utf-8")
    return out_path
