"""Themes loader for agent-publish."""

from pathlib import Path
from typing import Optional

DEFAULT_CSS = """:root{
  --bg:#faf8f5;--fg:#1c1917;--muted:#78716c;--accent:#0077b6;
  --accent-2:#48cae4;--border:#e7e5e4;--surface:#fff;--code-bg:#f5f5f0
}
*{box-sizing:border-box}
html{font-size:16px;scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  line-height:1.7;color:var(--fg);background:var(--bg);margin:0;padding:0;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent;transition:border-color .15s,color .15s}
a:hover{border-bottom-color:var(--accent)}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-bottom-color:transparent}
.skip-link{position:absolute;top:-40px;left:0;background:var(--accent);color:#fff;padding:.5rem 1rem;z-index:100;text-decoration:none;border-bottom:0;font-size:.875rem;font-weight:500}
.skip-link:focus{top:0}
.back{display:inline-block;margin:2rem auto 0;font-size:.8125rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;transition:color .15s}
.back:hover{color:var(--fg)}
.back:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
header,.main{max-width:720px;margin:0 auto;padding:1.75rem}
header{padding-bottom:.5rem}
.main{padding-top:0}
h1{font-family:Georgia,'Times New Roman',serif;font-size:2rem;font-weight:700;line-height:1.2;letter-spacing:-0.025em;margin:0 0 .25rem;color:var(--fg)}
h2{font-size:1.3rem;font-weight:600;margin:2.5rem 0 1rem;padding-left:.65rem;border-left:3px solid var(--accent);color:var(--fg);position:relative}
h3{font-size:1rem;font-weight:600;margin:1.5rem 0 .5rem;color:var(--muted);position:relative}
h2 a.anchor,h3 a.anchor{opacity:0;position:absolute;left:-1.2em;top:.15em;font-size:.85em;text-decoration:none;border-bottom:0;transition:opacity .15s}
h2:hover a.anchor,h3:hover a.anchor{opacity:1}
p{margin:0 0 1.125rem}
.meta{font-size:.8125rem;color:var(--muted);margin-top:.5rem;letter-spacing:.06em;text-transform:uppercase;font-size:.75rem}
table{width:100%;border-collapse:collapse;font-size:.875rem;margin:1.25rem 0;background:var(--surface)}
tr{transition:background .12s}
tr:hover{background:rgba(0,119,182,.06)}
th,td{text-align:left;padding:.6rem .9rem;border-bottom:1px solid var(--border)}
thead th{font-weight:600;color:var(--fg);background:#f5f5f0;border-bottom:2px solid var(--border)}
ul{margin:0 0 1.125rem;padding-left:1.5rem}
li{margin-bottom:.4rem}
blockquote{border-left:3px solid var(--accent-2);margin:1.75rem 0;padding:.5rem 0 .5rem 1.25rem;color:var(--muted);font-style:italic;background:none}
code{background:var(--code-bg);padding:.18em .45em;border-radius:4px;font-size:.85em;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;color:var(--fg)}
pre{background:var(--code-bg);padding:1rem 1.25rem;border-radius:8px;overflow-x:auto;font-size:.82rem;margin:1.25rem 0;line-height:1.6;border:1px solid var(--border);transition:border-color .15s,box-shadow .15s}
pre:hover{border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,119,182,.08)}
pre:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,119,182,.08)}
pre code{background:none;padding:0;font-size:inherit}
.toc{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem 1.25rem;margin:0 0 1.75rem;font-size:.8125rem}
.toc ul{list-style:none;padding-left:0;margin:0}
.toc ul ul{padding-left:1.1rem;margin-top:.2rem}
.toc li{margin:0 0 .15rem}
.toc a{color:var(--accent);text-decoration:none;border-bottom:0}
.toc a:hover{text-decoration:underline}
.toc a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.toc details.toc-sub{margin:.1rem 0}
.toc details.toc-sub>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:.25rem;padding:.1rem 0;font-size:.75rem;color:var(--muted);user-select:none}
.toc details.toc-sub>summary::-webkit-details-marker{display:none}
.toc details.toc-sub>summary::marker{display:none;content:""}
.toc-toggle{display:inline-block;width:.85em;height:.85em;position:relative;flex-shrink:0}
.toc-toggle::before,.toc-toggle::after{content:"";position:absolute;background:var(--muted);transition:transform .15s}
.toc-toggle::before{top:50%;left:0;right:0;height:1.5px;transform:translateY(-50%)}
.toc-toggle::after{top:0;bottom:0;left:50%;width:1.5px;transform:translateX(-50%)}
.toc details.toc-sub[open]>summary .toc-toggle::after{transform:translateX(-50%) rotate(90deg)}
.toc a.toc-active{color:var(--fg);font-weight:600;background:rgba(0,119,182,.08);border-radius:3px;padding:0 .3rem;margin:0 -.3rem}
.tldr-callout{background:var(--surface);border-left:3px solid var(--accent);padding:.85rem 1.1rem;margin:0 0 1.75rem;font-size:.9rem;color:var(--fg);border-radius:0 6px 6px 0;line-height:1.5}
.tag-bar{display:flex;flex-wrap:wrap;gap:.35rem;margin-bottom:1.5rem}
.tag{display:inline-block;padding:.18rem .5rem;border-radius:99px;font-size:.75rem;background:var(--surface);color:var(--fg-muted);border:1px solid var(--border);line-height:1.4}
.tag:before{content:"";display:inline-block;width:.25rem;height:.25rem;border-radius:99px;background:var(--accent);margin-right:.25rem;vertical-align:middle;opacity:.7}
.footnotes-sep{border:0;border-top:1px solid var(--border);margin-top:2.5rem}
.footnotes{font-size:.8125rem;color:var(--muted);margin-top:.75rem}
.footnotes-list{padding-left:1.5rem;margin:0}
.footnotes-list li{margin-bottom:.4rem}
.footnotes-list p{display:inline;margin:0}
.footnote-ref{font-size:.8em;position:relative;top:-.35em;scroll-margin-top:2rem}
.footnote-ref a{color:var(--accent);border-bottom:0;text-decoration:none}
.footnote-ref a:hover{text-decoration:underline}
.footnote-backref{font-size:.85em;text-decoration:none;color:var(--muted);border-bottom:0;margin-left:.3em}
.footnote-backref:hover{color:var(--accent)}
@media (max-width:640px){html{font-size:15px}header,.main{padding:1rem}h1{font-size:1.35rem}h2{font-size:1.05rem}table{font-size:.8rem;display:block;overflow-x:auto}pre{padding:.75rem}.toc{padding:.75rem}}
@media (max-width:1024px){header,.main{padding:1.25rem}}
@media print{body{background:#fff}a[href]:after{content:" (" attr(href) ")";font-size:.75rem;color:var(--muted)}.back{display:none}.toc{display:none}.skip-link{display:none}}
@media (prefers-color-scheme:dark){
  :root{--bg:#1a1816;--fg:#e8e4df;--muted:#9e9891;--accent:#4fb3d9;--accent-2:#7bcfe8;--border:#2e2a26;--surface:#242220;--code-bg:#1f1d1a}
  body{background:var(--bg);color:var(--fg)}
  a{color:var(--accent)}
  h2{border-left-color:var(--accent)}
  table{background:var(--surface)}
  thead th{background:#2d2b28}
  tr:hover{background:rgba(79,179,217,.08)}
  pre:hover{border-color:var(--accent);box-shadow:0 0 0 3px rgba(79,179,217,.10)}
  blockquote{border-left-color:var(--accent-2);color:var(--muted)}
}
""".strip()


