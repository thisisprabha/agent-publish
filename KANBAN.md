# Agent-Publish Kanban

Git-based state management for daily agent sprints.
Cron reads only this file → executes Ready tasks → commits → pushes.

---

## Done

- [x] **AP-001**: Scaffold core converter module (`src/agent_publish/converter.py`) - markdown → HTML with Jinja2 templates | Completed: 2026-06-02
- [x] **AP-002**: Create base CSS system inline (no external deps) - clean minimal style, mobile-responsive | Completed: 2026-06-02
- [x] **AP-003**: Add CLI entry point with argparse - `agent-publish convert input.md --output-dir ./dist` | Est: 45min | Completed: 2026-06-02
- [x] **AP-004**: GitHub Pages auto-deployment helper - push built HTML to `gh-pages` branch | Est: 90min | Completed: 2026-06-02
- [x] **AP-005**: Config file support (YAML) - custom CSS paths, template overrides | Est: 60min | Completed: 2026-06-02
- [x] **AP-007**: Image path resolution + copy to output directory | Est: 45min | Completed: 2026-06-02
- [x] **AP-010**: Eval/test suite - sample markdowns → HTML → verify structure | Est: 90min | Completed: 2026-06-02

---

## Review

*No tasks under review. PRs will be listed here with #number.*

---

## In Progress

*Max 2 cards. Cron picks these up and works until done or blocked.*

---

## Ready (Next Up)

- [ ] **AP-005**: Config file support (YAML) - custom CSS paths, template overrides | Est: 60min
- [ ] **AP-007**: Image path resolution + copy to output directory | Est: 45min
- [ ] **AP-008**: Table of contents generator from H2/H3 headers | Est: 45min
- [ ] **AP-011**: README polish with usage examples + GIF demo | Est: 60min

---

## Backlog

- [ ] **AP-005**: Config file support (YAML) - custom CSS paths, template overrides | Est: 60min
- [ ] **AP-006**: Fenced code block syntax highlighting (Pygments integration) | Est: 45min
- [ ] **AP-007**: Image path resolution + copy to output directory | Est: 45min
- [ ] **AP-008**: Table of contents generator from H2/H3 headers | Est: 45min
- [ ] **AP-009**: Dark mode CSS variant (media query toggle) | Est: 45min
- [ ] **AP-010**: Eval/test suite - sample markdowns → HTML → verify structure | Est: 90min
- [ ] **AP-011**: README polish with usage examples + GIF demo | Est: 60min
- [ ] **AP-012**: PyPI package prep - `setup.py`, classifiers, entry points | Est: 60min

---

## Archive

*Shipped releases / abandoned ideas. Reference only.*

---

## How This Works

1. **Cron runs at 1AM IST** via `~/.hermes/cron/agent-publish-daily`
2. **Cron loads only**: `kanban` skill (minimal) + this file (~50 lines)
3. **Picks top 2** from "Ready" column
4. **Executes each card** → commits → pushes
5. **Moves cards** Ready → In Progress → Done
6. **Telegram summary** sent to Prabha with: tasks done, commits made, blockers

**Card format:**
```
- [ ] ID: Title | Est: time | Skills: skill1, skill2
```

**Token budget per run:** ~4K loaded context (vs 15K+ for full roadmap planning)
