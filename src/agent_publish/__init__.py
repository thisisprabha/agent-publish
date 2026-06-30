"""agent-publish: Markdown-to-HTML pipeline for AI agents.

Stable public API for embedding in agent pipelines, cron jobs, and hooks.
"""

__version__ = "0.1.0"

import tempfile
from pathlib import Path
from typing import Any, List, Optional

from .assets import copy_assets
from .config import Config, load_config
from .converter import ConversionResult, convert_file
from .publisher import GitPublisher, PublishResult
from .publisher import publish as _publish_file


def convert(
    markdown: str,
    *,
    theme: str = "default",
    skill: Optional[str] = None,
    output_dir: Optional[Path] = None,
    entry_type: str = "daily",
    site_title: Optional[str] = None,
    author: Optional[str] = None,
    show_toc: bool = True,
    mermaid: bool = True,
    humanize: bool = False,
    tldr: bool = False,
    tags: bool = False,
    smart_typography: bool = False,
) -> ConversionResult:
    """Convert a markdown string to a complete HTML page.

    Returns a ``ConversionResult`` with ``.html``, ``.title``,
    ``.output_path``, ``.reading_time``, and other metadata.

    Args:
        markdown: Markdown source string
        theme: CSS theme name (default, minimal, brutalist) or "editorial"
        skill: Skill name for template (article, briefing, changelog, deck)
        output_dir: Where to write the HTML file (uses temp dir if None)
        entry_type: Category label (daily, weekly, note, research)
        site_title: Site name shown in page header
        author: Author string for <meta> tag
        show_toc: Insert table of contents when 2+ headings exist
        mermaid: Enable Mermaid diagram rendering
        humanize: Rewrite markdown via LLM before conversion (needs API key)
        tldr: Inject auto-generated TL;DR summary
        tags: Inject topic tag badges
        smart_typography: Apply curly quotes, em-dashes, ellipsis
    """
    from .themes import load as load_theme

    tmpdir = output_dir or Path(tempfile.mkdtemp())
    tmpdir.mkdir(parents=True, exist_ok=True)

    md_path = tmpdir / "_input.md"
    md_path.write_text(markdown, encoding="utf-8")

    css = load_theme(theme)

    skill_template = None
    skill_assets = None
    if skill:
        from .skills_loader import get_builtin_skills_dir, load_skill

        skill_dir = get_builtin_skills_dir() / skill
        data = load_skill(skill_dir)
        skill_template = data["template"]
        skill_assets = data["assets"]

    return convert_file(
        input_path=md_path,
        output_dir=tmpdir,
        entry_type=entry_type,
        custom_css=css,
        show_toc=show_toc,
        mermaid=mermaid,
        author=author,
        site_title=site_title,
        skill_template=skill_template,
        skill_assets=skill_assets,
        humanize=humanize,
        tldr=tldr,
        tags=tags,
        smart_typography=smart_typography,
    )


def publish(
    html_path: Path,
    *,
    title: str,
    fingerprint: str,
    config: Optional[Config] = None,
    repo_path: Optional[Path] = None,
    base_url: Optional[str] = None,
    content_dir: str = "sketch",
    auto_push: bool = True,
    commit_prefix: str = "📦",
    asset_paths: Optional[List[Path]] = None,
    theme_css: Optional[str] = None,
    site_title: str = "Published Articles",
    generate_index: bool = True,
    generate_feed: bool = True,
    **kwargs: Any,
) -> PublishResult:
    """Publish an HTML file to GitHub Pages.

    Accepts either a ``Config`` object or individual keyword arguments.
    CLI arguments or ``Config`` values take precedence over defaults.

    Args:
        html_path: Path to the generated HTML file
        title: Content title for the commit message
        fingerprint: Content fingerprint for dedup (use ``ConversionResult.fingerprint``)
        config: Optional ``Config`` instance (load with ``load_config()``)
        repo_path: Local git repository path
        base_url: Base URL of the published site
        content_dir: Subdirectory for generated content inside the repo
        auto_push: Automatically git push after commit
        commit_prefix: Emoji/prefix for commit messages
        asset_paths: Extra files to copy alongside the HTML
        theme_css: CSS string for index page generation
        site_title: Site title for index and feed
        generate_index: Whether to regenerate index.html after publish
        generate_feed: Whether to regenerate feed.xml after publish
        **kwargs: Additional ``GitPublisher`` keyword arguments

    Returns:
        ``PublishResult`` with ``.success``, ``.url``, and ``.message``
    """
    if config:
        repo_path = repo_path or Path(config.github_repo_path)
        base_url = base_url or config.base_url
        content_dir = content_dir or config.output_dir
        auto_push = config.github_auto_push
        commit_prefix = config.github_commit_prefix
        site_title = config.site_title
        generate_index = config.generate_index
        generate_feed = config.generate_feed

    if not base_url:
        raise ValueError("base_url is required — pass it directly or set in config")

    publisher = GitPublisher(
        repo_path=repo_path or Path("."),
        base_url=base_url,
        content_dir=content_dir,
        auto_push=auto_push,
        commit_prefix=commit_prefix,
        theme_css=theme_css,
        site_title=site_title,
        generate_index=generate_index,
        generate_feed=generate_feed,
    )

    return publisher.publish(
        html_path=html_path,
        title=title,
        fingerprint=fingerprint,
        asset_paths=asset_paths,
    )


__all__ = [
    "convert",
    "copy_assets",
    "convert_file",
    "ConversionResult",
    "publish",
    "PublishResult",
    "Config",
    "load_config",
    "GitPublisher",
    "_publish_file",
]
