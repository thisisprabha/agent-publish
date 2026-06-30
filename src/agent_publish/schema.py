"""Frontmatter schema validation for agent-publish.

Supports user-provided .agent_publish_schema.yaml for extensible validation.
"""

import re
from datetime import date as date_type
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_SCHEMA: Dict[str, Dict[str, Any]] = {
    "title": {"type": "str", "required": False},
    "date": {"type": "str", "required": False},
    "author": {"type": "str", "default": ""},
    "type": {
        "type": "str",
        "one_of": ["daily", "weekly", "note", "research"],
        "default": "daily",
    },
    "tags": {"type": "list", "default": []},
    "draft": {"type": "bool", "default": False},
    "description": {"type": "str", "default": ""},
    "slug": {"type": "str", "default": ""},
}

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_frontmatter(md_content: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Extract YAML frontmatter from markdown content.

    Returns (frontmatter_dict, content_without_frontmatter).
    Returns (None, original_content) if no frontmatter found.
    """
    m = _FRONTMATTER_RE.match(md_content)
    if not m:
        return None, md_content

    try:
        import yaml

        fm = yaml.safe_load(m.group(1))
        if not isinstance(fm, dict):
            return None, md_content
        return fm, md_content[m.end() :]
    except Exception:
        return None, md_content


def _find_schema_file(repo_root: Path) -> Optional[Path]:
    candidate = repo_root / ".agent_publish_schema.yaml"
    if candidate.exists():
        return candidate
    return None


def load_user_schema(repo_root: Path) -> Optional[Dict[str, Dict[str, Any]]]:
    schema_path = _find_schema_file(repo_root)
    if not schema_path:
        return None

    try:
        import yaml

        with open(schema_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        fields = raw.get("fields", {})
        if not isinstance(fields, dict):
            return None
        return fields
    except Exception:
        return None


def merge_schemas(
    base: Dict[str, Dict[str, Any]], user: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    merged = dict(base)
    for key, spec in user.items():
        if key in merged:
            merged[key] = {**merged[key], **spec}
        else:
            merged[key] = spec
    return merged


def validate_frontmatter(
    frontmatter: Dict[str, Any],
    schema: Dict[str, Dict[str, Any]],
) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []

    for field_name, spec in schema.items():
        if spec.get("required") and field_name not in frontmatter:
            errors.append(
                {
                    "field": field_name,
                    "error": f"Required field '{field_name}' is missing",
                    "severity": "error",
                }
            )
            continue

        value = frontmatter.get(field_name)
        if value is None:
            continue

        field_type = spec.get("type", "str")

        if field_type == "str" and not isinstance(value, str):
            errors.append(
                {
                    "field": field_name,
                    "error": f"'{field_name}' must be a string, got {type(value).__name__}",
                    "severity": "error",
                }
            )
        elif field_type == "int" and not isinstance(value, int):
            errors.append(
                {
                    "field": field_name,
                    "error": f"'{field_name}' must be an integer, got {type(value).__name__}",
                    "severity": "error",
                }
            )
        elif field_type == "bool" and not isinstance(value, bool):
            errors.append(
                {
                    "field": field_name,
                    "error": f"'{field_name}' must be a boolean, got {type(value).__name__}",
                    "severity": "error",
                }
            )
        elif field_type == "list" and not isinstance(value, list):
            errors.append(
                {
                    "field": field_name,
                    "error": f"'{field_name}' must be a list, got {type(value).__name__}",
                    "severity": "error",
                }
            )
        elif field_type == "date":
            if isinstance(value, str):
                try:
                    date_type.fromisoformat(value)
                except ValueError:
                    errors.append(
                        {
                            "field": field_name,
                            "error": f"'{field_name}' must be a valid date (YYYY-MM-DD), got '{value}'",
                            "severity": "error",
                        }
                    )
            elif not isinstance(value, date_type):
                errors.append(
                    {
                        "field": field_name,
                        "error": f"'{field_name}' must be a date string, got {type(value).__name__}",
                        "severity": "error",
                    }
                )

        one_of = spec.get("one_of")
        if one_of and value not in one_of:
            errors.append(
                {
                    "field": field_name,
                    "error": f"'{field_name}' must be one of {one_of}, got '{value}'",
                    "severity": "warning",
                }
            )

    return errors


def apply_defaults(
    frontmatter: Dict[str, Any],
    schema: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    result = dict(frontmatter)
    for field_name, spec in schema.items():
        if field_name not in result and "default" in spec:
            result[field_name] = spec["default"]
    return result
