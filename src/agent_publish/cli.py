"""CLI for agent-publish."""

import argparse
import importlib.metadata
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table

from .config import load_config, merge_with_cli_args
from .converter import convert_file
from .index import generate_index_and_feed
from .publisher import GitPublisher
from .validator import Validator, AntiSlopChecker
from .watch import WatchServer

console = Console()


def _get_version() -> str:
    """Get version from installed package or pyproject.toml."""
    try:
        return importlib.metadata.version("agent-publish")
    except importlib.metadata.PackageNotFoundError:
        pass
    # Fallback: read repo pyproject.toml
    pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject.exists():
        try:
            import toml
            cfg = toml.load(pyproject)
            return cfg["project"]["version"]
        except Exception:
            pass
    return "unknown"


def _publish_cmd(args):
    """Handle the publish subcommand."""
    # Load config
    cfg = load_config(args.config)
    cfg = merge_with_cli_args(
        cfg,
        theme=args.theme,
        custom_css_path=args.custom_css,
        theme_design_path=args.theme_design,
        template_override=args.template_override,
        base_url=args.url,
        repo_path=args.repo,
        mermaid=not args.no_mermaid,
        favicon=args.favicon,
        author=args.author,
        site_title=args.site_title,
        show_toc=not args.no_toc,
        strict=args.strict,
        direction=args.direction,
        skill=args.skill,
        humanize=args.humanize,
    )

    # Resolve skill template and assets if requested
    skill_template: Optional[str] = None
    skill_assets: Optional[List[Path]] = None
    if cfg.skill:
        from .skills_loader import get_builtin_skills_dir, load_skill
        skill_dir = get_builtin_skills_dir() / cfg.skill
        try:
            skill_data = load_skill(skill_dir)
            skill_template = skill_data["template"]
            skill_assets = skill_data["assets"]
        except FileNotFoundError as exc:
            console.print(f"[red]Error: {exc}[/red]")
            sys.exit(1)

    repo_path = Path(cfg.github_repo_path)
    base_url = cfg.base_url

    if not base_url and not args.dry_run:
        console.print("[red]Error: --url or output.base_url in config required[/red]")
        sys.exit(1)

    # Load theme CSS
    from . import themes
    if cfg.direction:
        theme_css = themes.load("default", direction=cfg.direction)
    elif cfg.theme_design_path:
        theme_css = themes.load("default", design_path=cfg.theme_design_path)
    elif cfg.custom_css_path:
        theme_css = themes.load("default", custom_path=cfg.custom_css_path)
    else:
        theme_css = themes.load(cfg.theme)

    # Process files
    results = []
    for input_file in args.input:
        input_path = Path(input_file)
        if not input_path.exists():
            console.print(f"[red]Error: {input_path} not found[/red]")
            continue

        # Convert
        with console.status(f"[yellow]Converting {input_path.name}...[/yellow]"):
            result = convert_file(
                input_path=input_path,
                output_dir=repo_path / cfg.output_dir,
                entry_type=args.type,
                custom_css=theme_css,
                custom_css_path=cfg.custom_css_path,
                template_override=cfg.template_override,
                og_image=args.og_image,
                mermaid=cfg.mermaid,
                favicon=cfg.favicon,
                author=cfg.author,
                site_title=cfg.site_title,
                show_toc=cfg.show_toc,
                skill_template=skill_template,
                skill_assets=skill_assets,
                humanize=cfg.humanize,
            )

        console.print(f"[green]✓[/green] Converted: {result.title}")

        # Anti-slop quality gate
        html_content = result.output_path.read_text(encoding="utf-8")
        checker = AntiSlopChecker()
        violations = checker.check(html_content)
        if violations:
            errors = [v for v in violations if v.severity == "error"]
            warnings = [v for v in violations if v.severity == "warning"]
            for e in errors:
                console.print(f"[red]✗[/red]  {e.category}: {e.details}")
            for w in warnings:
                tag = "[red]✗[/red]" if cfg.strict else "[yellow]⚠[/yellow]"
                console.print(f"{tag}  {w.category}: {w.details}")
            if errors or cfg.strict:
                console.print(
                    f"[red]Build failed: {len(errors)} errors, "
                    f"{len(warnings)}{' (strict)' if not errors else ''}[/red]"
                )
                sys.exit(1)

        # Publish (unless dry-run)
        if not args.dry_run:
            publisher = GitPublisher(
                repo_path=repo_path,
                base_url=base_url,
                content_dir=cfg.output_dir,
                auto_push=cfg.github_auto_push,
                commit_prefix=cfg.github_commit_prefix,
                theme_css=theme_css,
                site_title=args.site_title,
                generate_index=not args.no_index,
                generate_feed=not args.no_feed,
            )
            pub_result = publisher.publish(
                html_path=result.output_path,
                title=result.title,
                fingerprint=result.fingerprint,
                asset_paths=result.assets_copied,
            )

            if pub_result.success:
                console.print(f"[green]✓[/green] {pub_result.message}")
                if pub_result.url:
                    console.print(f"[blue]  →[/blue] {pub_result.url}")
            else:
                console.print(f"[red]✗[/red] {pub_result.message}")

            results.append((input_path, result, pub_result))
        else:
            console.print(f"[dim]Dry-run: Would publish to {result.output_path}[/dim]")
            results.append((input_path, result, None))

    # Eval if requested
    if args.eval and not args.dry_run and results:
        console.print("\n[cyan]Running eval verification...[/cyan]")
        validator = Validator()
        for _, conv_result, pub_result in results:
            if pub_result and pub_result.url:
                verf = validator.verify_url(pub_result.url)
                if verf.success:
                    console.print(f"[green]✓[/green] Verified: {verf.status}")
                else:
                    console.print(f"[red]✗[/red] Verification failed: {verf.error}")

    # Summary table
    if len(results) > 1:
        console.print("\n[bold]Summary:[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("File")
        table.add_column("Title")
        table.add_column("Status")
        table.add_column("URL")

        for input_path, conv_result, pub_result in results:
            status = "[green]✓ Published[/green]" if (pub_result and pub_result.success) else "[red]✗ Failed[/red]"
            url = pub_result.url if (pub_result and pub_result.url) else "-"
            table.add_row(input_path.name, conv_result.title[:30], status, url)

        console.print(table)


def _index_cmd(args):
    """Handle the index subcommand."""
    cfg = load_config(args.config)
    cfg = merge_with_cli_args(cfg, repo_path=args.repo, base_url=args.url)

    output_dir = Path(cfg.github_repo_path) / cfg.output_dir
    if not output_dir.exists():
        console.print(f"[red]Error: output directory {output_dir} not found[/red]")
        sys.exit(1)

    from . import themes
    theme_css = themes.load(cfg.theme) if not cfg.custom_css_path else themes.load("default", custom_path=cfg.custom_css_path)

    console.print(f"[yellow]Generating index + feed in {output_dir}...[/yellow]")
    index_path, feed_path = generate_index_and_feed(
        output_dir=output_dir,
        base_url=args.url or cfg.base_url or "",
        theme_css=theme_css,
        site_title=args.site_title,
    )

    if not args.dry_run:
        publisher = GitPublisher(
            repo_path=Path(cfg.github_repo_path),
            base_url=cfg.base_url or args.url or "",
            content_dir=cfg.output_dir,
            auto_push=cfg.github_auto_push,
            commit_prefix=cfg.github_commit_prefix,
            generate_index=False,
            generate_feed=False,
        )
        add_result = publisher.publish(
            html_path=index_path,
            title="index",
            fingerprint="static",
        )
        if add_result.success:
            console.print(f"[green]✓[/green] Index pushed")
        else:
            console.print(f"[red]✗[/red] {add_result.message}")
    else:
        console.print(f"[dim]Dry-run:[/dim] {index_path} + {feed_path}")


def _watch_cmd(args):
    """Handle the watch subcommand."""
    cfg = load_config(args.config)
    cfg = merge_with_cli_args(
        cfg,
        theme=args.theme,
        custom_css_path=args.custom_css,
        template_override=args.template_override,
        repo_path=args.repo,
        skill=args.skill,
    )

    # Resolve skill template if requested
    skill_template: Optional[str] = None
    skill_assets: Optional[List[Path]] = None
    if cfg.skill:
        from .skills_loader import get_builtin_skills_dir, load_skill
        skill_dir = get_builtin_skills_dir() / cfg.skill
        try:
            skill_data = load_skill(skill_dir)
            skill_template = skill_data["template"]
            skill_assets = skill_data["assets"]
        except FileNotFoundError as exc:
            console.print(f"[red]Error: {exc}[/red]")
            sys.exit(1)

    repo_path = Path(cfg.github_repo_path) if cfg.github_repo_path else Path.cwd()
    watch_dir = Path(args.watch_dir) if args.watch_dir else repo_path
    output_dir = args.output_dir if args.output_dir else (repo_path / cfg.output_dir)

    # Load theme CSS
    from . import themes
    if cfg.custom_css_path:
        theme_css = themes.load("default", custom_path=cfg.custom_css_path)
    else:
        theme_css = themes.load(cfg.theme)

    server = WatchServer(
        watch_dir=watch_dir,
        output_dir=output_dir,
        port=args.port,
        theme=cfg.theme,
        custom_css=theme_css,
        custom_css_path=cfg.custom_css_path,
        template_override=cfg.template_override,
        entry_type=args.type,
        og_image=args.og_image,
        skill_template=skill_template,
        skill_assets=skill_assets,
    )
    server.start()


def _init_cmd(args):
    """Handle the init subcommand."""
    config_path = args.config or Path("agent-publish.toml")
    config_path = config_path.resolve()

    if config_path.exists():
        if sys.stdin.isatty():
            try:
                answer = input("File exists. Overwrite? [y/N] ")
            except (EOFError, KeyboardInterrupt):
                sys.exit(1)
            if answer.strip().lower() != "y":
                console.print("[yellow]Aborted.[/yellow]")
                sys.exit(0)
        else:
            console.print(
                f"[yellow]Warning: {config_path} already exists. "
                "Run with --config to choose a different path.[/yellow]"
            )
            sys.exit(1)

    interactive = sys.stdin.isatty()

    if interactive:
        console.print(
            "[bold cyan]Welcome to agent-publish![/bold cyan] "
            "Let's set up your configuration.\n"
        )
        theme = (
            console.input(
                "Theme (default/minimal/brutalist) [default]: "
            ).strip()
            or "default"
        )
        content_dir = (
            console.input(
                "Content directory relative to repo [sketch]: "
            ).strip()
            or "sketch"
        )
        repo_path = (
            console.input("Repository path [.]: ").strip() or "."
        )
        site_title = (
            console.input(
                "Site title [Published Articles]: "
            ).strip()
            or "Published Articles"
        )
        base_url = console.input("Base URL []: ").strip()

        theme_line = f'theme = "{theme}"'
        content_dir_line = f'content_dir = "{content_dir}"'
        base_url_line = (
            f'base_url = "{base_url}"' if base_url else '# base_url = ""'
        )
        site_title_line = f'site_title = "{site_title}"'
        repo_path_line = f'repo_path = "{repo_path}"'
        msg = f"Configuration written to [bold]{config_path}[/bold]"
    else:
        theme_line = '# theme = "default"'
        content_dir_line = '# content_dir = "sketch"'
        base_url_line = '# base_url = ""'
        site_title_line = '# site_title = "Published Articles"'
        repo_path_line = '# repo_path = "."'
        msg = (
            f"Created configuration template at "
            f"[bold]{config_path}[/bold]"
        )

    content = f"""# agent-publish configuration
# Generated by `agent-publish init`
# Uncomment lines to customize.

[output]
# CSS theme (default, minimal, brutalist)
{theme_line}

# Directory for generated HTML files relative to repo_path
{content_dir_line}

# Base URL for published content (e.g., "https://example.com")
{base_url_line}

# Site title used for index.html and feed.xml
{site_title_line}

# Path to a custom CSS file (relative to config file or absolute)
# custom_css_path = ""

# Path to a custom HTML template file (relative to config file or absolute)
# template_override = ""

# Automatically generate index.html after publishing
# generate_index = true

# Automatically generate feed.xml after publishing
# generate_feed = true

# Path to a favicon file (relative to config file or absolute)
# favicon = ""

[github]
# Path to the target git repository
{repo_path_line}

# Automatically push changes after commit
# auto_push = true

# Commit message prefix
# commit_prefix = "📦"

[validation]
# Verify that published URLs are reachable after publishing
# verify_reachable = true
"""

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(content, encoding="utf-8")
    console.print(f"[green]✓[/green] {msg}")


def main():
    version = _get_version()
    parser = argparse.ArgumentParser(
        description="Markdown-to-HTML pipeline for AI agents",
        prog="agent-publish",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Config file path (TOML or YAML)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ---- publish command ----
    pub_parser = subparsers.add_parser("publish", help="Publish markdown files")
    pub_parser.add_argument(
        "input",
        nargs="+",
        help="Markdown file(s) to publish",
    )
    pub_parser.add_argument(
        "--repo",
        type=Path,
        help="Target repository path",
    )
    pub_parser.add_argument(
        "--type",
        default="daily",
        choices=["daily", "weekly", "note", "research"],
        help="Entry type",
    )
    pub_parser.add_argument(
        "--url",
        help="Base URL for published content",
    )
    pub_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Convert without pushing",
    )
    pub_parser.add_argument(
        "--theme",
        choices=["default", "minimal", "brutalist"],
        help="CSS theme",
    )
    pub_parser.add_argument(
        "--custom-css",
        type=Path,
        dest="custom_css",
        help="Path to custom CSS file",
    )
    pub_parser.add_argument(
        "--theme-design",
        type=Path,
        dest="theme_design",
        help="Path to a DESIGN.md file to generate CSS from",
    )
    pub_parser.add_argument(
        "--template",
        type=Path,
        dest="template_override",
        help="Path to custom HTML template file",
    )
    pub_parser.add_argument(
        "--eval",
        action="store_true",
        help="Run eval verification after publish",
    )
    pub_parser.add_argument(
        "--og-image",
        default=None,
        dest="og_image",
        help="Open Graph image URL for social sharing",
    )
    pub_parser.add_argument(
        "--site-title",
        default="Published Articles",
        help="Site title for index + feed",
    )
    pub_parser.add_argument(
        "--no-index",
        action="store_true",
        help="Skip regenerating index.html",
    )
    pub_parser.add_argument(
        "--no-feed",
        action="store_true",
        help="Skip regenerating feed.xml",
    )
    pub_parser.add_argument(
        "--no-mermaid",
        action="store_true",
        help="Skip Mermaid diagram processing",
    )
    pub_parser.add_argument(
        "--favicon",
        type=Path,
        default=None,
        help="Path to favicon image (copied to output and linked in HTML)",
    )
    pub_parser.add_argument(
        "--author",
        default=None,
        help="Author name for site metadata",
    )
    pub_parser.add_argument(
        "--site_title",
        default=None,
        help="Site title shown in page header",
    )
    pub_parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Disable table of contents sidebar",
    )
    pub_parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail build on anti-slop violations (warnings become errors)",
    )
    pub_parser.add_argument(
        "--direction",
        choices=["editorial", "modern-minimal", "warm-soft", "tech-utility", "brutalist"],
        default=None,
        help="OKLch-generated color palette direction",
    )
    pub_parser.add_argument(
        "--skill",
        default=None,
        help="Skill name to use for template (article, briefing, changelog, deck)",
    )
    pub_parser.add_argument(
        "--humanize",
        action="store_true",
        help="Rewrite markdown through an LLM before conversion (requires AGENT_PUBLISH_API_KEY)",
    )
    pub_parser.set_defaults(func=_publish_cmd)

    # ---- index command ----
    idx_parser = subparsers.add_parser("index", help="Regenerate index.html and feed.xml")
    idx_parser.add_argument(
        "--repo",
        type=Path,
        help="Target repository path",
    )
    idx_parser.add_argument(
        "--url",
        help="Base URL for published content",
    )
    idx_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate without pushing",
    )
    idx_parser.add_argument(
        "--site-title",
        default="Published Articles",
        help="Site title for index + feed",
    )
    idx_parser.set_defaults(func=_index_cmd)

    # ---- watch command ----
    watch_parser = subparsers.add_parser("watch", help="Watch markdown files and serve on localhost")
    watch_parser.add_argument(
        "--watch-dir",
        type=Path,
        default=None,
        help="Directory to watch for .md changes (default: current dir)",
    )
    watch_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for generated HTML (default: <repo>/sketch)",
    )
    watch_parser.add_argument(
        "--repo",
        type=Path,
        help="Target repository path",
    )
    watch_parser.add_argument(
        "--type",
        default="daily",
        choices=["daily", "weekly", "note", "research"],
        help="Entry type",
    )
    watch_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for dev server",
    )
    watch_parser.add_argument(
        "--theme",
        choices=["default", "minimal", "brutalist"],
        help="CSS theme",
    )
    watch_parser.add_argument(
        "--custom-css",
        type=Path,
        dest="custom_css",
        help="Path to custom CSS file",
    )
    watch_parser.add_argument(
        "--template",
        type=Path,
        dest="template_override",
        help="Path to custom HTML template file",
    )
    watch_parser.add_argument(
        "--og-image",
        default=None,
        dest="og_image",
        help="Open Graph image URL for social sharing",
    )
    watch_parser.add_argument(
        "--skill",
        default=None,
        help="Skill name to use for template (article, briefing, changelog, deck)",
    )
    watch_parser.set_defaults(func=_watch_cmd)

    # ---- init command ----
    init_parser = subparsers.add_parser("init", help="Create a default configuration file")
    init_parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Config file path (default: agent-publish.toml)",
    )
    init_parser.set_defaults(func=_init_cmd)

    args = parser.parse_args()

    if not args.command:
        # No subcommand given - check if first positional arg looks like an md file
        # For backward compat, just default to publish
        print("Usage: agent-publish publish <file.md> [options]")
        print("       agent-publish index [options]")
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
