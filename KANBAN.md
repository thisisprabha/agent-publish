# Agent-Publish Kanban

Git-based state management for daily agent sprints.
Cron reads only this file → executes Ready tasks → commits → pushes.

---

## Done

- [x] **AP-001**: Scaffold core converter module (`src/agent_publish/converter.py`) - markdown → HTML with fenced code, tables, Pygments highlighting | Completed: 2026-06-02
- [x] **AP-002**: Create base CSS system inline (no external deps) - default, minimal, brutalist themes | Completed: 2026-06-02
- [x] **AP-003**: Add CLI entry point with argparse - `agent-publish publish input.md --theme default` | Completed: 2026-06-02
- [x] **AP-004**: GitHub Pages auto-deployment helper - git add/commit/push with fingerprint dedup cache | Completed: 2026-06-02
- [x] **AP-005**: Config file support (TOML/YAML) - custom CSS paths, template overrides, config discovery | Completed: 2026-06-02
- [x] **AP-006**: Fenced code block syntax highlighting via Pygments + CodeHilite extension | Completed: 2026-06-02
- [x] **AP-007**: Image path resolution + asset copy to output directory with src rewriting | Completed: 2026-06-02
- [x] **AP-008**: Table of contents generator from H2/H3 headers (injected via markdown TocExtension, 2+ link threshold) | Completed: 2026-06-02
- [x] **AP-010**: Eval/test suite - 16 tests covering converter, config, assets, state, validator | Completed: 2026-06-02
- [x] **AP-011**: README polish - expanded CLI reference, real examples, eval checklist, install from source | Completed: 2026-06-02

---

## Review

*No tasks under review.*

---

## In Progress

*Max 2 cards. Cron picks these up and works until done or blocked.*

---

## Ready (Next Up)

- [x] **AP-013**: Fix `template.format()` crash — user markdown containing `{braces}` causes KeyError. Replace `.format()` with safe substitution (e.g., `string.Template` or manual replace). Add test with markdown containing `{example}` text. | Completed: 2026-06-02
- [x] **AP-014**: Fix empty slug edge case — `_clean_slug()` returns empty string for titles with all special chars, producing filenames like `2024-01-01-.html`. Add fallback to "untitled" + add test. | Completed: 2026-06-02

---

## Backlog

### Phase 1: Bug fixes (do these first)

- [x] **AP-015**: Remove orphaned `state.py` — duplicate fingerprint system that's never called from cli.py or converter.py. Publisher has its own cache. Delete state.py, remove its tests if any, keep publisher cache as single source of truth. | Completed: 2026-06-03
- [x] **AP-016**: Add `--version` flag to CLI using version from pyproject.toml | Completed: 2026-06-03
- [x] **AP-017**: Fix validator `verify_file` — H1 regex fails on titles with inline HTML or attributes. Use proper HTML parser (html.parser) instead of regex. | Completed: 2026-06-03

### Phase 2: CSS polish + transitions

- [x] **AP-009**: Dark mode CSS — add `@media (prefers-color-scheme: dark)` block to all three themes. Dark variants: default (warm dark), minimal (true black), brutalist (light alt). Test with sample HTML. | Completed: 2026-06-03
- [x] **AP-018**: CSS transitions — add smooth scroll (`html { scroll-behavior: smooth }`), heading anchor hover reveal, table row hover highlight (`tr:hover`), link underline transition, code block hover border. All three themes. Zero JS. | Completed: 2026-06-03
- [x] **AP-019**: Fix brutalist theme — missing styles for `.meta`, `.back`, `blockquote`, `pre code`. Add responsive rules. Complete the theme so it's actually usable. | Completed: 2026-06-03 | Skills: css
- [ ] **AP-020**: Accessibility pass — add `:focus-visible` outlines, skip-to-content link in template, `aria-label` on nav elements, ensure color contrast meets WCAG AA in all themes. | Est: 45min | Skills: css, html
- [ ] **AP-021**: Responsive breakpoints — add `@media` queries for mobile (<640px) and tablet (<1024px) to all themes. Test: heading sizes, table horizontal scroll, code block overflow. | Est: 45min | Skills: css
- [ ] **AP-022**: Print stylesheet — add `@media print` to minimal and brutalist (default already has one). Hide nav, expand links, ensure clean page breaks. | Est: 30min | Skills: css

### Phase 3: Zero-token features

