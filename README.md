# agent-publish

Markdown-to-HTML pipeline for AI agents.

Converts research outputs, logs, and agent artifacts into clean, styled HTML and publishes to GitHub Pages.

## Why This Exists

The "3 AM problem": You run overnight research, get markdown output... now what? This tool bridges that gap -- turning raw agent outputs into publishable web pages without manual intervention.

## Features

- **CLI-first**: `agent-publish publish input.md --url https://user.github.io/repo`
- **Zero-config**: Sane defaults, optional `agent-publish.toml` override
- **Cache-aware**: Prevents duplicate publishes via content fingerprinting
- **Auto-TOC**: Generates table of contents from H2/H3; enable with `--toc` (desktop sticky, mobile collapsible)
- **Asset collection**: Copies local images into `images/` subfolder and rewrites paths
- **Theme system**: 3 built-in CSS themes + OKLch-generated palettes via `--direction`
- **Portable themes**: `DESIGN.md` files (structured Markdown theme specs) → CSS at build time
- **Skill extensibility**: `--skill article|briefing|changelog|deck` loads `SKILL.md` + `template.html` + `assets/` folders
- **Anti-slop quality gate**: Built-in `AntiSlopChecker` blocks banned marketing phrases (strict mode via `--strict`)
- **GitHub Pages native**: Built-in push with proper cache-busting
- **RSS/Atom feed**: `feed.xml` generated alongside `index.html`
- **Reading time + Open Graph**: Automatic word-count estimation and social meta tags
- **Mermaid diagrams**: Client-side render for `` ```mermaid `` blocks (auto-injected CDN)
- **Favicon + branding**: `--favicon`, `--author`, `--site-title` wired into every page
- **Watch mode**: Local dev server on `localhost:8080` with auto-rebuild (`agent-publish watch`)
- **Init scaffolding**: `agent-publish init` creates a commented `agent-publish.toml`

## Install

From source (recommended while pre-PyPI):

```bash
git clone https://github.com/thisisprabha/agent-publish.git
cd agent-publish
pip install -e .
```

## Quick Start

### One-shot publish

```bash
agent-publish publish research.md --url https://thisisprabha.github.io/warehouse
```

### Dry run (convert without pushing)

```bash
agent-publish publish draft.md --dry-run --theme minimal
```

### Bulk publish with config

```toml
# agent-publish.toml
[output]
theme = "minimal"
base_url = "https://thisisprabha.github.io/warehouse"
site_title = "My Research"

