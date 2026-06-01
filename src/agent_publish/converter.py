"""Markdown to HTML conversion with agent-friendly defaults."""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import markdown
from markdown.extensions import fenced_code, tables, toc


@dataclass
class ConversionResult:
    html: str
    title: str
    fingerprint: str
    output_path: Path


DEFAULT_CSS = """:root{
  --bg:#faf8f5;--fg:#1c1917;--muted:#78716c;--accent:#0077b6;
  --accent-2:#48cae4;--border:#e7e5e4;--surface:#fff;--code-bg:#f5f5f0
}
*{box-sizing:border-box}
html{font-size:16px}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  line-height:1.7;color:var(--fg);background:var(--bg);margin:0;padding:0;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent;transition:border-color .15s}
a:hover{border-bottom-color:var(--accent)}
.back{display:inline-block;margin:2rem auto 0;font-size:.8125rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
header,.main{max-width:720px;margin:0 auto;padding:1.75rem}
header{padding-bottom:.5rem}
.main{padding-top:0}
h1{font-size:1.625rem;font-weight:700;line-height:1.2;letter-spacing:-0.025em;margin:0;color:var(--fg)}
h2{font-size:1.125rem;font-weight:600;margin:2.5rem 0 1rem;padding-top:.5rem;border-top:2px solid var(--accent);color:var(--fg)}
h3{font-size:1rem;font-weight:600;margin:1.5rem 0 .5rem;color:var(--fg)}
p{margin:0 0 1.125rem}
.meta{font-size:.8125rem;color:var(--muted);margin-top:.5rem;letter-spacing:.01em}
table{width:100%;border-collapse:collapse;font-size:.875rem;margin:1.25rem 0;background:var(--surface);border-radius:6px;overflow:hidden}
th,td{text-align:left;padding:.6rem .9rem;border-bottom:1px solid var(--border)}
thead th{font-weight:600;color:var(--fg);background:#f5f5f0;border-bottom:2px solid var(--border)}
ul{margin:0 0 1.125rem;padding-left:1.5rem}
li{margin-bottom:.4rem}
blockquote{border-left:3px solid var(--accent-2);margin:1.75rem 0;padding:.5rem 0 .5rem 1.25rem;color:var(--muted);font-style:italic;background:none}
code{background:var(--code-bg);padding:.18em .45em;border-radius:4px;font-size:.85em;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;color:var(--fg)}
pre{background:var(--code-bg);padding:1rem 1.25rem;border-radius:8px;overflow-x:auto;font-size:.82rem;margin:1.25rem 0;line-height:1.6;border:1px solid var(--border)}
pre code{background:none;padding:0;font-size:inherit}
@media print{body{background:#fff}a[href]:after{content:" (" attr(href) ")";font-size:.75rem;color:var(--muted)}.back{display:none}}
""".strip()


def _generate_fingerprint(content: str) -> str:
    """Generate content fingerprint for cache-busting."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _extract_title(md_content: str) -> str:
    """Extract title from first h1 or use default."""
    match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"


def _clean_slug(title: str) -> str:
    """Generate URL-safe slug from title."""
    # Strip common prefixes
    cleaned = re.sub(r'^(Cron Job:|Research Report:|Daily:|Weekly:)\s*', '', title, flags=re.IGNORECASE)
    cleaned = re.sub(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s*[-:]\s*', '', cleaned)
    # Clean special chars
    slug = re.sub(r'[^a-zA-Z0-9\s-]', ' ', cleaned.strip())
    slug = re.sub(r'\s+', '-', slug)
    return re.sub(r'-+', '-', slug).lower()[:60]


def convert_file(
    input_path: Path,
    output_dir: Path,
    entry_type: str = "daily",
    custom_css: Optional[str] = None,
    date_str: Optional[str] = None,
) -> ConversionResult:
    """Convert markdown file to HTML.
    
    Args:
        input_path: Path to input markdown file
        output_dir: Directory for output HTML
        entry_type: Category for metadata (daily, weekly, etc.)
        custom_css: Optional custom CSS to override default
        date_str: Optional date string (defaults to today)
    
    Returns:
        ConversionResult with HTML content and metadata
    """
    md_content = input_path.read_text(encoding='utf-8')
    
    # Extract title and fingerprint
    title = _extract_title(md_content)
    fingerprint = _generate_fingerprint(md_content)
    
    # Parse markdown
    md = markdown.Markdown(extensions=[
        fenced_code.FencedCodeExtension(),
        tables.TableExtension(),
        toc.TocExtension(),
    ])
    
    html_body = md.convert(md_content)
    
    # Build output
    css = custom_css or DEFAULT_CSS
    date = date_str or __import__('datetime').datetime.now().strftime("%Y-%m-%d")
    slug = _clean_slug(title)
    
    html = f'''<!DOCTYPE html>
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
<a href="../" class="back">&larr; Back</a>

<header>
  <h1>{title}</h1>
  <p class="meta">{entry_type.capitalize()} &middot; {date} &middot; <code>{fingerprint}</code></p>
</header>

<main class="main">
{html_body}
</main>
</body>
</html>'''
    
    output_name = f"{date}-{slug}.html"
    output_path = output_dir / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    
    return ConversionResult(
        html=html,
        title=title,
        fingerprint=fingerprint,
        output_path=output_path,
    )
