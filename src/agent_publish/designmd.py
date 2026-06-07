"""DESIGN.md parser -- reads structured Markdown theme spec and generates CSS.

Schema: YAML front-matter with typed token groups (colors, typography, spacing, rounded).
Markdown body holds the nine canonical sections for human readability.

A DESIGN.md can sit beside an optional base.css file.  The generated output is:
  1. CSS custom properties from tokens
  2. (optional) base.css content
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class DesignTokens:
    """Parsed token groups from a DESIGN.md YAML front-matter."""

    colors: dict[str, Any] = field(default_factory=dict)
    typography: dict[str, Any] = field(default_factory=dict)
    spacing: dict[str, Any] = field(default_factory=dict)
    rounded: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDesign:
    """Result of parsing a single DESIGN.md file."""

    name: str = ""
    version: str = ""
    tokens: DesignTokens = field(default_factory=DesignTokens)
    base_css: str = ""
    sections: dict[str, str] = field(default_factory=dict)  # human-readable sections


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_design(design_path: Path) -> ParsedDesign:
    """Parse a DESIGN.md file and optionally pull in a sibling base.css.

    Args:
        design_path: Path to a DESIGN.md file.

    Returns:
        Parsed design with generated CSS custom properties + optional base CSS.
    """
    raw_text = design_path.read_text(encoding="utf-8")
    fm, body = _split_front_matter(raw_text)
    tokens = _parse_yaml_tokens(fm) if fm else DesignTokens()
    sections = _parse_sections(body)

    base_css = ""
    base_css_path = design_path.with_name("base.css")
    if base_css_path.exists():
        base_css = base_css_path.read_text(encoding="utf-8")

    return ParsedDesign(
        name=fm.get("name", ""),
        version=str(fm.get("version", "")),
        tokens=tokens,
        base_css=base_css,
        sections=sections,
    )


def generate_css(parsed: ParsedDesign, *, include_base: bool = True) -> str:
    """Generate a single CSS string from a parsed DESIGN.md.

    Args:
        parsed: ParsedDesign instance returned by load_design().
        include_base: Whether to append the optional sibling base.css.

    Returns:
        CSS text containing :root custom properties + base styles.
    """
    var_lines: list[str] = [":root{"]
    token_map = _flatten_tokens(parsed.tokens)
    resolved = _resolve_aliases(token_map)

    for key, value in sorted(resolved.items()):
        var_lines.append(f"  {key}:{value};")

    var_lines.append("}")
    css = "\n".join(var_lines)

    if include_base and parsed.base_css:
        css = css + "\n\n" + parsed.base_css

    return css


# ---------------------------------------------------------------------------
# Low-level parsing helpers
# ---------------------------------------------------------------------------

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split raw file into YAML front-matter dict and Markdown body.

    If no front-matter is present, returns ({}, text).
    """
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text

    import yaml
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    body = m.group(2)
    return fm, body


def _parse_yaml_tokens(fm: dict[str, Any]) -> DesignTokens:
    """Extract recognized token groups from YAML front-matter."""
    return DesignTokens(
        colors=_copy_dict(fm.get("colors", {})),
        typography=_copy_dict(fm.get("typography", {})),
        spacing=_copy_dict(fm.get("spacing", {})),
        rounded=_copy_dict(fm.get("rounded", {})),
    )


def _copy_dict(obj: Any) -> dict[str, Any]:
    """Coerce to a shallow dict copy."""
    if isinstance(obj, dict):
        return dict(obj)
    return {}


# ---------------------------------------------------------------------------
# Token flattening + alias resolution
# ---------------------------------------------------------------------------

_PREFIX_MAP = {
    "colors": "color",
    "typography": "",
    "spacing": "spacing",
    "rounded": "radius",
}

_TYPE_KEYS = {"colors", "typography", "spacing", "rounded"}


def _flatten_tokens(tokens: DesignTokens, *, _prefix: str = "") -> dict[str, str]:
    """Flatten nested token dicts into flat `--kebab-case` keys with CSS values."""
    result: dict[str, str] = {}
    source: dict[str, Any] = {
        "colors": tokens.colors,
        "typography": tokens.typography,
        "spacing": tokens.spacing,
        "rounded": tokens.rounded,
    }

    for group_name, group in source.items():
        css_prefix = _PREFIX_MAP.get(group_name, group_name)
        _walk_flat(group, css_prefix, result)

    return result


def _walk_flat(obj: Any, prefix: str, out: dict[str, str]) -> None:
    """Recursively walk a token group; leaf values become CSS strings."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            sep = "-" if prefix else ""
            _walk_flat(v, f"{prefix}{sep}{k}", out)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj, start=1):
            sep = "-" if prefix else ""
            _walk_flat(item, f"{prefix}{sep}{idx}", out)
    else:
        # Leaf value
        var_name = f"--{prefix.replace('.', '-')}"
        out[var_name] = _css_value(obj)


def _css_value(obj: Any) -> str:
    """Coerce a leaf token value into a CSS-safe string."""
    if obj is None:
        return ""
    if isinstance(obj, (int, float)):
        # Assume px for spacing/fontSize, unitless for lineHeight
        return str(obj)
    if isinstance(obj, str):
        return obj
    return str(obj)


_ALIAS_RE = re.compile(r"\{([a-zA-Z0-9_.-]+)\}")


def _resolve_aliases(tokens: dict[str, str]) -> dict[str, str]:
    """Resolve `{path.to.token}` references recursively.

    Converts dot-paths into the same flattened kebab notation used for
    CSS variable names, e.g. `{colors.primary}` -> `#1a3a52`.
    """
    resolved: dict[str, str] = dict(tokens)
    max_passes = 10

    for _ in range(max_passes):
        changed = False
        for key, value in resolved.items():
            def _sub(m: re.Match[str]) -> str:
                path: str = m.group(1)
                css_key = f"--{path.replace('.', '-')}"
                return resolved.get(css_key, m.group(0))

            new_value = _ALIAS_RE.sub(_sub, value)
            if new_value != value:
                resolved[key] = new_value
                changed = True

        if not changed:
            break

    return resolved


# ---------------------------------------------------------------------------
# Section extraction (human-readable nine-section body)
# ---------------------------------------------------------------------------

_SECTION_HEADER_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def _parse_sections(body: str) -> dict[str, str]:
    """Extract H2 sections from the Markdown body.

    Returns a dict mapping lower-cased header name -> body text.
    Primarily for human readability / debugging; not consumed by the CSS
    generator in this version.
    """
    sections: dict[str, str] = {}
    headers = list(_SECTION_HEADER_RE.finditer(body))
    if not headers:
        return sections

    for i, m in enumerate(headers):
        title = m.group(1).strip()
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        text = body[start:end].strip()
        sections[title.lower()] = text

    return sections
