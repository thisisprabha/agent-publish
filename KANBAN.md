# Agent-Publish Kanban

Git-based state management for daily agent sprints.
Cron reads only this file → executes Ready tasks → commits → pushes.

---

## Done

- [x] **AP-035**: Smart tagging — zero-token keyword extraction + LLM enhancement, `--tags` flag, CSS badge styles. | Completed: 2026-06-08
- [x] **AP-034**: Auto TL;DR — `--tldr` flag architecture with LLM + zero-token fallback, styled callout injection. | Completed: 2026-06-07
- [x] **AP-033**: `--humanize` flag architecture — optional post-processing hook in converter pipeline. When `--humanize` passed, pipe markdown through LLM rewrite before HTML conversion. Support `AGENT_PUBLISH_API_KEY` env var. Skip gracefully if no key. | Completed: 2026-06-07
- [x] **AP-012**: PyPI package prep — verify pyproject.toml classifiers, add LICENSE file (MIT), test `pip install` from source, create GitHub release workflow. | Completed: 2026-06-07
- [x] **AP-030**: Add LICENSE file (MIT) + CONTRIBUTING.md with dev setup, code style, PR process. | Completed: 2026-06-07
- [x] **AP-031**: GitHub Actions CI — run pytest on push/PR, lint with ruff, build wheel, test `pip install` from wheel. | Completed: 2026-06-07
- [x] **AP-001**: Scaffold core converter module (`src/agent_publish/converter.py`) — markdown → HTML with fenced code, tables, Pygments highlighting | Completed: 2026-06-02
- [x] **AP-002**: Create base CSS system inline (no external deps) — default, minimal, brutalist themes | Completed: 2026-06-02
- [x] **AP-003**: Add CLI entry point with argparse — `agent-publish publish input.md --theme default` | Completed: 2026-06-02
- [x] **AP-004**: GitHub Pages auto-deployment helper — git add/commit/push with fingerprint dedup cache | Completed: 2026-06-02
- [x] **AP-005**: Config file support (TOML/YAML) — custom CSS paths, template overrides, config discovery | Completed: 2026-06-02
- [x] **AP-006**: Fenced code block syntax highlighting via Pygments + CodeHilite extension | Completed: 2026-06-02
- [x] **AP-007**: Image path resolution + asset copy to output directory with src rewriting | Completed: 2026-06-02
- [x] **AP-010**: Eval/test suite — 16 tests covering converter, config, assets, state, validator | Completed: 2026-06-02
- [x] **AP-013**: Fix `template.format()` crash — safe substitution with `_safe_format()`, test with `{example}` markdown | Completed: 2026-06-02
- [x] **AP-014**: Fix empty slug edge case — `_clean_slug()` fallback to "untitled", tests for all-special-char titles | Completed: 2026-06-02
- [x] **AP-015**: Remove orphaned `state.py` — duplicate fingerprint system, deleted, kept publisher cache as single source | Completed: 2026-06-02
- [x] **AP-016**: Add `--version` flag to CLI using version from pyproject.toml | Completed: 2026-06-02
- [x] **AP-017**: Fix validator `verify_file` — replaced H1 regex with html.parser for titles with inline HTML | Completed: 2026-06-02
- [x] **AP-009**: Dark mode CSS — `@media (prefers-color-scheme: dark)` for all three themes | Completed: 2026-06-02
- [x] **AP-018**: CSS transitions — smooth scroll, heading anchor hover, table row hover, link underline transition, code block hover border | Completed: 2026-06-02
- [x] **AP-019**: Fix brutalist theme — added `.meta`, `.back`, `blockquote`, `pre code` styles, responsive rules | Completed: 2026-06-02
- [x] **AP-020**: Accessibility pass — `:focus-visible` outlines, skip-to-content link, `aria-label` on nav, WCAG AA contrast | Completed: 2026-06-02
- [x] **AP-021**: Responsive breakpoints — mobile (<640px) and tablet (<1024px) for all themes | Completed: 2026-06-02
- [x] **AP-022**: Print stylesheet — `@media print` for minimal and brutalist, hide nav, expand links, clean page breaks | Completed: 2026-06-02
- [x] **AP-023**: Index page generator — `agent-publish index` scans HTML, extracts title/date/type, generates styled `index.html` | Completed: 2026-06-02
- [x] **AP-024**: RSS/Atom feed — `feed.xml` alongside index, standard RSS 2.0 format | Completed: 2026-06-02
- [x] **AP-025**: Reading time + OG meta tags — word count / 200 WPM, `<meta property="og:*">`, `--og-image` flag | Completed: 2026-06-02
- [x] **AP-026**: `--watch` mode — local dev server with `http.server`, auto-rebuild on .md change via `watchdog`, localhost:8080 | Completed: 2026-06-02
- [x] **AP-027**: `--init` command — scaffold `agent-publish.toml` with commented defaults, interactive prompts for theme/output dir/git | Completed: 2026-06-02
- [x] **AP-028**: Mermaid diagram support — detect `` ```mermaid `` blocks, inject mermaid.js CDN only when needed, client-side render | Completed: 2026-06-02
- [x] **AP-029**: Favicon + site metadata — `favicon` config/CLI, `site_title`, `author` wired into template, favicon copied to output | Completed: 2026-06-05
- [x] **AP-036**: DESIGN.md portable theme spec — structured Markdown theme files, converter reads DESIGN.md → generates CSS at build time, 16 tests | Completed: 2026-06-06
- [x] **AP-008**: TOC sidebar — `--toc` / `--no-toc` CLI flag, `show_toc` config, sticky desktop CSS, collapsible mobile | Completed: 2026-06-05
- [x] **AP-040**: Fix CLI `--template` crash — use `args.template_override`, add regression test | Completed: 2026-06-05
- [x] **AP-037**: Skill-as-folder extensibility — `skills/` directory with `SKILL.md` + `template.html` + optional `assets/`. CLI auto-discovers: `--skill briefing`. 4 built-in skills, 14 tests | Completed: 2026-06-06
- [x] **AP-011**: README rewrite — accurate feature list matching actual code, install from source instructions, CLI table, theme docs, architecture tree, contributing section, 5 example markdowns. | Completed: 2026-06-06
- [x] **AP-038**: Interactive post preview — `--preview` spins up ephemeral HTTP server on :8765 with draft HTML, auto-adds `<meta name="robots" content="noindex">`. LiveReload on file change. SIGINT (Ctrl+C) stops server and deletes temp files. | Completed: 2026-06-08
- [x] **AP-032**: Example gallery — pre-built HTML for all themes (6 markdowns × 3 themes = 18 HTML files) | Completed: 2026-06-07

---

## Review

*No tasks under review.*

---

## In Progress

- [ ] **AP-036**: Multi-format export plugin — `--format epub,pdf` alongside `--to-gh`. Hook-based architecture: `register_exporter(ext, callable)`. Built-in: markdown (passthrough), html (default), epub (zip-based), pdf (weasyprint optional). | Est: 90min | Skills: python, hooks
- [ ] **AP-037**: Image optimization pipeline — when `--optimize-images` passed, compress JPEG/PNG in-place, convert oversized PNG → WebP, strip EXIF. Zero dependencies: pure Python PIL or skip. Generate `images_report.json` with before/after sizes. | Est: 75min | Skills: python, image-processing

---

## Ready (Next Up)

- [ ] **AP-039**: YAML frontmatter schema extensibility — make frontmatter validation pluggable. User can supply custom `.agent_publish_schema.yaml` in repo root. If found, merge with built-in schema. Support `required` fields, `type` (str/int/date/bool/list), `default`, `one_of` enum. Validate on every build. | Est: 90min | Skills: python, yaml

- [x] **AP-041**: Upgrade default DESIGN.md theme system — inspired by open-design.ai editorial principles. Current default theme has 4 bugs + weak design: (1) `border-top` on h2 should be a left accent bar (`border-left: 3px solid var(--accent)`) not a top rule; (2) `border-collapse:collapse` + `border-radius` + `overflow:hidden` on tables breaks in WebKit — border-radius never renders; (3) dark mode is broken: `--surface:#000000` == `--bg:#000000`, tables invisible in dark mode; (4) 150+ lines of Pygments CSS injected even when there are no code blocks. Design goals: strong typographic hierarchy (display serif H1, weight/size variation across H2/H3/body/meta/eyebrow), clean hairline-only table rows (no box-border), TOC as slim left-ruled list not a box, dark mode with luminance-stepped surfaces. Reference: `nexu-io/open-design` DESIGN.md format — 9-section schema covering palette, type, spacing, elevation, do/don'ts. Ship an updated `design_themes/default/DESIGN.md` that an agent can read and regenerate the CSS from. Also add a second built-in theme `editorial` based on warm off-white (#FAFAF8), off-black (#1A1916), left-bar section accents, serif display headlines. | Est: 2h | Completed: 2026-06-09

---

## Backlog

### Phase 6: Optional AI enhancements (tokens only when user opts in)

*All Phase 6 tasks promoted to Ready.*

---

## Archive

*Shipped releases / abandoned ideas. Reference only.*

---

## How This Works

1. **Cron runs every 5h** via Hermes cron
2. **Cron loads only**: `kanban-codex-lane` skill + this file
3. **Picks top 2** from "Ready" column
4. **Executes each card** → writes code → runs tests → commits → pushes
5. **Moves cards** Ready → In Progress → Done
6. **Telegram summary** sent to Prabha

**Card format:**
```
- [ ] **AP-XXX**: Description | Est: time | Skills: skill1, skill2
```

**Promotion rule:** When Ready is empty, promote the next 2 cards from the topmost Backlog phase. Phases are ordered: architecture → open-source → AI enhancements.

**Token budget per run:** ~4K loaded context