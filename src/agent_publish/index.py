"""Generate index.html and feed.xml for published entries."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import feed as feed_mod
from .themes import THEMES


DEFAULT_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{site_title}</title>
  <style>
    {css}
    body {{ max-width: 720px; margin: 0 auto; padding: 2rem 1rem; font-family: system-ui, sans-serif; }}
    header {{ margin-bottom: 2rem; }}
    h1 {{ font-size: 2rem; margin: 0 0 0.25rem; }}
    .meta {{ color: #555; font-size: 0.9rem; }}
    .entry-list {{ list-style: none; padding: 0; margin: 0; }}
    .entry-list li {{ border-bottom: 1px solid #e0e0e0; padding: 1rem 0; }}
    .entry-list a {{ text-decoration: none; color: inherit; font-weight: 600; font-size: 1.1rem; }}
    .entry-list a:hover {{ text-decoration: underline; }}
    .entry-date {{ color: #777; font-size: 0.85rem; margin-top: 0.25rem; }}
    .empty {{ color: #666; font-style: italic; }}
    @media (max-width: 640px) {{
      body {{ padding: 1rem 0.75rem; }}
      h1 {{ font-size: 1.5rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{site_title}</h1>
    <p class="meta">{entry_count} entries</p>
  </header>
  <main>
    {entries_html}{empty_msg}
  </main>
</body>
</html>
"""


def _entry_li(entry: dict, base_url: str) -> str:
    """Return HTML <li> for a single entry."""
    slug = entry["slug"]
    # Build relative or absolute link
    href = entry.get("url") or (f"{base_url.rstrip('/')}/{slug}.html" if base_url else f"{slug}.html")
    date = entry.get("date", "")
    date_html = f'<p class="entry-date">{date}</p>' if date else ""
    return f'<li><a href="{href}">{entry["title"]}</a>{date_html}</li>'


def generate_index_page(
    *,
    entries: list[dict],
    out_dir: Path,
    site_title: str,
    theme: str = "default",
    base_url: str = "",
) -> Path:
    """Generate index.html into *out_dir*."""
    css = THEMES.get(theme, THEMES["default"])
    if entries:
        entries_html = '<ul class="entry-list">\n' + "\n".join(_entry_li(e, base_url) for e in entries) + '\n</ul>'
        empty_msg = ""
        count_str = str(len(entries))
    else:
        entries_html = ""
        empty_msg = '<p class="empty">No entries published yet.</p>'
        count_str = "0"

    html = DEFAULT_INDEX_TEMPLATE.format(
        site_title=site_title,
        css=css,
        entries_html=entries_html,
        empty_msg=empty_msg,
        entry_count=count_str,
    )
    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _scan_entries(output_dir: Path, base_url: str) -> list[dict]:
    """Scan *output_dir* for .html files and build entry metadata."""
    entries = []
    _TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
    for html_file in sorted(output_dir.glob("*.html"), reverse=True):
        if html_file.name == "index.html":
            continue
        text = html_file.read_text(encoding="utf-8")
        m = _TITLE_RE.search(text)
        title = m.group(1) if m else html_file.stem.replace("-", " ").title()
        slug = html_file.stem
        mtime = html_file.stat().st_mtime
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        url = f"{base_url.rstrip('/')}/{slug}.html" if base_url else f"{slug}.html"
        entries.append({
            "title": title,
            "slug": slug,
            "date": date_str,
            "url": url,
            "fingerprint": "",
        })
    return entries


class IndexGenerator:
    """Back-compat wrapper that scans a directory and regenerates index + feed."""

    def __init__(self, output_dir: Path, base_url: str = "", theme_css: str | None = None):
        self.output_dir = output_dir
        self.base_url = base_url.rstrip("/")
        self.theme_css = theme_css

    def generate_index(self, site_title: str = "Published Articles") -> Path:
        """Regenerate index.html from existing HTML files."""
        entries = _scan_entries(self.output_dir, self.base_url)
        return generate_index_page(
            entries=entries,
            out_dir=self.output_dir,
            site_title=site_title,
            theme="default",
            base_url=self.base_url,
        )

    def generate_feed(self, site_title: str = "Published Articles", site_url: str = "") -> Path:
        """Regenerate feed.xml from existing HTML files."""
        entries = _scan_entries(self.output_dir, self.base_url)
        return feed_mod.generate_rss_feed(
            entries=entries,
            out_dir=self.output_dir,
            site_title=site_title,
            base_url=site_url or self.base_url,
            description=f"Feed for {site_title}",
        )


def generate_index_and_feed(
    output_dir: Path,
    base_url: str = "",
    site_title: str = "Published Articles",
    theme_css: str | None = None,
) -> tuple[Path, Path]:
    """Convenience function that regenerates index.html and feed.xml.

    Returns (index_path, feed_path)."""
    gen = IndexGenerator(
        output_dir=output_dir,
        base_url=base_url,
        theme_css=theme_css,
    )
    idx = gen.generate_index(site_title=site_title)
    feed = gen.generate_feed(site_title=site_title, site_url=base_url)
    return idx, feed
