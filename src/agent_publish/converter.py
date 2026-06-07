"""Markdown to HTML conversion with agent-friendly defaults."""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import markdown
from markdown.extensions import fenced_code, tables, toc
from markdown.extensions.codehilite import CodeHiliteExtension

_FENCE_RE = re.compile(r'^```mermaid\s*\n(.*?)\n?^```', re.MULTILINE | re.DOTALL)


@dataclass
class ConversionResult:
    html: str
    title: str
    fingerprint: str
    output_path: Path
    assets_copied: List[Path] = field(default_factory=list)
    reading_time: int = 1
    description: Optional[str] = None


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


def _calculate_reading_time(md_content: str) -> int:
    """Calculate reading time in minutes at 200 WPM."""
    # Strip code blocks
    text = re.sub(r'```.*?```', '', md_content, flags=re.DOTALL)
    # Strip inline code
    text = re.sub(r'`[^`]*`', '', text)
    # Strip images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Strip links but keep text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Strip remaining markdown syntax
    text = re.sub(r'[#*_>`~]', '', text)
    # Count words
    words = len(text.split())
    return max(1, round(words / 200))


def _extract_description(html_body: str) -> str:
    """Extract first paragraph text as plain string for OG description."""
    match = re.search(r'<p>(.*?)</p>', html_body, re.DOTALL)
    if match:
        text = re.sub(r'<[^>]+>', '', match.group(1))
        text = ' '.join(text.split())
        return text
    return ""


def _build_og_tags(title: str, description: str, og_image: Optional[str] = None) -> str:
    """Build Open Graph meta tags."""
    esc = description.replace('"', '&quot;')
    t_esc = title.replace('"', '&quot;')
    lines = [
        f'<meta name="description" content="{esc}">',
        '<meta property="og:type" content="article">',
        f'<meta property="og:title" content="{t_esc}">',
        f'<meta property="og:description" content="{esc}">',
    ]
    if og_image:
        lines.append(f'<meta property="og:image" content="{og_image}">')
    return "\n".join(lines)


def _unwrap_mermaid(html: str) -> str:
    """Convert any highlighted mermaid blocks to raw <pre class='mermaid'>."""
    # match <div class="codehilite">...</div> when inner code references mermaid
    pattern = re.compile(
        r'<div\s+class="codehilite"\s*>(?P<inner>.*?)</div>',
        re.DOTALL,
    )

    def mermaid_div_repl(m: re.Match) -> str:
        inner = m.group('inner')
        if 'language-mermaid' not in inner and 'class="mermaid"' not in inner:
            return m.group(0)
        raw = re.sub(r'<[^>]+>', '', inner)
        raw = raw.strip()
        if not raw:
            return m.group(0)
        return f'<pre class="mermaid">{raw}</pre>'

    html = pattern.sub(mermaid_div_repl, html)

    # Also handle <pre><code class="language-mermaid"> outside div.codehilite
    pre_code_pattern = re.compile(
        r'<pre>\s*<code(?:\s+class="[^"]*\blanguage-mermaid\b[^"]*")?\s*>'
        r'(.*?)'
        r'</code>\s*</pre>',
        re.DOTALL,
    )

    def pre_code_repl(m: re.Match) -> str:
        raw = m.group(1).strip()
        return f'<pre class="mermaid">{raw}</pre>'

    html = pre_code_pattern.sub(pre_code_repl, html)
    return html


def _inject_mermaid(html: str) -> str:
    """Inject Mermaid.js CDN and initialize script before </body>."""
    scripts = (
        '\n<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>\n'
        '<script>mermaid.initialize({startOnLoad:true, theme: "default"});</script>\n'
    )
    if "</body>" in html:
        html = html.replace("</body>", f"{scripts}</body>")
    else:
        html = html + scripts + "\n"
    return html


def _clean_slug(title: str) -> str:
    """Generate URL-safe slug from title."""
    cleaned = re.sub(
        r'^(Cron Job:|Research Report:|Daily:|Weekly:)\s*',
        '', title, flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s*[-:]\s*',
        '', cleaned,
    )
    slug = re.sub(r'[^a-zA-Z0-9\s-]', ' ', cleaned.strip())
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-').lower()[:60]
    return slug if slug else "untitled"


DEFAULT_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_title}</title>
{og_tags}
{author_meta}
{favicon_tag}
<style>
{css}
</style>
</head>
<body>
<a href="#main-content" class="skip-link">Skip to content</a>
<a href="../" class="back">&larr; Back</a>

