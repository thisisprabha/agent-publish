"""Auto TL;DR -- generate a summary and inject as a styled callout.

When `--tldr` is passed, this module:
  1. Attempts an LLM-based 2-3 sentence summary (requires API key).
  2. Falls back to extracting the first substantial paragraph (zero-token).

The summary is injected at the top of the HTML body as a `<div class="tldr-callout">`.
"""

import os
import re
from typing import Optional


_DEFAULT_PROMPT = """Summarize the following article in exactly 2-3 clear sentences.
Preserve the key insight. Do not add preamble. Return only the summary.

{content}
"""


def _get_api_config():
    key = os.environ.get("AGENT_PUBLISH_API_KEY", "")
    base = os.environ.get("AGENT_PUBLISH_API_BASE", "https://api.openai.com/v1")
    model = os.environ.get("AGENT_PUBLISH_MODEL", "gpt-4o-mini")
    return key, base, model


def extract_first_paragraph(md_content: str) -> str:
    """Extract the first substantial paragraph from markdown as zero-token fallback."""
    # Strip code blocks
    text = re.sub(r'```[\s\S]*?```', '', md_content)
    # Strip inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Strip headings
    text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)
    # Strip blockquotes (but keep the text inside)
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    # Strip horizontal rules
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
    # Strip images FIRST (before links, since links pattern would corrupt image markdown)
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    # Strip links -- keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Split into paragraphs (blank-line separated)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    for p in paragraphs:
        # Skip short/fragment paragraphs
        if len(p.split()) >= 5:
            # Flatten newlines into spaces
            return ' '.join(p.split())
    # Absolute fallback: first non-empty paragraph, even if short
    for p in paragraphs:
        return ' '.join(p.split())
    return ""


def generate_tldr(
    md_content: str,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    prompt_template: Optional[str] = None,
) -> str:
    """Generate a TL;DR summary.

    Tries LLM first (if API key available), falls back to first paragraph.

    Args:
        md_content: Original markdown string.
        api_key: Explicit API key (overrides env).
        api_base: Explicit API base URL (overrides env).
        model: Explicit model name (overrides env).
        prompt_template: Custom prompt template with {content} placeholder.

    Returns:
        Summary string (2-3 sentences) or first paragraph fallback.
    """
    env_key, env_base, env_model = _get_api_config()
    key = api_key or env_key
    base_url = api_base or env_base
    model_name = model or env_model

    fallback = extract_first_paragraph(md_content)

    if not key:
        return fallback

    prompt = (prompt_template or _DEFAULT_PROMPT).format(content=md_content)

    try:
        import urllib.request
        import json

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }

        payload = json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": 512,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=payload,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            summary = data["choices"][0]["message"]["content"]

        # Strip markdown fences
        summary = re.sub(r'^```markdown\s*\n', '', summary)
        summary = re.sub(r'\n?```\s*$', '', summary)
        summary = summary.strip()

        # Ensure it ends with a period if it doesn't already
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'

        return summary if summary else fallback

    except Exception:
        return fallback
