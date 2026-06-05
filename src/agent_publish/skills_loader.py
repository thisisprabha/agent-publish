"""Skills loader for agent-publish.

Auto-discovers and loads skill folders containing SKILL.md + template.html.
"""

from pathlib import Path
from typing import Dict, List, Optional


def get_builtin_skills_dir() -> Path:
    """Return the package-level built-in skills directory."""
    return Path(__file__).parent / "skills"


def discover_skills(base_path: Path) -> List[str]:
    """List skill directory names under *base_path* that contain SKILL.md.

    Args:
        base_path: Directory to scan for skill folders.

    Returns:
        Alphabetically sorted list of skill names.
    """
    if not base_path.exists():
        return []
    skills: List[str] = []
    for child in base_path.iterdir():
        if child.is_dir() and (child / "SKILL.md").exists():
            skills.append(child.name)
    return sorted(skills)


def load_skill(skill_path: Path) -> Dict[str, object]:
    """Load a skill folder into its constituent parts.

    Args:
        skill_path: Path to a skill directory.

    Returns:
        Dict with keys:
        - "name": skill folder name
        - "skill_path": absolute path to skill folder
        - "skill_md": raw contents of SKILL.md
        - "template": raw contents of template.html
        - "assets": list of absolute paths to files in assets/ (empty if none)

    Raises:
        FileNotFoundError: if SKILL.md or template.html is missing.
    """
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_path}")
    skill_md_path = skill_path / "SKILL.md"
    template_path = skill_path / "template.html"
    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md missing in skill: {skill_path}")
    if not template_path.exists():
        raise FileNotFoundError(f"template.html missing in skill: {skill_path}")

    skill_md = skill_md_path.read_text(encoding="utf-8")
    template = template_path.read_text(encoding="utf-8")
    assets_dir = skill_path / "assets"
    assets: List[Path] = []
    if assets_dir.exists():
        assets = sorted(
            [p.resolve() for p in assets_dir.iterdir() if p.is_file()],
            key=lambda p: p.name,
        )

    return {
        "name": skill_path.name,
        "skill_path": skill_path.resolve(),
        "skill_md": skill_md,
        "template": template,
        "assets": assets,
    }
