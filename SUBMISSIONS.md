# Awesome List Submission Materials

Prepared PR descriptions for three awesome lists.
Submit after AP-048 (live demo site) is deployed.

---

## 1. awesome-agent-skills

**Repo:** `VoltAgent/awesome-agent-skills` or `heilcheng/awesome-agent-skills`

**Category:** Development and Testing / Context Engineering

**Entry (paste into README under appropriate category):**

```markdown
- **[thisisprabha/agent-publish](https://github.com/thisisprabha/agent-publish)** — Markdown-to-HTML publishing skills for AI agent output (article, briefing, changelog, deck)
```

**PR Title:** `Add skill: thisisprabha/agent-publish`

**PR Description:**

```
Adds agent-publish — four composable agent skills (article, briefing,
changelog, deck) that turn raw markdown output from any AI agent into
styled, publish-ready HTML with GitHub Pages deployment.

Each skill includes a SKILL.md with agentskills.io-compatible YAML
frontmatter, a custom HTML template, and processing instructions.

- **article** — Long-form narrative layout for essays and research posts
- **briefing** — Compact scannable layout for daily stand-ups and memos
- **changelog** — Date-stamped list layout for release notes
- **deck** — Full-width presentation layout for slide-like documents

Live demo: https://thisisprabha.github.io/agent-publish
PyPI: https://pypi.org/project/agentpub
```

---

## 2. awesome-llm-tools

**Repo:** Search for active `awesome-llm-tools` fork (several exist)

**Category:** Output / Publishing / Content Generation

**Entry:**

```markdown
- **[agent-publish](https://github.com/thisisprabha/agent-publish)** — Turn LLM/agent markdown output into published HTML with one command
```

**PR Title:** `Add tool: agent-publish`

**PR Description:**

```
Markdown-to-HTML publishing pipeline purpose-built for AI agent output.

agent-publish solves the "3 AM problem" — you run overnight research,
get markdown back from your agent, and want it published somewhere
without manual intervention.

- Zero-config: `agent-publish publish output.md --url your.site`
- 3 built-in CSS themes + OKLch color engine
- Python API: `from agent_publish import convert, publish`
- GitHub Pages native with fingerprint dedup
- Auto TOC, smart typography, Mermaid diagrams, RSS feed

Live demo: https://thisisprabha.github.io/agent-publish
PyPI: https://pypi.org/project/agentpub
```

---

## 3. awesome-python

**Repo:** `vinta/awesome-python`

**Category:** Text Processing (or Content Management)

**Entry:**

```markdown
- **[agent-publish](https://github.com/thisisprabha/agent-publish)** — Markdown-to-HTML pipeline for AI agents with GitHub Pages deployment.
```

**Full description (for PR body):**

```
agent-publish is a Python CLI and library that converts markdown into
publishable HTML pages and deploys them to GitHub Pages.

Built for AI agent pipelines: your agent writes markdown, agent-publish
handles everything else — conversion, theming, image optimization,
frontmatter validation, multi-format export (HTML, EPUB, PDF), and
git-based deployment with content fingerprinting.

Key features:
- `agent-publish publish file.md --url site.github.io/repo`
- Python API for embedding in agent pipelines (n8n, cron, hooks)
- Multi-format export: HTML, EPUB (zip-based), PDF (WeasyPrint)
- Image optimization: compress JPEG, PNG→WebP, EXIF stripping
- Skills system: article, briefing, changelog, deck templates
- DESIGN.md portable theme spec + OKLch color engine

pip install agentpub

Live demo: https://thisisprabha.github.io/agent-publish
Source: https://github.com/thisisprabha/agent-publish
```

---

## 1-line descriptions

- "Markdown-to-HTML publishing pipeline purpose-built for AI agent output"
- "Turn LLM-generated markdown into published web pages with one command"
- "Python CLI and library that converts agent markdown output into themed, deployable HTML"

## 3-line descriptions

- "agent-publish is a CLI and Python library that bridges the gap between AI agent output
  and published web content. It converts markdown to styled HTML, deploys to GitHub Pages
  with fingerprint dedup, and supports multi-format export (HTML, EPUB, PDF).
  `pip install agentpub`"

- "Built for the '3 AM problem' — your agent produces markdown overnight, agent-publish
  converts it into a beautiful, themed web page and pushes it live. Includes Python API
  for embedding in cron, n8n, and Claude Code hooks. `agent-publish publish output.md`"

- "Complete markdown-to-GitHub-Pages pipeline: conversion, theming (3 built-in + OKLch
  engine), image optimization, schema validation, and multi-format export. Designed as
  both a CLI tool and an importable Python library for agent workflows."
