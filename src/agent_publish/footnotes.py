"""Footnote detection and HTML rendering for agent-publish."""

import re
from typing import Dict, List, Tuple

_FN_DEF_RE = re.compile(
    r'^\[\^([^\]]+)\]:[ \t]*(.*?)(?=\n\n\[\^|\n\n[^\s]|\Z)',
    re.MULTILINE | re.DOTALL,
)

_FN_REF_RE = re.compile(r'\[\^([^\]]+)\]')


def extract_footnote_defs(md_content: str) -> Tuple[str, Dict[str, str]]:
    """Extract footnote definitions from markdown and remove them.

    Handles multi-line footnotes with indented continuation lines.

    Args:
        md_content: Raw markdown content.

    Returns:
        Tuple of (cleaned_markdown_without_defs, {label: html_content}).
    """
    definitions: Dict[str, str] = {}

    def _extract(m):
        label = m.group(1).strip()
        content = m.group(2).strip()
        # Collapse indented continuation lines into a single paragraph
        content = re.sub(r'\n[ \t]+', ' ', content)
        if label and label not in definitions:
            definitions[label] = content
        return ''

    cleaned = _FN_DEF_RE.sub(_extract, md_content)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned, definitions


def process_footnotes(md_content: str, html_body: str) -> str:
    """Post-process HTML to render markdown footnotes.

    Finds footnote definitions in raw markdown and replaces [^label]
    references in the HTML body with superscript anchor links. Appends
    a numbered footnotes section with back-links at the end.

    Args:
        md_content: Original raw markdown (used to find definitions).
        html_body: HTML body string after markdown conversion.

    Returns:
        HTML body with footnote refs rendered and footnotes section.
    """
    definitions: Dict[str, str] = {}
    for m in _FN_DEF_RE.finditer(md_content):
        label = m.group(1).strip()
        content = m.group(2).strip()
        content = re.sub(r'\n[ \t]+', ' ', content)
        if label and label not in definitions:
            definitions[label] = content

    if not definitions:
        return html_body

    # Determine reference order from appearance in markdown source
    ref_labels: List[str] = []
    seen: set = set()
    for m in _FN_REF_RE.finditer(md_content):
        label = m.group(1)
        if label in definitions and label not in seen:
            seen.add(label)
            ref_labels.append(label)

    # Append any defined-but-not-referenced footnotes
    for label in definitions:
        if label not in seen:
            ref_labels.append(label)

    fn_map = {label: i + 1 for i, label in enumerate(ref_labels)}

    # Replace [^label] refs in HTML with superscript links
    def _replace_ref(m):
        label = m.group(1)
        num = fn_map.get(label)
        if num is None:
            return m.group(0)
        return (
            f'<sup><a href="#fn-{num}" id="fnref-{num}"'
            f' class="footnote-ref">[{num}]</a></sup>'
        )

    html_body = _FN_REF_RE.sub(_replace_ref, html_body)

    # Build footnotes section
    items = []
    for label in ref_labels:
        num = fn_map[label]
        content = definitions[label]
        items.append(
            f'<li id="fn-{num}" class="footnote-item">'
            f'<p>{content} '
            f'<a href="#fnref-{num}" class="footnote-backref"'
            f' aria-label="Back to reference {num}">\u21a9</a></p>'
            f'</li>'
        )

    fn_section = (
        '\n<hr class="footnotes-sep">\n'
        '<section class="footnotes">\n'
        '<ol class="footnotes-list">\n'
        + '\n'.join(items) +
        '\n</ol>\n'
        '</section>\n'
    )

    return html_body.rstrip() + '\n' + fn_section
