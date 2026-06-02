# agent-publish

Markdown-to-HTML pipeline for AI agents.

Converts research outputs, logs, and agent artifacts into clean, styled HTML and publishes to GitHub Pages.

## Why This Exists

The "3 AM problem": You run overnight research, get markdown output... now what? This tool bridges that gap — turning raw agent outputs into publishable web pages without manual intervention.

## Features

- **CLI-first**: `agent-publish input.md --url https://user.github.io/repo`
- **Zero-config**: Sane defaults, optional `agent-publish.toml` override
- **Cache-aware**: Prevents duplicate publishes via content fingerprinting
- **Auto-TOC**: Generates table of contents from H2/H3 when 2+ subsections exist
- **Asset collection**: Copies local images into `images/` subfolder and rewrites paths
- **Theme system**: Pluggable CSS (default, minimal, brutalist)
- **GitHub Pages native**: Built-in push with proper cache-busting

## Install

```bash
pip install agent-publish
```

Or from source:
```bash
git clone https://github.com/thisisprabha/agent-publish.git
cd agent-publish
pip install -e .
```

## Quick Start

### One-shot publish
```bash
agent-publish research.md --url https://thisisprabha.github.io/warehouse
```

### Dry run (convert without pushing)
```bash
agent-publish draft.md --dry-run --theme minimal
```

### Bulk publish with config
```bash
# agent-publish.toml
[output]
theme = "minimal"
base_url = "https://thisisprabha.github.io/warehouse"

[github]
auto_push = true
commit_prefix = "🤖 publish:"
```
Then: `agent-publish docs/*.md --config agent-publish.toml`

### With custom CSS
```bash
agent-publish report.md --custom-css ./styles/custom.css
```

## CLI Reference

| Flag | Description |
|---|---|
| `input.md` | Markdown file(s) to convert |
| `--type {daily,weekly,note,research}` | Entry category |
| `--url` | Base URL for published content |
| `--repo` | Target repo path |
| `--theme {default,minimal,brutalist}` | Built-in CSS theme |
| `--custom-css` | Path to custom CSS file |
| `--template` | Path to custom Jinja2 template |
| `--config` | Config file path (TOML/YAML) |
| `--dry-run` | Convert without git push |
| `--eval` | Run eval verification after publish |

## Structure

```
src/agent_publish/
├── __init__.py
├── converter.py      # MD → HTML with fenced code, tables, TOC
├── publisher.py      # Git ops + fingerprint cache
├── config.py         # TOML/YAML config loader
├── themes.py         # Built-in CSS themes
├── assets.py         # Image resolution + copy
└── validator.py      # Output verification
```

## Eval

Every release verified against:
- [x] Markdown parity (tables, code blocks, links)
- [x] CSS renders without external deps
- [x] Git push succeeds with non-empty commit
- [x] Image assets copied and paths rewritten
- [x] TOC generated for multi-section docs

Run locally: `pytest tests/`

## License

MIT