MINIMAL_CSS = """:root{
  --bg:#fff;--fg:#111;--muted:#666;--accent:#111
}
*{box-sizing:border-box}
html{font-size:15px;scroll-behavior:smooth}
body{font-family:system-ui,-apple-system,sans-serif;
  line-height:1.6;color:var(--fg);background:var(--bg);margin:0;padding:2rem;max-width:680px}
a{color:var(--accent);text-decoration:underline;text-underline-offset:2px;transition:text-underline-offset .15s}
a:hover{text-underline-offset:4px}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;text-underline-offset:4px}
.skip-link{position:absolute;top:-40px;left:0;background:var(--fg);color:var(--bg);padding:.5rem 1rem;z-index:100;text-decoration:none;font-size:.875rem;font-weight:500}
.skip-link:focus{top:0}
h1{font-size:1.5rem;font-weight:500;margin:0 0 1rem}
h2{font-size:1.1rem;font-weight:500;margin:2rem 0 .5rem;padding-top:1rem;border-top:1px solid #ddd;position:relative}
h2 a.anchor{opacity:0;position:absolute;left:-1.2em;top:.25em;font-size:.85em;text-decoration:none;transition:opacity .15s}
h2:hover a.anchor{opacity:1}
code{background:#f5f5f5;padding:.1em .3em;font-size:.9em;font-family:monospace}
pre{background:#f5f5f5;padding:1rem;overflow-x:auto;border:1px solid transparent;transition:border-color .15s}
pre:hover{border-color:#ccc}
pre:focus-within{border-color:#ccc}
table{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.9em}
tr{transition:background .12s}
tr:hover{background:rgba(0,0,0,.04)}
th,td{text-align:left;padding:.4rem .8rem;border-bottom:1px solid #ddd}
th{font-weight:500;border-bottom:2px solid #111}
.footnotes-sep{border:0;border-top:1px solid #ddd;margin-top:2.5rem}
.footnotes{font-size:.8125rem;color:var(--muted);margin-top:.75rem}
.footnotes-list{padding-left:1.5rem;margin:0}
.footnotes-list li{margin-bottom:.4rem}
.footnotes-list p{display:inline;margin:0}
.footnote-ref{font-size:.8em;position:relative;top:-.35em;scroll-margin-top:2rem}
.footnote-ref a{color:var(--accent);text-decoration:none}
.footnote-ref a:hover{text-decoration:underline}
.footnote-backref{font-size:.85em;text-decoration:none;color:var(--muted);margin-left:.3em}
.footnote-backref:hover{color:var(--fg)}
@media (max-width:640px){body{padding:1rem;font-size:.95rem}h1{font-size:1.3rem}h2{font-size:1rem}table{display:block;overflow-x:auto}pre{padding:.75rem}}
@media (max-width:1024px){body{padding:1.5rem}}
@media print{body{background:#fff}h2{border-top-color:#bbb}a[href]:after{content:" (" attr(href) ")";font-size:.75rem;color:var(--muted)}.skip-link{display:none}}
@media (prefers-color-scheme:dark){
  :root{--bg:#000;--fg:#eee;--muted:#999;--accent:#ccc}
  body{background:var(--bg);color:var(--fg)}
  h2{border-top-color:#444}
  code,pre{background:#1a1a1a}
  th{border-bottom-color:#666}
  td{border-bottom-color:#333}
  tr:hover{background:rgba(255,255,255,.06)}
  pre:hover{border-color:#444}
  pre:focus-within{border-color:#444}
}
""".strip()


