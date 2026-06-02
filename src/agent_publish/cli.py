"""CLI for agent-publish."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .config import load_config, merge_with_cli_args
from .converter import convert_file
from .publisher import GitPublisher
from .validator import Validator

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Markdown-to-HTML pipeline for AI agents",
        prog="agent-publish",
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="Markdown file(s) to publish",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        help="Target repository path",
    )
    parser.add_argument(
        "--type",
        default="daily",
        choices=["daily", "weekly", "note", "research"],
        help="Entry type",
    )
    parser.add_argument(
        "--url",
        help="Base URL for published content",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Convert without pushing",
    )
    parser.add_argument(
        "--theme",
        choices=["default", "minimal", "brutalist"],
        help="CSS theme",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Config file path (TOML or YAML)",
    )
    parser.add_argument(
        "--custom-css",
        type=Path,
        dest="custom_css_path",
        help="Path to custom CSS file",
    )
    parser.add_argument(
        "--template",
        type=Path,
        dest="template_override",
        help="Path to custom HTML template file",
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Run eval verification after publish",
    )
    
    args = parser.parse_args()
    
    # Load config
    cfg = load_config(args.config)
    cfg = merge_with_cli_args(
        cfg,
        theme=args.theme,
        custom_css_path=args.custom_css_path,
        template_override=args.template_override,
        base_url=args.url,
        repo_path=args.repo,
    )
    
    repo_path = Path(cfg.github_repo_path)
    base_url = cfg.base_url
    
    if not base_url and not args.dry_run:
        console.print("[red]Error: --url or output.base_url in config required[/red]")
        sys.exit(1)
    
    # Load theme CSS unless custom_css_path is provided
    from . import themes
    if cfg.custom_css_path:
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
            )
        
        console.print(f"[green]✓[/green] Converted: {result.title}")
        
        # Publish (unless dry-run)
        if not args.dry_run:
            publisher = GitPublisher(
                repo_path=repo_path,
                base_url=base_url,
                content_dir=cfg.output_dir,
                auto_push=cfg.github_auto_push,
                commit_prefix=cfg.github_commit_prefix,
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


if __name__ == "__main__":
    main()