[github]
auto_push = true
commit_prefix = "🤖 publish:"
```

Then: `agent-publish publish docs/*.md --config agent-publish.toml`

### Init a config interactively

```bash
agent-publish init
```

### Watch mode (local dev server)

```bash
agent-publish watch --port 8080
```

### With a portable theme (DESIGN.md)

```bash
agent-publish publish report.md --theme-design ./my-theme/DESIGN.md
```

### With a skill template

```bash
agent-publish publish changelog.md --skill changelog
```

## CLI Reference

### Global flags

| Flag | Description |
|---|---|
| `--version` | Show program version |
| `--config CONFIG` | Path to TOML/YAML config file |

### `publish` subcommand

| Flag | Description |
|---|---|
| `input.md ...` | Markdown file(s) to convert |
| `--repo REPO` | Target repository path |
| `--type {daily,weekly,note,research}` | Entry category |
| `--url URL` | Base URL for published content |
| `--dry-run` | Convert without git push |
| `--theme {default,minimal,brutalist}` | Built-in CSS theme |
| `--custom-css PATH` | Path to custom CSS file |
| `--theme-design PATH` | Path to a `DESIGN.md` file that generates CSS at build time |
| `--template PATH` | Path to custom Jinja2/HTML template |
| `--eval` | Run eval verification after publish (HTTP check) |
| `--og-image URL` | Open Graph image URL |
| `--site-title TITLE` | Site title for index + feed |
| `--no-index` | Skip `index.html` regeneration |
| `--no-feed` | Skip `feed.xml` generation |
| `--no-mermaid` | Skip Mermaid diagram detection |
| `--favicon PATH` | Favicon image (copied and linked) |
| `--author NAME` | Author name in metadata |
| `--no-toc` | Disable table of contents sidebar |
| `--strict` | Warnings become errors (anti-slop gate) |
| `--direction {editorial,modern-minimal,warm-soft,tech-utility,brutalist}` | OKLch palette generation direction |
| `--skill {article,briefing,changelog,deck}` | Load a skill folder template |

### Other commands

| Command | Description |
|---|---|
| `agent-publish index` | Regenerate `index.html` + `feed.xml` from existing output |
| `agent-publish watch` | Watch markdown files, serve locally, auto-rebuild |
| `agent-publish init` | Scaffold `agent-publish.toml` with commented defaults |

## Themes

### Built-in

- **default** -- Clean academic serif/sans hybrid, good for research notes
- **minimal** -- Ultra-sparse, borderless, single container
- **brutalist** -- Borders, monospace, high-contrast, no-frills

Each has automatic dark mode via `@media (prefers-color-scheme: dark)`.

### OKLch palette directions

Pass `--direction <name>` to generate a full CSS variable palette from OKLch color space:

| Direction | Vibe |
|---|---|
| `editorial` | Warm paper background, strong contrast |
| `modern-minimal` | Cool grays, crisp lines |
| `warm-soft` | Saturated warm primaries |
| `tech-utility` | Highly readable, blue-shifted |
| `brutalist` | Black/white/orange, intentionally raw |

### Portable (DESIGN.md)

Define themes as structured Markdown files. The converter reads `DESIGN.md` and generates CSS at build time so themes are version-controlled as text, not opaque binaries.

Example: `src/agent_publish/design_themes/default/DESIGN.md`

## Architecture

```
src/agent_publish/
├── __init__.py
├── cli.py                # argparse entry points + rich console output
├── config.py             # TOML/YAML config loader + CLI merge
├── converter.py          # MD -> HTML (tables, fenced code, TOC, mermaid)
├── themes.py             # Built-in CSS + custom CSS + DESIGN.md -> CSS
├── designmd.py           # DESIGN.md parser -> CSS variable generation
├── oklch.py              # OKLch color space palette generation
├── assets.py             # Image path resolution + copy + src rewrite
├── publisher.py          # Git ops + fingerprint cache + index/feed
├── index.py              # Index.html + RSS/Atom feed generation
├── feed.py               # RSS 2.0 XML builder
├── validator.py          # AntiSlopChecker + HTML verification
├── watch.py              # Watchdog-based local dev server
├── skills_loader.py      # Auto-discovery of skill/ folders
└── design_themes/        # Built-in DESIGN.md themes
    ├── default/
    ├── minimal/
    └── brutalist/

skills/                   # Built-in skill folders
├── article/
├── briefing/
├── changelog/
└── deck/

tests/
├── test_agent_publish.py
├── test_antislp.py
├── test_designmd.py
├── test_oklch.py
└── test_skills.py
```

## Eval

Every release verified against:

- [x] Markdown parity (tables, code blocks, links)
- [x] CSS renders without external dependencies
- [x] Git push succeeds with non-empty commit
- [x] Image assets copied and paths rewritten
- [x] TOC generated for multi-section docs
- [x] DESIGN.md round-trip generates valid CSS
- [x] Skill folders load template + assets
- [x] Anti-slop checker catches banned phrases

Run locally:

```bash
pytest tests/
```

## Roadmap

| Phase | Status |
|---|---|
| Core pipeline (MD -> HTML, themes, CLI, config, assets) | ✅ Done |
| Quality (tests, TOC, dark mode, responsive, print, a11y) | ✅ Done |
| Polish (index, RSS, OG, reading time, watch mode, init) | ✅ Done |
| Extensibility (DESIGN.md, OKLch, skills) | ✅ Done |
| Open-source readiness (README, LICENSE, CI, examples) | 🔄 In progress |
| Optional AI features (humanize, TL;DR, auto-tags) | 📋 Backlog |

See [`KANBAN.md`](./KANBAN.md) for the full tracked backlog.

## Contributing

This project uses a kanban-driven daily execution model. Each card in `KANBAN.md` maps to a single focused commit (e.g. `feat(AP-XXX): description`).

To contribute:

1. Fork the repo
2. Pick or open an issue describing what you want to change
3. Create a branch: `git checkout -b feat/AP-XXX-description`
4. Write code + tests (we use `pytest`)
5. Lint with `ruff` and `black`
6. Open a PR referencing the issue

Current priorities are cards in the **Ready** column of `KANBAN.md`.

## License

MIT
