"""Themes loader for agent-publish."""

from pathlib import Path
from typing import Optional

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


MINIMAL_CSS = """:root{
  --bg:#fff;--fg:#111;--muted:#666;--accent:#111
}
*{box-sizing:border-box}
html{font-size:15px}
body{font-family:system-ui,-apple-system,sans-serif;
  line-height:1.6;color:var(--fg);background:var(--bg);margin:0;padding:2rem;max-width:680px}
h1{font-size:1.5rem;font-weight:500;margin:0 0 1rem}
h2{font-size:1.1rem;font-weight:500;margin:2rem 0 .5rem;padding-top:1rem;border-top:1px solid #ddd}
code{background:#f5f5f5;padding:.1em .3em;font-size:.9em;font-family:monospace}
pre{background:#f5f5f5;padding:1rem;overflow-x:auto}
table{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.9em}
th,td{text-align:left;padding:.4rem .8rem;border-bottom:1px solid #ddd}
th{font-weight:500;border-bottom:2px solid #111}
""".strip()


BRUTALIST_CSS = """:root{
  --bg:#000;--fg:#0f0;--accent:#0f0;--dim:#0a0
}
*{box-sizing:border-box;}
html{font-family:"Courier New",monospace;background:var(--bg);color:var(--fg)}
body{max-width:720px;margin:0 auto;padding:2rem}
h1,h2{border:2px solid var(--accent);padding:.5rem;display:inline-block}
h2{margin-top:2rem}
a{color:var(--accent);text-decoration:none}
a:hover{background:var(--accent);color:var(--bg)}
code,pre{background:var(--dim);padding:.1em .3em}
pre{padding:1rem;overflow-x:auto}
table{width:100%;border:2px solid var(--accent);border-collapse:collapse}
th,td{border:1px solid var(--accent);padding:.5rem;text-align:left}
th{background:var(--dim)}
ul{margin:1rem 0;padding-left:1.5rem}
li{margin:.3rem 0}
""".strip()


THEMES = {
    "default": DEFAULT_CSS,
    "minimal": MINIMAL_CSS,
    "brutalist": BRUTALIST_CSS,
}


def load(theme: str, custom_path: Optional[Path] = None) -> str:
    """Load CSS theme.
    
    Args:
        theme: Theme name (default, minimal, brutalist) or 'custom' with custom_path
        custom_path: Path to custom CSS file
        
    Returns:
        CSS string
    """
    if custom_path:
        return custom_path.read_text(encoding='utf-8')
    
    return THEMES.get(theme, DEFAULT_CSS)


def list_themes() -> list:
    """List available themes."""
    return list(THEMES.keys())
