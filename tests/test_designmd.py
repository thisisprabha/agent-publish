from pathlib import Path

import pytest

from agent_publish import designmd
from agent_publish.themes import THEMES, list_themes, load

# ── helpers ──

MINIMAL_TEXT = """---
version: alpha
name: "Minimal"
colors:
  bg: "#fff"
  fg: "#111"
typography:
  font-family:
    sans: 'system-ui'
---

## Visual Theme & Atmosphere

Pure utility.
"""

FULL_TEXT = """---
version: alpha
name: "Full"
colors:
  bg: "#faf8f5"
  fg: "#1c1917"
  muted: "#78716c"
  accent: "#0077b6"
  accent-2: "#48cae4"
  border: "#e7e5e4"
  surface: "#fff"
  code-bg: "#f5f5f0"
  dark:
    bg: "#1a1816"
    fg: "#e8e4df"

typography:
  font-family:
    sans: 'system-ui'
  base:
    size: 16
    weight: 400
    line-height: 1.7
  h1:
    size: 26
    weight: 700
    line-height: 1.2
  h2:
    size: 18
    weight: 600
    line-height: 1.3

spacing:
  scale: [4, 8, 12, 16, 24, 32, 48]

rounded:
  sm: 4
  md: 6
  lg: 8
---

## Visual Theme & Atmosphere

Warm, clean, readable.

## Color Palette & Roles

| Token | Value | Role |
|-------|-------|------|
| bg | #faf8f5 | Page canvas |
| fg | #1c1917 | Body text |

## Agent Prompt Guide

1. Use the warm palette.
2. Serif for headings only.
"""


def _write_design(tmp_path: Path, text: str) -> Path:
    """Write a DESIGN.md into a temp directory and return its path."""
    d = tmp_path / "DESIGN.md"
    d.write_text(text, encoding="utf-8")
    return d


# ── designmd.py parser tests ──

def test_load_design_minimal(tmp_path: Path):
    d = designmd.load_design(_write_design(tmp_path, MINIMAL_TEXT))
    assert d.name == "Minimal"
    assert d.tokens.colors["bg"] == "#fff"
    assert d.tokens.colors["fg"] == "#111"


def test_load_design_full(tmp_path: Path):
    d = designmd.load_design(_write_design(tmp_path, FULL_TEXT))
    assert d.tokens.colors["accent"] == "#0077b6"
    assert d.tokens.colors["dark"]["bg"] == "#1a1816"


def test_load_design_no_yaml(tmp_path: Path):
    d = designmd.load_design(_write_design(tmp_path, "No yaml frontmatter here."))
    assert d.name == ""
    assert d.tokens.colors == {}


def test_generate_css_produces_required_rules(tmp_path: Path):
    design_file = _write_design(tmp_path, MINIMAL_TEXT)
    parsed = designmd.load_design(design_file)
    css = designmd.generate_css(parsed)
    assert ":root{" in css


def test_generate_css_includes_dark_mode(tmp_path: Path):
    """When a sibling base.css with @media dark exists, it is appended."""
    d = _write_design(tmp_path, FULL_TEXT)
    b = d.with_name("base.css")
    b.write_text("@media (prefers-color-scheme:dark){body{color:#fff}}", encoding="utf-8")
    parsed = designmd.load_design(d)
    css = designmd.generate_css(parsed)
    assert "@media (prefers-color-scheme:dark)" in css


def test_generate_css_includes_print_media(tmp_path: Path):
    d = _write_design(tmp_path, FULL_TEXT)
    b = d.with_name("base.css")
    b.write_text("@media print{body{background:#fff}}", encoding="utf-8")
    parsed = designmd.load_design(d)
    css = designmd.generate_css(parsed)
    assert "@media print" in css


def test_generate_css_no_crash_on_empty_guide(tmp_path: Path):
    parsed = designmd.load_design(_write_design(tmp_path, "---\n---\n"))
    css = designmd.generate_css(parsed)
    assert len(css) > 0


# ── Theme loading tests ──

def test_list_themes():
    themes = list_themes()
    assert "default" in themes
    assert "minimal" in themes
    assert "brutalist" in themes


def test_load_default_theme():
    css = load("default")
    assert "--bg:" in css
    assert "font-family" in css


def test_load_minimal_theme():
    css = load("minimal")
    assert "#fff" in css
    assert "max-width:680px" in css.replace(" ", "")


def test_load_brutalist_theme():
    css = load("brutalist")
    assert "#000" in css or "#0f0" in css
    assert "border:2pxsolid" in css.replace(" ", "")


def test_load_unknown_theme_falls_back():
    css = load("nonexistent")
    assert "--bg:" in css  # Gets default


def test_load_custom_path(tmp_path: Path):
    custom = tmp_path / "custom.css"
    custom.write_text("body{ color: pink }")
    css = load("custom", custom_path=custom)
    assert "pink" in css


def test_themes_dict_keys():
    assert set(THEMES.keys()) == {"default", "minimal", "brutalist"}


def test_every_builtin_theme_loads():
    """Ensure all themes produce non-empty CSS with :root."""
    for name in list_themes():
        css = load(name)
        assert ":root{" in css, f"Theme {name} missing :root"
        assert len(css) > 500, f"Theme {name} seems too short"


def test_designmd_file_load(tmp_path: Path):
    """Load DESIGN.md from a real file path."""
    d = designmd.load_design(_write_design(tmp_path, MINIMAL_TEXT))
    assert d.name == "Minimal"
    assert d.sections.get("visual theme & atmosphere", "") == "Pure utility."


# ── CLI --theme-design integration tests ──

def test_cli_theme_design_flag_parsed_by_config(tmp_path: Path):
    """theme_design_path from CLI merges correctly into config."""
    from agent_publish.config import Config, merge_with_cli_args
    design_file = tmp_path / "design.md"
    design_file.write_text("---\n---\n")
    cfg = Config(github_repo_path="/tmp/repo")
    result = merge_with_cli_args(cfg, theme_design_path=str(design_file))
    assert result.theme_design_path == design_file


def test_cli_theme_design_file_must_exist():
    """Non-existent theme_design_path raises FileNotFoundError."""
    from agent_publish.config import Config, merge_with_cli_args
    cfg = Config(github_repo_path="/tmp/repo")
    with pytest.raises(FileNotFoundError):
        merge_with_cli_args(cfg, theme_design_path="/tmp/nonexistent.md")


def test_themes_load_with_design_path(tmp_path: Path):
    """themes.load('default', design_path=...) injects DESIGN.md CSS."""
    design_file = _write_design(tmp_path, FULL_TEXT)
    css = load("default", design_path=design_file)
    assert "#faf8f5" in css or "#1c1917" in css


def test_themes_load_design_path_priority_over_custom_path(tmp_path: Path):
    """design_path overrides custom_path when both given."""
    design_file = _write_design(tmp_path, FULL_TEXT)
    custom_css = tmp_path / "custom.css"
    custom_css.write_text("body{ color: pink }")
    css = load("default", design_path=design_file, custom_path=custom_css)
    assert "#faf8f5" in css or "#1c1917" in css
    assert "pink" not in css


def test_cli_help_shows_theme_design_flag():
    """Ensure --theme-design appears in CLI help output."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "agent_publish.cli", "publish", "--help"],
        capture_output=True,
        text=True,
    )
    assert "--theme-design" in result.stdout
