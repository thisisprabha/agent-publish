"""Markdown to HTML conversion with agent-friendly defaults."""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions import fenced_code, tables, toc


@dataclass
class ConversionResult:
    html: str
    title: str
    fingerprint: str
    output_path: Path
    assets_copied: List[Path] = field(default_factory=list)


def _generate_fingerprint(content: str) -> str:
    """Generate content fingerprint for cache-busting."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _extract_title(md_content: str) -> str:
    """Extract title from first h1 or use default."""
    match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"


def _safe_format(template: str, **kwargs) -> str:
    """Replace {key} placeholders safely without interpreting other braces."""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def _clean_slug(title: str) -> str:
    """Generate URL-safe slug from title."""
    # Strip common prefixes
    cleaned = re.sub(
        r'^(Cron Job:|Research Report:|Daily:|Weekly:)\s*',
        '', title, flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s*[-:]\s*',
        '', cleaned,
    )
    # Clean special chars
    slug = re.sub(r'[^a-zA-Z0-9\s-]', ' ', cleaned.strip())
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-').lower()[:60]
    return slug if slug else "untitled"


DEFAULT_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<a href="#main-content" class="skip-link">Skip to content</a>
<a href="../" class="back">&larr; Back</a>

<header>
  <h1>{title}</h1>
  <p class="meta">{entry_type} &middot; {date} &middot; <code>{fingerprint}</code></p>
</header>

<main class="main" id="main-content">
{body}
</main>
</body>
</html>'''


def convert_file(
    input_path: Path,
    output_dir: Path,
    entry_type: str = "daily",
    custom_css: Optional[str] = None,
    custom_css_path: Optional[Path] = None,
    template_override: Optional[Path] = None,
    date_str: Optional[str] = None,
) -> ConversionResult:
    """Convert markdown file to HTML.

    Args:
        input_path: Path to input markdown file
        output_dir: Directory for output HTML
        entry_type: Category for metadata (daily, weekly, etc.)
        custom_css: Optional custom CSS string to override default
        custom_css_path: Optional path to custom CSS file (takes precedence over custom_css)
        template_override: Optional path to template file with {title}, {css}, {fingerprint}, {date}, {body}, {entry_type} placeholders
        date_str: Optional date string (defaults to today)

    Returns:
        ConversionResult with HTML content and metadata
    """
    from pygments.formatters.html import HtmlFormatter
    from agent_publish.themes import DEFAULT_CSS

    md_content = input_path.read_text(encoding='utf-8')

    # Extract title and fingerprint
    title = _extract_title(md_content)
    fingerprint = _generate_fingerprint(md_content)

    # Parse markdown with syntax highlighting
    md = markdown.Markdown(extensions=[
        fenced_code.FencedCodeExtension(),
        CodeHiliteExtension(linenums=False, guess_lang=False),
        tables.TableExtension(),
        toc.TocExtension(),
    ])

    html_body = md.convert(md_content)
    toc_html = md.toc if hasattr(md, 'toc') else ""  # type: ignore[attr-defined]

    # If TOC has at least 2 entries (meaningful nav), wrap and prepend
    if toc_html and toc_html.count('<a href="#') >= 2:
        toc_nav = f'<nav class="toc">{toc_html}</nav>\n'
        html_body = toc_nav + html_body

    # Resolve CSS
    if custom_css_path and custom_css_path.exists():
        css = custom_css_path.read_text(encoding='utf-8')
    else:
        css = custom_css or DEFAULT_CSS

    # Inline pygments CSS for syntax highlighting
    pyg_css = HtmlFormatter(style="default").get_style_defs(".codehilite")
    css = css + "\n" + pyg_css

    date = date_str or __import__('datetime').datetime.now().strftime("%Y-%m-%d")
    slug = _clean_slug(title)

    # Resolve template
    if template_override and template_override.exists():
        template = template_override.read_text(encoding='utf-8')
    else:
        template = DEFAULT_TEMPLATE

    html = _safe_format(
        template,
        title=title,
        css=css,
        fingerprint=fingerprint,
        date=date,
        body=html_body,
        entry_type=entry_type.capitalize(),
    )

    from agent_publish.assets import copy_assets

    html, assets_copied = copy_assets(html, base_dir=input_path.parent, output_dir=output_dir)

    output_name = f"{date}-{slug}.html"
    output_path = output_dir / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')

    return ConversionResult(
        html=html,
        title=title,
        fingerprint=fingerprint,
        output_path=output_path,
        assets_copied=assets_copied,
    )
