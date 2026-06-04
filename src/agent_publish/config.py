"""Config loader for agent-publish.

Supports TOML and YAML config files with CLI override fallback.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Typed configuration for agent-publish."""

    output_dir: str = "sketch"
    theme: str = "default"
    custom_css_path: Optional[Path] = None
    theme_design_path: Optional[Path] = None
    template_override: Optional[Path] = None
    base_url: str = ""
    github_repo_path: str = "."
    github_auto_push: bool = True
    github_commit_prefix: str = "📦"
    site_title: str = "Published Articles"
    validation_verify_reachable: bool = True
    generate_index: bool = True
    generate_feed: bool = True
    mermaid: bool = True
    favicon: Optional[Path] = None
    author: str = ""


def _find_config_file() -> Optional[Path]:
    """Find config file in current directory or home directory.

    Checks for both TOML and YAML variants.
    """
    cwd = Path.cwd()
    for name in ("agent-publish.yaml", "agent-publish.yml", "agent-publish.toml"):
        candidate = cwd / name
        if candidate.exists():
            return candidate

    config_dir = Path.home() / ".config" / "agent-publish"
    for name in ("config.yaml", "config.yml", "config.toml"):
        candidate = config_dir / name
        if candidate.exists():
            return candidate

    return None


def _load_raw(path: Path) -> dict:
    """Load raw config dict from a TOML or YAML file."""
    suffix = path.suffix.lower()
    if suffix == ".toml":
        import toml
        return toml.load(path)
    if suffix in (".yaml", ".yml"):
        import yaml
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    raise ValueError(f"Unsupported config format: {suffix}")


def load_config(path: Optional[Path] = None) -> Config:
    """Load configuration from file.

    Args:
        path: Explicit config file path. If None, searches default locations.

    Returns:
        Config instance with validated fields.
    """
    config_path = path or _find_config_file()
    raw: dict = {}
    if config_path and config_path.exists():
        raw = _load_raw(config_path)

    output = raw.get("output", {})
    github = raw.get("github", {})
    validation = raw.get("validation", {})

    cfg_dir = config_path.parent if config_path else None

    cfg = Config(
        output_dir=output.get("content_dir", "sketch"),
        theme=output.get("theme", "default"),
        custom_css_path=_resolve_path(output.get("custom_css_path"), cfg_dir),
        theme_design_path=_resolve_path(output.get("theme_design_path"), cfg_dir),
        template_override=_resolve_path(output.get("template_override"), cfg_dir),
        base_url=output.get("base_url", ""),
        github_repo_path=github.get("repo_path", "."),
        github_auto_push=github.get("auto_push", True),
        github_commit_prefix=github.get("commit_prefix", "📦"),
        site_title=output.get("site_title", "Published Articles"),
        validation_verify_reachable=validation.get("verify_reachable", True),
        generate_index=output.get("generate_index", True),
        generate_feed=output.get("generate_feed", True),
        mermaid=output.get("mermaid", True),
        favicon=_resolve_path(output.get("favicon"), cfg_dir),
        author=output.get("author", ""),
    )

    if cfg.favicon is not None and not cfg.favicon.exists():
        raise FileNotFoundError(f"favicon not found: {cfg.favicon}")
    if cfg.theme_design_path is not None and not cfg.theme_design_path.exists():
        raise FileNotFoundError(f"theme_design_path not found: {cfg.theme_design_path}")
    if cfg.custom_css_path is not None and not cfg.custom_css_path.exists():
        raise FileNotFoundError(f"custom_css_path not found: {cfg.custom_css_path}")
    if cfg.template_override is not None and not cfg.template_override.exists():
        raise FileNotFoundError(f"template_override not found: {cfg.template_override}")

    return cfg


def _resolve_path(value: Optional[str], base_dir: Optional[Path] = None) -> Optional[Path]:
    """Resolve a config path, expanding user home and making absolute.

    If base_dir is provided and the path is relative, resolve it relative
    to base_dir instead of the current working directory.
    """
    if not value:
        return None
    p = Path(value).expanduser()
    if not p.is_absolute() and base_dir:
        p = base_dir / p
    return p.resolve()


def merge_with_cli_args(cfg: Config, **cli_args) -> Config:
    """Merge a Config with CLI arguments (CLI wins).

    Pass CLI values as keyword args; None or missing values are ignored.
    """
    kwargs = {}
    field_map = {
        "theme": "theme",
        "custom_css_path": "custom_css_path",
        "theme_design_path": "theme_design_path",
        "template_override": "template_override",
        "base_url": "base_url",
        "repo_path": "github_repo_path",
        "auto_push": "github_auto_push",
        "commit_prefix": "github_commit_prefix",
        "site_title": "site_title",
        "generate_index": "generate_index",
        "generate_feed": "generate_feed",
        "mermaid": "mermaid",
        "favicon": "favicon",
        "author": "author",
    }
    for cli_key, cfg_key in field_map.items():
        val = cli_args.get(cli_key)
        if val is not None:
            kwargs[cfg_key] = val

    if kwargs:
        # Validate any newly supplied paths
        if "custom_css_path" in kwargs:
            p = Path(kwargs["custom_css_path"]).expanduser().resolve()
            if not p.exists():
                raise FileNotFoundError(f"custom_css_path not found: {p}")
            kwargs["custom_css_path"] = p
        if "theme_design_path" in kwargs:
            p = Path(kwargs["theme_design_path"]).expanduser().resolve()
            if not p.exists():
                raise FileNotFoundError(f"theme_design_path not found: {p}")
            kwargs["theme_design_path"] = p
        if "template_override" in kwargs:
            p = Path(kwargs["template_override"]).expanduser().resolve()
            if not p.exists():
                raise FileNotFoundError(f"template_override not found: {p}")
            kwargs["template_override"] = p
        if "favicon" in kwargs:
            p = Path(kwargs["favicon"]).expanduser().resolve()
            if not p.exists():
                raise FileNotFoundError(f"favicon not found: {p}")
            kwargs["favicon"] = p
        return cfg.__class__(**{**cfg.__dict__, **kwargs})

    return cfg
