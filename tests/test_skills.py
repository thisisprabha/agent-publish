"""Tests for the skills loader system (AP-037)."""

import tempfile
from pathlib import Path

import pytest

from agent_publish.config import Config, merge_with_cli_args
from agent_publish.converter import convert_file
from agent_publish.skills_loader import (
    discover_skills,
    get_builtin_skills_dir,
    load_skill,
)


def test_get_builtin_skills_dir():
    """Test builtin skills directory exists and contains the four sample skills."""
    d = get_builtin_skills_dir()
    assert d.exists()
    assert d.is_dir()
    names = {child.name for child in d.iterdir() if child.is_dir()}
    assert {"article", "briefing", "changelog", "deck"}.issubset(names)


def test_discover_builtin_skills():
    """Test discover_skills lists the four built-in skills."""
    skills = discover_skills(get_builtin_skills_dir())
    assert skills == ["article", "briefing", "changelog", "deck"]


def test_discover_skills_empty():
    """Test discover_skills returns empty list for nonexistent path."""
    assert discover_skills(Path("/nonexistent/skills")) == []


def test_load_skill_article():
    """Test loading the article skill returns expected keys."""
    skill_dir = get_builtin_skills_dir() / "article"
    data = load_skill(skill_dir)
    assert data["name"] == "article"
    assert "template" in data
    assert data["skill_md"].startswith("# Article")
    assert "{page_title}" in data["template"]
    assert "{css}" in data["template"]
    assert isinstance(data["assets"], list)


def test_load_skill_briefing():
    """Test loading the briefing skill returns a different template."""
    skill_dir = get_builtin_skills_dir() / "briefing"
    data = load_skill(skill_dir)
    assert data["name"] == "briefing"
    assert "body class=\"briefing\"" in data["template"]


def test_load_skill_changelog():
    """Test loading the changelog skill returns a changelog-tagged template."""
    skill_dir = get_builtin_skills_dir() / "changelog"
    data = load_skill(skill_dir)
    assert data["name"] == "changelog"
    assert "body class=\"changelog\"" in data["template"]


def test_load_skill_deck():
    """Test loading the deck skill returns a deck-tagged template."""
    skill_dir = get_builtin_skills_dir() / "deck"
    data = load_skill(skill_dir)
    assert data["name"] == "deck"
    assert "body class=\"deck\"" in data["template"]


def test_load_skill_missing_skill_md():
    """Test FileNotFoundError when SKILL.md is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad_skill"
        bad.mkdir()
        (bad / "template.html").write_text("noop")
        with pytest.raises(FileNotFoundError):
            load_skill(bad)


def test_load_skill_missing_template():
    """Test FileNotFoundError when template.html is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad_skill"
        bad.mkdir()
        (bad / "SKILL.md").write_text("# Bad")
        with pytest.raises(FileNotFoundError):
            load_skill(bad)


def test_skill_template_override_in_converter():
    """Test skill_template takes precedence over DEFAULT_TEMPLATE and template_override."""
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "test.md"
        md.write_text("# Skill Override\n\nContent.")
        tpl_override = Path(tmp) / "override.html"
        tpl_override.write_text(
            '<!DOCTYPE html><html><head><title>{title}</title></head>'
            '<body><h1>{title}</h1><style>{css}</style><div class="body">{body}</div></body></html>'
        )
        skill_tpl = (
            '<!DOCTYPE html><html><head><title>{html_title}</title></head>'
            '<body class="skill-body"><h1>{page_title}</h1><style>{css}</style>'
            '<div class="skill-body">{body}</div></body></html>'
        )
        result = convert_file(
            md, Path(tmp), "daily",
            template_override=tpl_override,
            skill_template=skill_tpl,
        )
        html = result.output_path.read_text()
        assert 'class="skill-body"' in html
        assert '<div class="body">' not in html


def test_skill_assets_copied():
    """Test skill_assets are copied into the output directory."""
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "test.md"
        md.write_text("# Assets\n\nContent.")
        assets_dir = Path(tmp) / "assets"
        assets_dir.mkdir()
        asset = assets_dir / "logo.png"
        asset.write_bytes(b"fake-png")
        result = convert_file(
            md, Path(tmp), "daily",
            skill_assets=[asset],
        )
        copied = Path(tmp) / "logo.png"
        assert copied.exists()
        assert copied.read_bytes() == b"fake-png"
        assert copied in result.assets_copied


# ---- CLI integration tests ----

def test_cli_publish_skill_flag():
    """Test --skill flag is accepted in publish command."""
    import subprocess
    import sys
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "report.md"
        md.write_text("# Daily Brief\n\nUpdates.")
        result = subprocess.run(
            [
                sys.executable, "-m", "agent_publish.cli",
                "publish", str(md),
                "--dry-run",
                "--skill", "briefing",
            ],
            capture_output=True, text=True, cwd=tmp,
        )
        assert result.returncode == 0, result.stderr
        assert "Converted:" in result.stdout


def test_cli_watch_skill_flag():
    """Test --skill flag appears in watch command help."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "agent_publish.cli", "watch", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "--skill" in result.stdout


def test_merge_with_cli_args_skill():
    """Test merge_with_cli_args passes through the skill field."""
    cfg = Config(skill=None)
    merged = merge_with_cli_args(cfg, skill="article")
    assert merged.skill == "article"