- [ ] **AP-023**: Index page generator — `agent-publish index --output-dir ./dist` scans all published HTML files, extracts title/date/type from meta, generates a styled `index.html` listing all pages sorted by date. Use same theme as individual pages. | Est: 90min | Skills: python
- [ ] **AP-024**: RSS/Atom feed — generate `feed.xml` alongside index page. Extract title, date, first paragraph as description. Standard RSS 2.0 format. Update on every publish. | Est: 60min | Skills: python
- [ ] **AP-025**: Reading time + OG meta tags — calculate reading time (word count / 200 WPM), add to `.meta` line in template. Generate `<meta property="og:title/description/image">` from title + first paragraph. Add `--og-image` flag for custom social image. | Est: 45min | Skills: python, html
- [ ] **AP-026**: `--watch` mode — local dev server with `http.server`, auto-rebuild on .md file change using `watchdog`. Serve on localhost:8080. Print URL on start. | Est: 60min | Skills: python
- [ ] **AP-027**: `--init` command — scaffold `agent-publish.toml` config file in current directory with commented defaults. Interactive prompts for theme, output dir, git repo path. | Est: 30min | Skills: python
- [ ] **AP-028**: Mermaid diagram support — detect ` ```mermaid` fenced blocks, inject mermaid.js CDN script (only when mermaid blocks exist), render client-side. Zero tokens. | Est: 45min | Skills: python, js
- [ ] **AP-029**: Favicon + site metadata — add favicon support via config (`favicon = "path/to/icon.png"`), generate `<link rel=icon>`. Add site title/author config for consistent headers. | Est: 30min | Skills: python, html

### Phase 4: Architecture upgrades (inspired by open-design)

- [ ] **AP-036**: DESIGN.md portable theme spec — replace inline CSS strings in `themes.py` with structured Markdown files (`themes/default/DESIGN.md`, `themes/minimal/DESIGN.md`, etc.). Each DESIGN.md defines: color tokens, typography, spacing, layout, motion, and anti-patterns as readable sections. Converter reads DESIGN.md → generates CSS at build time. Non-devs can edit themes without touching Python. Ref: open-design's 9-section DESIGN.md schema. | Est: 120min | Skills: python, css
- [ ] **AP-037**: Skill-as-folder extensibility — add `skills/` directory pattern where each output type (article, briefing, changelog, deck) is a folder containing `SKILL.md` (instructions + template hints) + `template.html` (custom HTML template) + optional `assets/`. CLI auto-discovers skills: `agent-publish publish report.md --skill briefing`. Drop a folder in, it appears as an option. Ref: open-design's skill-as-folder convention. | Est: 90min | Skills: python
- [ ] **AP-038**: Anti-slop quality gate — add `validator.py` post-conversion checklist that scores output HTML on 5 dimensions: (1) no repeated filler phrases like "comprehensive analysis", "it's worth noting" (2) heading hierarchy is clean H1→H2→H3 (3) no empty sections (4) code blocks have language tags (5) no orphan links. Run automatically, print warnings. `--strict` flag fails the build on violations. Zero tokens — pure regex/heuristic checks. | Est: 60min | Skills: python
- [ ] **AP-039**: Deterministic OKLch color palettes — replace hand-picked hex colors in themes with generated OKLch palettes. Define 5 curated visual directions: Editorial (serif, warm), Modern Minimal (sans, neutral), Warm Soft (rounded, muted), Tech Utility (mono, sharp), Brutalist (mono, high contrast). Each direction locks a palette + font stack in DESIGN.md. `--direction editorial` flag on CLI. Prevents theme "freestyle" — colors always harmonize. | Est: 90min | Skills: python, css

### Phase 5: Open-source readiness

- [ ] **AP-012**: PyPI package prep — verify pyproject.toml classifiers, add LICENSE file (MIT), test `pip install` from source, create GitHub release workflow. | Est: 60min | Skills: python, ci
- [ ] **AP-030**: Add LICENSE file (MIT) + CONTRIBUTING.md with dev setup, code style, PR process. | Est: 30min | Skills: docs
- [ ] **AP-031**: GitHub Actions CI — run pytest on push/PR, lint with ruff, build wheel, test `pip install` from wheel. Badge in README. | Est: 60min | Skills: ci
- [ ] **AP-032**: Example gallery — create `examples/` with 5 sample markdowns (research report, daily briefing, code walkthrough, meeting notes, changelog) + pre-built HTML for each theme. | Est: 60min | Skills: docs

### Phase 6: Optional AI enhancements (tokens only when user opts in)

- [ ] **AP-033**: `--humanize` flag architecture — add optional post-processing hook in converter pipeline. When `--humanize` is passed, pipe markdown through an LLM rewrite before HTML conversion. Support `AGENT_PUBLISH_API_KEY` env var. If no key, skip gracefully with warning. Core pipeline stays zero-token. | Est: 90min | Skills: python
- [ ] **AP-034**: Auto TL;DR — when `--tldr` flag passed, generate 2-3 sentence summary and inject at top of HTML as a styled callout. Requires API key. Falls back to first paragraph extraction (zero-token) if no key. | Est: 60min | Skills: python
- [ ] **AP-035**: Smart tagging — when `--auto-tag` passed, classify content into categories (research, briefing, changelog, tutorial, etc.) and add as HTML meta tags + visible badges. Zero-token fallback: keyword matching. | Est: 60min | Skills: python

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

**Promotion rule:** When Ready is empty, promote the next 2 cards from the topmost Backlog phase. Phases are ordered: bug fixes → CSS → zero-token features → architecture (open-design inspired) → open-source → AI enhancements.

**Token budget per run:** ~4K loaded context
