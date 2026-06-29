#!/usr/bin/env python3
"""Claude Code post-hook — auto-publish agent output to GitHub Pages.

Drop this into your Claude Code hooks directory (or run as a standalone
script pointed at the markdown file Claude Code wrote).

Usage as Claude Code hook (`.claude/hooks/post_tool.py` or similar):
    python examples/claude_post_hook.py "$CLAUDE_OUTPUT_FILE"

Usage standalone:
    python examples/claude_post_hook.py output.md --theme editorial

Requires:
    pip install agentpub
    Agent publish config file (agent-publish.toml) with base_url set
"""

import argparse
import sys
from pathlib import Path

from agent_publish import (
    Config,
    ConversionResult,
    convert_file,
    load_config,
    publish as api_publish,
)
from agent_publish.themes import load as load_theme


def guess_entry_type(filename: str) -> str:
    """Guess the entry type category from the filename.

    Falls back to "note" for unknown patterns.
    """
    name = filename.lower()
    if "daily" in name or "briefing" in name:
        return "daily"
    if "weekly" in name or "summary" in name:
        return "weekly"
    if "research" in name or "analysis" in name:
        return "research"
    if "changelog" in name or "release" in name:
        return "note"
    return "note"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto-publish Claude Code markdown output to GitHub Pages",
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=None,
        help="Markdown file to publish (default: latest .md in working dir)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to agent-publish config",
    )
    parser.add_argument(
        "--theme",
        default="editorial",
        help="CSS theme",
    )
    parser.add_argument(
        "--skill",
        default=None,
        help="Skill template (article, briefing, changelog, deck)",
    )
    parser.add_argument(
        "--type",
        dest="entry_type",
        default=None,
        help="Entry type (auto-detected if omitted)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Convert but skip git push",
    )
    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Disable table of contents",
    )
    args = parser.parse_args()

    # 1. Find the input file
    if args.input:
        md_path = args.input
    else:
        cwd = Path.cwd()
        md_files = sorted(cwd.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not md_files:
            print("Error: No .md files found and no input path given")
            sys.exit(1)
        md_path = md_files[0]
        print(f"Auto-detected: {md_path}")

    if not md_path.exists():
        print(f"Error: {md_path} not found")
        sys.exit(1)

    # 2. Load config
    config = load_config(args.config) if args.config else load_config()
    if not args.dry_run and not config.base_url:
        print("Error: Set base_url in config or use --dry-run")
        sys.exit(1)

    # 3. Convert
    print(f"Converting {md_path.name}...")
    theme_css = load_theme(args.theme)

    skill_template = None
    skill_assets = None
    if args.skill:
        from agent_publish.skills_loader import get_builtin_skills_dir, load_skill

        skill_dir = get_builtin_skills_dir() / args.skill
        data = load_skill(skill_dir)
        skill_template = data["template"]
        skill_assets = data["assets"]

    entry_type = args.entry_type or guess_entry_type(md_path.name)

    result = convert_file(
        input_path=md_path,
        output_dir=Path(config.github_repo_path) / config.output_dir,
        entry_type=entry_type,
        custom_css=theme_css,
        show_toc=config.show_toc and not args.no_toc,
        mermaid=config.mermaid,
        author=config.author,
        site_title=config.site_title,
        skill_template=skill_template,
        skill_assets=skill_assets,
    )

    print(f"  Title: {result.title}")
    print(f"  Output: {result.output_path}")

    # 4. Publish
    if args.dry_run:
        print(f"Dry run — skipping publish")
    else:
        print("Publishing...")
        pub = api_publish(
            html_path=result.output_path,
            title=result.title,
            fingerprint=result.fingerprint,
            config=config,
            asset_paths=result.assets_copied,
        )
        if pub.success:
            print(f"  {pub.message}")
        else:
            print(f"  Failed: {pub.message}")
            sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