BRUTALIST_CSS = """:root{
  --bg:#000;--fg:#0f0;--accent:#0f0;--dim:#0a0
}
*{box-sizing:border-box;}
html{font-family:"Courier New",monospace;background:var(--bg);color:var(--fg);scroll-behavior:smooth}
body{max-width:720px;margin:0 auto;padding:2rem}
a{color:var(--accent);text-decoration:none;transition:background .1s,color .1s}
a:hover{background:var(--accent);color:var(--bg)}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.skip-link{position:absolute;top:-40px;left:0;background:var(--accent);color:var(--bg);padding:.5rem 1rem;z-index:100;text-decoration:none;font-size:.875rem;font-weight:700}
.skip-link:focus{top:0}
.back:hover{color:var(--fg);background:none}
.back:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
h1,h2{border:2px solid var(--accent);padding:.5rem;display:inline-block;position:relative}
h2{margin-top:2rem}
h3{font-size:.95rem;font-weight:700;margin:1.5rem 0 .5rem;color:var(--fg);position:relative}
h2 a.anchor,h3 a.anchor{opacity:0;position:absolute;left:-1.4em;top:.3em;font-size:.85em;text-decoration:none;border-bottom:0;transition:opacity .15s}
h2:hover a.anchor,h3:hover a.anchor{opacity:1}
p{margin:0 0 1.125rem}
.back{display:inline-block;margin:2rem 0 0;font-size:.8125rem;color:var(--dim);text-transform:uppercase;letter-spacing:.05em}
.meta{font-size:.8125rem;color:var(--dim);margin-top:.5rem}
code,pre{background:var(--dim);padding:.1em .3em}
pre{padding:1rem;overflow-x:auto;border:1px solid transparent;transition:border-color .15s}
pre:hover{border-color:var(--accent)}
pre:focus-within{border-color:var(--accent)}
pre code{background:none;padding:0;font-size:inherit}
table{width:100%;border:2px solid var(--accent);border-collapse:collapse;margin:1.25rem 0}
tr{transition:background .12s}
tr:hover{background:rgba(0,255,0,.08)}
th,td{border:1px solid var(--accent);padding:.5rem;text-align:left}
th{background:var(--dim)}
ul{margin:1rem 0;padding-left:1.5rem}
li{margin:.3rem 0}
blockquote{border-left:2px solid var(--accent);margin:1.5rem 0;padding:.5rem 0 .5rem 1rem;color:var(--dim);font-style:italic}
.toc{background:var(--dim);border:2px solid var(--accent);padding:1rem 1.25rem;margin:0 0 1.5rem;font-size:.8125rem}
.toc ul{list-style:none;padding-left:0;margin:0}
.toc ul ul{padding-left:1.1rem;margin-top:.2rem}
.toc li{margin:0 0 .15rem}
.toc a{color:var(--accent);text-decoration:none}
.toc a:hover{text-decoration:underline}
.toc a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.footnotes-sep{border:0;border-top:1px solid var(--accent);margin-top:2.5rem}
.footnotes{font-size:.8125rem;color:var(--dim);margin-top:.75rem}
.footnotes-list{padding-left:1.5rem;margin:0}
.footnotes-list li{margin-bottom:.4rem}
.footnotes-list p{display:inline;margin:0}
.footnote-ref{font-size:.8em;position:relative;top:-.35em;scroll-margin-top:2rem}
.footnote-ref a{color:var(--accent);text-decoration:none}
.footnote-ref a:hover{background:var(--accent);color:var(--bg)}
.footnote-backref{font-size:.85em;text-decoration:none;color:var(--dim);margin-left:.3em}
.footnote-backref:hover{color:var(--fg)}
.toc details.toc-sub{margin:.1rem 0}
.toc details.toc-sub>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:.25rem;padding:.1rem 0;font-size:.75rem;color:var(--dim);user-select:none}
.toc details.toc-sub>summary::-webkit-details-marker{display:none}
.toc details.toc-sub>summary::marker{display:none;content:""}
.toc-toggle{display:inline-block;width:.85em;height:.85em;position:relative;flex-shrink:0}
.toc-toggle::before,.toc-toggle::after{content:"";position:absolute;background:var(--accent);transition:transform .15s}
.toc-toggle::before{top:50%;left:0;right:0;height:1.5px;transform:translateY(-50%)}
.toc-toggle::after{top:0;bottom:0;left:50%;width:1.5px;transform:translateX(-50%)}
.toc details.toc-sub[open]>summary .toc-toggle::after{transform:translateX(-50%) rotate(90deg)}
.toc a.toc-active{color:var(--fg);font-weight:700}
@media (max-width:640px){body{padding:1rem;font-size:.875rem}h1,h2{padding:.35rem;font-size:1.1rem}h3{font-size:.85rem}pre{padding:.75rem}table{font-size:.8rem}.toc{padding:.75rem}}
@media (max-width:1024px){body{padding:1.25rem}}
@media print{body{background:#fff;color:#000}a{color:#000;text-decoration:underline}h1,h2{border-color:#000}code,pre{background:#f5f5f5;color:#000}th,td{border-color:#000}.skip-link{display:none}.back{display:none}.toc{display:none}}
@media (prefers-color-scheme:dark){
  :root{--bg:#0a0;--fg:#000;--accent:#000;--dim:#050}
  html{background:var(--bg);color:var(--fg)}
  body{background:var(--bg);color:var(--fg)}
  a{color:var(--accent)}
  a:hover{background:var(--accent);color:var(--bg)}
  h1,h2{border-color:var(--accent)}
  code,pre{background:var(--dim);color:var(--fg)}
  pre:hover{border-color:var(--accent)}
  pre:focus-within{border-color:var(--accent)}
  table{border-color:var(--accent)}
  th,td{border-color:var(--accent)}
  th{background:var(--dim)}
  tr:hover{background:rgba(0,0,0,.10)}
  blockquote{border-left-color:var(--accent);color:var(--fg)}
  .toc{background:var(--dim);border-color:var(--accent)}
  .toc a{color:var(--accent)}
}
""".strip()


