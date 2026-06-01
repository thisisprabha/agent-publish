# agent-publish

Markdown-to-HTML pipeline for AI agents.

Converts research outputs, logs, and agent artifacts into clean, styled HTML and publishes to GitHub Pages.

## Why This Exists

The "3 AM problem": You run overnight research, get markdown output... now what? This tool bridges that gap — turning raw agent outputs into publishable web pages without manual intervention.

## Features

- **CLI-first**: `agent-publish input.md --repo path/to/site`
- **Zero-config**: Sane defaults, optional `agent-publish.toml` override
- **Cache-aware**: Prevents duplicate publishes via content fingerprinting
- **Theme system**: Pluggable CSS (default, minimal, brutalist)
- **GitHub Pages native**: Built-in push with proper cache-busting

## Install

```bash
pip install agent-publish
```

## Quick Start

```bash
# Publish a research report
agent-publish research.md --type weekly

# With custom config
agent-publish docs/*.md --config agent-publish.toml
```

## Config

```toml
# agent-publish.toml
[output]
theme = "minimal"
base_url = "https://username.github.io/repository"

[github]
auto_push = true
commit_prefix = "🤖 Agent publish:"

[patterns]
# Skip files containing these strings
exclude = ["draft", "wip"]
```

## Structure

```
src/agent_publish/
├── __init__.py
├── converter.py      # MD → HTML w/ fenced code, tables
├── publisher.py      # Git operations + cache-busting
├── validator.py      # Output verification
└── themes/
    ├── default.css
    ├── minimal.css
    └── brutalist.css
```

## Eval

Every release verified against:
- [ ] Markdown parity (tables, code blocks, links)
- [ ] CSS renders without external deps
- [ ] Git push succeeds with non-empty commit
- [ ] URL reachable via agent-browser

## License

MIT
