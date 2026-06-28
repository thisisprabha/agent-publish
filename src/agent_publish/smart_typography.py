"""Smart typography post-processing for HTML body text.

Applies typographic replacements on prose text, skipping code/pre blocks:
- ``--`` → em-dash (—)
- ``...`` → ellipsis (…)
- Straight double quotes → curly double quotes (" " → \u201c \u201d)
- Straight single quotes → curly single quotes (' ' → \u2018 \u2019)
  (preserves apostrophes: don't → don\u2019t)
"""

import re

_BLOCK_RE = re.compile(
    r'(<(?:pre|code|script|style)\b[^>]*>.*?</\1>)',
    re.DOTALL | re.IGNORECASE,
)

_TAG_SPLIT_RE = re.compile(r'(<[^>]+>)')


def _process_text(text: str) -> str:
    """Apply smart typography to a plain-text chunk (no HTML tags)."""
    text = text.replace('...', '\u2026')
    text = text.replace('--', '\u2014')
    text = _smart_dbl_quotes(text)
    text = _smart_sgl_quotes(text)
    return text


def _smart_dbl_quotes(text: str) -> str:
    """Convert straight double quotes to curly double quotes.

    Alternates opening/closing, resetting at sentence boundaries.
    """
    result = []
    dq_open = True
    for ch in text:
        if ch == '"':
            if dq_open:
                result.append('\u201c')
            else:
                result.append('\u201d')
            dq_open = not dq_open
        else:
            if ch in '.!?':
                dq_open = True
            result.append(ch)
    return ''.join(result)


def _smart_sgl_quotes(text: str) -> str:
    """Convert straight single quotes to curly single quotes.

    Preserves apostrophes/contractions (between or after letters) as
    right single quotes. Alternates opening/closing for quotes,
    resetting at sentence boundaries.
    """
    result = []
    sq_state = 'open'
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "'":
            prev_is_alpha = i > 0 and text[i - 1].isalpha()
            next_is_alpha = i < len(text) - 1 and text[i + 1].isalpha()

            if prev_is_alpha and next_is_alpha:
                result.append('\u2019')
            elif prev_is_alpha:
                result.append('\u2019')
            elif sq_state == 'open':
                result.append('\u2018')
                sq_state = 'close'
            else:
                result.append('\u2019')
                sq_state = 'open'
        else:
            if ch in '.!?':
                sq_state = 'open'
            result.append(ch)
        i += 1
    return ''.join(result)


def apply_smart_typography(html_body: str) -> str:
    """Apply smart typography replacements to HTML body text.

    Skips <pre>, <code>, <script>, and <style> blocks so that code
    and diagram content is never modified.

    Args:
        html_body: HTML body content string.

    Returns:
        HTML body with smart typography applied to prose text.
    """
    blocks: dict[str, str] = {}
    counter = [0]

    def _save_block(m: re.Match) -> str:
        key = f'__STBLK_{counter[0]}__'
        blocks[key] = m.group(0)
        counter[0] += 1
        return key

    result = _BLOCK_RE.sub(_save_block, html_body)

    parts = _TAG_SPLIT_RE.split(result)
    out = []
    for part in parts:
        if part.startswith('<'):
            out.append(part)
        else:
            out.append(_process_text(part))

    result = ''.join(out)

    for key, block in reversed(blocks.items()):
        result = result.replace(key, block)

    return result