<header>
  {site_title_tag}
  <h1>{page_title}</h1>
  <p class="meta">{entry_type} &middot; {date} &middot; {reading_time} min read &middot; <code>{fingerprint}</code></p>
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
    og_image: Optional[str] = None,
    mermaid: bool = True,
    favicon: Optional[Path] = None,
    author: Optional[str] = None,
    site_title: Optional[str] = None,
    show_toc: bool = True,
    skill_template: Optional[str] = None,
    skill_assets: Optional[List[Path]] = None,
    humanize: bool = False,
    tldr: bool = False,
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
        og_image: Optional URL for Open Graph image
        mermaid: Whether to enable Mermaid diagram support (default True)
        favicon: Optional path to favicon image (copied to output and linked)
        author: Optional author name for site metadata
        site_title: Optional site title to show above page title
        show_toc: Whether to insert TOC when 2+ headings exist (default True)
        skill_template: Optional skill template string (takes precedence over template_override)
        skill_assets: Optional list of asset paths from the skill to copy into output
        humanize: Whether to rewrite markdown through LLM before conversion (default False)
        tldr: Whether to inject auto-generated TL;DR summary at the top (default False)

    Returns:
        ConversionResult with HTML content and metadata
    """
    from pygments.formatters.html import HtmlFormatter

    from agent_publish.humanize import humanize_markdown
    from agent_publish.themes import DEFAULT_CSS

    md_content = input_path.read_text(encoding='utf-8')

    # Optional humanization pass
    if humanize:
        md_content = humanize_markdown(md_content)

    # Extract title and fingerprint
    title = _extract_title(md_content)
    fingerprint = _generate_fingerprint(md_content)

    # Pre-extract mermaid blocks so they bypass syntax highlighting
    mermaid_blocks: List[str] = []
    if mermaid:
        def _mermaid_repl(match: re.Match) -> str:
            idx = len(mermaid_blocks)
            mermaid_blocks.append(match.group(1).rstrip('\n'))
            return f'\n<!-- MERMAID_BLOCK_{idx} -->\n'
        md_content = _FENCE_RE.sub(_mermaid_repl, md_content)

    # Parse markdown with syntax highlighting
    md = markdown.Markdown(extensions=[
        fenced_code.FencedCodeExtension(),
        CodeHiliteExtension(linenums=False, guess_lang=False),
        tables.TableExtension(),
        toc.TocExtension(),
    ])

    html_body = md.convert(md_content)
    toc_html = md.toc if hasattr(md, 'toc') else ""  # type: ignore[attr-defined]

    # Re-insert mermaid blocks as raw <pre class="mermaid">
    if mermaid and mermaid_blocks:
        for idx, block in enumerate(mermaid_blocks):
            placeholder = f'<!-- MERMAID_BLOCK_{idx} -->'
            html_body = html_body.replace(
                placeholder,
                f'<pre class="mermaid">{block}</pre>',
            )

    # Fallback: strip any remaining highlighted mermaid wrappers in HTML
    if mermaid:
        html_body = _unwrap_mermaid(html_body)

    # If TOC has at least 2 entries (meaningful nav) and show_toc is True, wrap and prepend
    if show_toc and toc_html and toc_html.count('<a href="#') >= 2:
        toc_nav = f'<nav class="toc">{toc_html}</nav>\n'
        html_body = toc_nav + html_body

    # Auto TL;DR injection
    if tldr:
        from agent_publish.tldr import generate_tldr
        tldr_text = generate_tldr(md_content)
        tldr_html = f'<div class="tldr-callout"><strong>TL;DR</strong> \u2014 {tldr_text}</div>\n'
        html_body = tldr_html + html_body

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
    if skill_template:
        template = skill_template
    elif template_override and template_override.exists():
        template = template_override.read_text(encoding='utf-8')
    else:
        template = DEFAULT_TEMPLATE

    # Compute reading time and description
    reading_time = _calculate_reading_time(md_content)
    description = _extract_description(html_body)
    og_tags = _build_og_tags(title, description, og_image)

    # Build favicon tag
    favicon_tag = ""
    if favicon and favicon.exists():
        favicon_tag = f'<link rel="icon" type="image/x-icon" href="{favicon.name}">'

    # Build site metadata
    html_title = f"{site_title} -- {title}" if site_title else title
    author_meta = f'<meta name="author" content="{author}">\n' if author else ""
    site_title_tag = f'<p class="site-title">{site_title}</p>\n' if site_title else ""

    html = _safe_format(
        template,
        html_title=html_title,
        author_meta=author_meta,
        title=title,
        page_title=title,
        css=css,
        fingerprint=fingerprint,
        date=date,
        body=html_body,
        entry_type=entry_type.capitalize(),
        reading_time=reading_time,
        og_tags=og_tags,
        favicon_tag=favicon_tag,
        site_title_tag=site_title_tag,
    )

    # Inject Mermaid.js if mermaid blocks are present and mermaid is enabled
    if mermaid and '<pre class="mermaid">' in html_body:
        html = _inject_mermaid(html)

    from agent_publish.assets import copy_assets

    html, assets_copied = copy_assets(html, base_dir=input_path.parent, output_dir=output_dir)

    # Copy favicon to output if provided
    if favicon and favicon.exists():
        import shutil
        dest_favicon = output_dir / favicon.name
        if favicon.resolve() != dest_favicon.resolve():
            shutil.copy2(favicon, dest_favicon)
            assets_copied.insert(0, dest_favicon)
        else:
            # Already in output dir -- ensure it's tracked
            if dest_favicon not in assets_copied:
                assets_copied.insert(0, dest_favicon)

    # Copy skill assets to output if provided
    if skill_assets:
        import shutil
        for asset in skill_assets:
            if asset.exists():
                dest_asset = output_dir / asset.name
                if asset.resolve() != dest_asset.resolve():
                    shutil.copy2(asset, dest_asset)
                    if dest_asset not in assets_copied:
                        assets_copied.append(dest_asset)

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
        reading_time=reading_time,
        description=description,
    )
