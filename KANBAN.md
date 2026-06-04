# KANBAN — agent-publish (Open Source)

| ID | Task | Status | Day | Notes |
|---|---|---|---|---|
| AP-001 | Create project structure (src, tests, docs) | ✅ Done | Day 1 | |
| AP-002 | Write README with concept and install instructions | ✅ Done | Day 1 | |
| AP-003 | Write design.md manifesto (design-first philosophy) | ✅ Done | Day 1 | |
| AP-004 | Wire GitHub repo + push initial commit | ✅ Done | Day 1 | https://github.com/thisisprabha/agent-publish |
| AP-005 | Add LICENSE (MIT) | ✅ Done | Day 1 | |
| AP-006 | Write design.md v0.1 — CLI skeleton | ✅ Done | Day 2 | `publish`, `index`, `config` subcommands |
| AP-007 | Set up pytest + write first failing tests | ✅ Done | Day 2 | |
| AP-008 | Implement `publish` subcommand (markdown → HTML) | ✅ Done | Day 3 | Supports `--theme`, `--custom-css`, `--date` |
| AP-009 | Implement `index` subcommand (generate index.html) | ✅ Done | Day 3 | Lists all published entries |
| AP-010 | Implement `config` subcommand (read TOML) | ✅ Done | Day 4 | |
| AP-011 | Design manifest parsing (`design.md`) | ✅ Done | Day 4 | |
| AP-012 | Write `design.md` parser | ✅ Done | Day 5 | Converts design spec to structured data |
| AP-013 | Generate base template from parsed design | ✅ Done | Day 5 | |
| AP-014 | Support custom `--design` path | ✅ Done | Day 5 | |
| AP-015 | Write Day 6 spec (fingerprint + manifest) | ✅ Done | Day 6 | |
| AP-016 | Implement content fingerprinting (SHA256) | ✅ Done | Day 6 | |
| AP-017 | Build manifest system (track slug, hash, date, url) | ✅ Done | Day 6 | |
| AP-018 | Detect duplicate content by fingerprint | ✅ Done | Day 6 | |
| AP-019 | Write manifest update logic | ✅ Done | Day 7 | |
| AP-020 | Write Day 7 spec (index, feed, nav, backlink) | ✅ Done | Day 8 | |
| AP-021 | Build navigation: prev/next links between entries | ✅ Done | Day 8 | |
| AP-022 | Add back-to-index link in each entry | ✅ Done | Day 8 | |
| AP-023 | Generate RSS/Atom feed | ✅ Done | Day 8 | |
| AP-024 | Write Day 8 spec (tests, CI, README polish) | ✅ Done | Day 9 | |
| AP-025 | Code review + refactor | ✅ Done | Day 9 | |
| AP-026 | Write comprehensive tests (pytest) | ✅ Done | Day 9 | 52 tests passing |
| AP-027 | Set up GitHub Actions CI | ✅ Done | Day 9 | `.github/workflows/ci.yml` |
| AP-028 | README polish + logo placeholder | ✅ Done | Day 9 | |
| AP-029 | DESIGN.md-driven theme system | ✅ Done | Day 10 | Parser (`designmd.py`), built-in themes, CSS generator, 16 tests |
| AP-030 | — | — | — | (reserved) |
| AP-031 | — | — | — | (reserved) |
| AP-032 | — | — | — | (reserved) |
| AP-033 | — | — | — | (reserved) |
| AP-034 | — | — | — | (reserved) |
| AP-035 | — | — | — | (reserved) |
| AP-036 | CLI wiring for DESIGN.md `--theme-design` flag | 🔄 In Progress | Day 10 | Hook `--theme-design` into `publish`, `index` commands |
| AP-037 | — | — | — | (reserved) |
| AP-038 | — | — | — | (reserved) |
| AP-039 | — | — | — | (reserved) |
| AP-040 | — | — | — | (reserved) |

---

## Legend

- ✅ Done — completed and committed
- 🔄 In Progress — active task
- 📝 Ready — next up
- ⏸️ On Hold — blocked or deprioritized

---

## Next Phase

Day 11: TBD (CLI `--theme-design` completion → integration tests)
