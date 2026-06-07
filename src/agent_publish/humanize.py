"""Humanize markdown via LLM rewrite before HTML conversion.

Optional post-processing hook. When enabled, pipes markdown through
an LLM to improve readability, tone, and flow. Requires an API key
via AGENT_PUBLISH_API_KEY environment variable.

Graceful fallback: if no key or the call fails, returns original markdown.
"""

import os
import re
from typing import Optional

# Default prompt used for humanization
_DEFAULT_PROMPT = """You are a writing editor. Improve the following markdown for clarity,
conciseness, and natural flow. Keep all headings, code blocks, tables, and images intact.
Do not change the factual content. Return ONLY the rewritten markdown, no preamble.

{content}
"""


def _get_api_config():
    """Read LLM API config from environment variables."""
    key = os.environ.get("AGENT_PUBLISH_API_KEY", "")
    base = os.environ.get("AGENT_PUBLISH_API_BASE", "https://api.openai.com/v1")
    model = os.environ.get("AGENT_PUBLISH_MODEL", "gpt-4o-mini")
    return key, base, model


def humanize_markdown(
    md_content: str,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    prompt_template: Optional[str] = None,
) -> str:
    """Humanize markdown content via LLM.

    Args:
        md_content: Original markdown string.
        api_key: Explicit API key (overrides env).
        api_base: Explicit API base URL (overrides env).
        model: Explicit model name (overrides env).
        prompt_template: Custom prompt template with {content} placeholder.

    Returns:
        Rewritten markdown, or original if no API key / request fails.
    """
    env_key, env_base, env_model = _get_api_config()
    key = api_key or env_key
    base_url = api_base or env_base
    model_name = model or env_model

    if not key:
        # Graceful skip — no key, return original
        return md_content

    prompt = (prompt_template or _DEFAULT_PROMPT).format(content=md_content)

    try:
        import json
        import urllib.request

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }

        payload = json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 4096,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=payload,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rewritten = data["choices"][0]["message"]["content"]

        # Strip any markdown fences the model may have wrapped the response in
        rewritten = re.sub(r'^```markdown\s*\n', '', rewritten)
        rewritten = re.sub(r'\n?```\s*$', '', rewritten)
        return rewritten.strip()

    except Exception:
        # Any failure (network, timeout, parsing) — return original gracefully
        return md_content
