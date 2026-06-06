# Contributing to Agent Publish

Thanks for hacking on this. Agent Publish is a small, sharp tool and we keep it that way.

## Setup

```bash
git clone https://github.com/thisisprabha/agent-publish.git
cd agent-publish
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run Tests

```bash
pytest
# With coverage
pytest --cov=agent_publish --cov-report=term-missing
```

## Code Style

- **Ruff** for lint + import sorting
- **Black** for formatting (88 char line limit)
- Run before committing:
  ```bash
  ruff check src tests
  ruff format src tests
  ```

## PR Process

1. Open an issue or comment on an existing one so we do not duplicate work
2. Fork + branch from `main`
3. One logical change per PR
4. Tests must pass. New features need new tests.
5. Update `KANBAN.md` if your PR closes a card: move it to Done
6. Update `README.md` if user-facing behavior changes

## Architecture Quick Reference

```
src/agent_publish/
  __init__.py          # Public API (open, publish, index, init)
  cli.py               # argparse entry point
  converter.py         # Markdown to HTML conversion pipeline
  config.py            # TOML/YAML config discovery and validation
  publisher.py           # Git add / commit / push with fingerprint cache
  themes.py              # Built-in CSS themes + OKLch + DESIGN.md parser
  templates.py           # HTML template system
  skills.py              # Skill-as-folder loader (SKILL.md + template.html)
  state.py               # (removed — kept in publisher.py)
tests/                   # Pytest suite (run with pytest)
examples/                # Sample markdowns + pre-built HTML
```

## Theme Contributions

### Option A: Built-in CSS
Add a new theme in `src/agent_publish/themes.py`, wire into `THEMES` dict, add a test.

### Option B: DESIGN.md Portable Theme
Create a `DESIGN.md` file with structured CSS blocks. See `docs/DESIGN.md` for the spec.

### Option C: Skill Folder
Create a folder under `skills/` with `SKILL.md` + `template.html` + optional `assets/`.
See `src/agent_publish/skills.py` for the loader interface.

## Commit Messages

Format: `type(AP-XXX): description`

- `feat` — new feature
- `fix` — bugfix
- `docs` — docs only
- `test` — test only
- `refactor` — no behavior change
- `chore` — tooling, deps, CI

## License

By contributing, you agree that your code will be released under the MIT License.
