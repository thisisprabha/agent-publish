"""Asset copying and path rewriting for generated HTML."""

import re
import shutil
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

_IMG_SRC_RE = re.compile(r'<img(\s+[^>]*?)src="([^"]+)"([^>]*)>', re.IGNORECASE)
_REMOTE_RE = re.compile(r'^https?://', re.IGNORECASE)


def _is_remote_url(src: str) -> bool:
    return bool(_REMOTE_RE.match(src))


def copy_assets(
    html: str,
    base_dir: Path,
    output_dir: Path,
    images_subdir: str = "images",
) -> Tuple[str, List[Path]]:
    """Find local image references in HTML, copy them to output_dir, and rewrite src.

    Args:
        html: Generated HTML content.
        base_dir: Directory of the source markdown file (for resolving relative paths).
        output_dir: Destination directory for generated HTML.
        images_subdir: Name of subdirectory within output_dir to place images.

    Returns:
        Tuple of (updated HTML string, list of copied asset Paths)
    """
    assets_copied: List[Path] = []
    src_map: Dict[str, str] = {}

    images_dir = output_dir / images_subdir
    images_dir.mkdir(parents=True, exist_ok=True)

    for match in _IMG_SRC_RE.finditer(html):
        src = match.group(2)
        if _is_remote_url(src):
            continue

        src_path = Path(src)
        if src_path.is_absolute():
            if not src_path.exists():
                warnings.warn(f"Absolute image path does not exist: {src}")
            continue

        resolved = (base_dir / src).resolve()
        if not resolved.exists():
            warnings.warn(f"Relative image path not found: {src}")
            continue

        dest = images_dir / resolved.name
        shutil.copy2(resolved, dest)
        assets_copied.append(dest)
        src_map[src] = f"{images_subdir}/{resolved.name}"

    if not src_map:
        return html, assets_copied

    def replacer(m):
        prefix = m.group(1)
        old_src = m.group(2)
        suffix = m.group(3)
        new_src = src_map.get(old_src, old_src)
        return f'<img{prefix}src="{new_src}"{suffix}>'

    updated_html = _IMG_SRC_RE.sub(replacer, html)
    return updated_html, assets_copied