EDITORIAL_CSS = """:root{--bg:#FAFAF8;--fg:#1A1916;--muted:#6B6560;--accent:#8B4513;--accent-2:#A0522D;--border:#E0DCD6;--surface:#F5F3EF;--code-bg:#EFEBE5}*{box-sizing:border-box}html{font-size:16px;scroll-behavior:smooth}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;line-height:1.7;color:var(--fg);background:var(--bg);margin:0;padding:0;-webkit-font-smoothing:antialiased}a{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent;transition:border-color .15s,color .15s}a:hover{border-bottom-color:var(--accent)}a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-bottom-color:transparent}.skip-link{position:absolute;top:-40px;left:0;background:var(--accent);color:#fff;padding:.5rem 1rem;z-index:100;text-decoration:none;border-bottom:0;font-size:.875rem;font-weight:500}.skip-link:focus{top:0}.back{display:inline-block;margin:2rem auto 0;font-size:.8125rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;transition:color .15s}.back:hover{color:var(--fg)}.back:focus-visible{outline:2px solid var(--accent);outline-offset:2px}header,.main{max-width:720px;margin:0 auto;padding:1.75rem}header{padding-bottom:.5rem}.main{padding-top:0}h1{font-family:Georgia,"Playfair Display","Times New Roman",serif;font-size:36px;font-weight:700;line-height:1.15;letter-spacing:-0.03em;margin:0;color:var(--fg)}h2{font-size:20px;font-weight:600;margin:2.5rem 0 1rem;padding-left:1rem;border-left:3px solid var(--accent);color:var(--fg);position:relative}h3{font-size:16px;font-weight:600;margin:1.5rem 0 .5rem;color:var(--muted);position:relative}h2 a.anchor,h3 a.anchor{opacity:0;position:absolute;left:-1.2em;top:.15em;font-size:.85em;text-decoration:none;border-bottom:0;transition:opacity .15s}h2:hover a.anchor,h3:hover a.anchor{opacity:1}p{margin:0 0 1.125rem}.meta{font-size:13px;color:var(--muted);margin-top:.5rem;letter-spacing:0.05em;text-transform:uppercase;font-weight:400}table{width:100%;font-size:.875rem;margin:1.25rem 0;background:var(--surface);border-collapse:separate;border-spacing:0}tr{transition:background .12s}tr:hover{background:rgba(139,69,19,.06)}th,td{text-align:left;padding:.6rem .9rem;border-bottom:1px solid var(--border)}thead th{font-weight:600;color:var(--fg);background:var(--surface);border-bottom:2px solid var(--border)}ul{margin:0 0 1.125rem;padding-left:1.5rem}li{margin-bottom:.4rem}blockquote{border-left:3px solid var(--accent-2);margin:1.75rem 0;padding:.5rem 0 .5rem 1.25rem;color:var(--muted);font-style:italic;background:none}code{background:var(--code-bg);padding:.18em .45em;border-radius:4px;font-size:.85em;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;color:var(--fg)}pre{background:var(--code-bg);padding:1rem 1.25rem;border-radius:8px;overflow-x:auto;font-size:.82rem;margin:1.25rem 0;line-height:1.6;border:1px solid var(--border);transition:border-color .15s,box-shadow .15s}pre:hover{border-color:var(--accent);box-shadow:0 0 0 3px rgba(139,69,19,.08)}pre:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px rgba(139,69,19,.08)}pre code{background:none;padding:0;font-size:inherit}.toc{border-left:2px solid var(--accent);padding-left:1rem;margin:0 0 1.75rem;font-size:.8125rem;background:none;border-radius:0}.toc ul{list-style:none;padding-left:0;margin:0}.toc ul ul{padding-left:1.1rem;margin-top:.2rem}.toc li{margin:0 0 .15rem}.toc a{color:var(--accent);text-decoration:none;border-bottom:0}.toc a:hover{text-decoration:underline}.toc a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}.tldr-callout{background:var(--surface);border-left:3px solid var(--accent);padding:.85rem 1.1rem;margin:0 0 1.75rem;font-size:.9rem;color:var(--fg);border-radius:0 6px 6px 0;line-height:1.5}.tag-bar{display:flex;flex-wrap:wrap;gap:.35rem;margin-bottom:1.5rem}.tag{display:inline-block;padding:.18rem .5rem;border-radius:99px;font-size:.75rem;background:var(--surface);color:var(--fg-muted);border:1px solid var(--border);line-height:1.4}.tag:before{content:"";display:inline-block;width:.25rem;height:.25rem;border-radius:99px;background:var(--accent);margin-right:.25rem;vertical-align:middle;opacity:.7}@media (max-width:640px){html{font-size:15px}header,.main{padding:1rem}h1{font-size:1.35rem}h2{font-size:1.05rem}table{font-size:.8rem;display:block;overflow-x:auto}pre{padding:.75rem}.toc{padding-left:.75rem}}@media (max-width:1024px){header,.main{padding:1.25rem}}@media print{body{background:#fff}a[href]:after{content:" (" attr(href) ")";font-size:.75rem;color:var(--muted)}.back{display:none}.toc{display:none}.skip-link{display:none}}@media (prefers-color-scheme:dark){:root{--bg:#1C1A18;--fg:#E8E4DF;--muted:#9E9891;--accent:#C8956C;--accent-2:#C8956C;--border:#3A3632;--surface:#2A2624;--code-bg:#232120}body{background:var(--bg);color:var(--fg)}a{color:var(--accent)}h2{border-left-color:var(--accent)}blockquote{border-left-color:var(--accent-2);color:var(--muted)}table{background:var(--surface)}thead th{background:var(--surface)}tr:hover{background:rgba(200,149,108,.08)}pre:hover{border-color:var(--accent);box-shadow:0 0 0 3px rgba(200,149,108,.10)}pre:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px rgba(200,149,108,.10)}.tag{background:var(--surface)}}""".strip()


THEMES = {
    "default": DEFAULT_CSS,
    "minimal": MINIMAL_CSS,
    "brutalist": BRUTALIST_CSS,
    "editorial": EDITORIAL_CSS,
}


def _package_themes_dir() -> Path:
    """Return the directory containing builtin DESIGN.md theme folders."""
    return Path(__file__).parent / "design_themes"


def load(theme: str, custom_path: Optional[Path] = None, design_path: Optional[Path] = None, direction: Optional[str] = None) -> str:
    """Load CSS theme.

    Args:
        theme: Theme name (default, minimal, brutalist) or 'custom' with
            custom_path.
        custom_path: Path to custom CSS file.
        design_path: Path to a DESIGN.md file to generate CSS from.
        direction: OKLch palette direction (e.g. 'editorial').
            When set, overrides theme/custom_path/design_path.

    Returns:
        CSS string.
    """
    if direction:
        from . import oklch
        return oklch.generate_css(direction)
    if design_path:
        from . import designmd
        parsed = designmd.load_design(design_path)
        return designmd.generate_css(parsed)
    if custom_path:
        return custom_path.read_text(encoding='utf-8')

    # For built-in themes, prefer DESIGN.md + base.css over hardcoded strings
    if theme in THEMES:
        design_candidate = _package_themes_dir() / theme / "DESIGN.md"
        if design_candidate.exists():
            from . import designmd
            parsed = designmd.load_design(design_candidate)
            return designmd.generate_css(parsed)

    return THEMES.get(theme, DEFAULT_CSS)


def load_design_theme(design_path: Path) -> str:
    """Load CSS from a DESIGN.md file.

    Args:
        design_path: Path to a DESIGN.md file.

    Returns:
        CSS string generated from the DESIGN.md spec.
    """
    from . import designmd
    parsed = designmd.load_design(design_path)
    return designmd.generate_css(parsed)


def list_themes() -> list:
    """List available themes."""
    return list(THEMES.keys())
