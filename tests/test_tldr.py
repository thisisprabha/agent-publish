"""Tests for the tldr module."""

from unittest.mock import MagicMock, patch

from agent_publish.tldr import (
    _get_api_config,
    extract_first_paragraph,
    generate_tldr,
)

# ── _get_api_config ──────────────────────────────────────────────────────────

def test_get_api_config_defaults(monkeypatch):
    """Clear env vars; should return empty key and defaults."""
    monkeypatch.delenv("AGENT_PUBLISH_API_KEY", raising=False)
    monkeypatch.delenv("AGENT_PUBLISH_API_BASE", raising=False)
    monkeypatch.delenv("AGENT_PUBLISH_MODEL", raising=False)
    key, base, model = _get_api_config()
    assert key == ""
    assert base == "https://api.openai.com/v1"
    assert model == "gpt-4o-mini"


def test_get_api_config_custom(monkeypatch):
    """Custom env vars should be respected."""
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    monkeypatch.setenv("AGENT_PUBLISH_API_BASE", "https://api.x.ai/v1")
    monkeypatch.setenv("AGENT_PUBLISH_MODEL", "grok-2")
    key, base, model = _get_api_config()
    assert key == "sk-test"
    assert base == "https://api.x.ai/v1"
    assert model == "grok-2"


# ── extract_first_paragraph ──────────────────────────────────────────────────

def test_extract_first_paragraph_basic():
    """Extracts the first substantial paragraph."""
    md = "# Title\n\nThis is the first real paragraph with enough words.\n\nSecond paragraph."
    result = extract_first_paragraph(md)
    assert result == "This is the first real paragraph with enough words."


def test_extract_first_paragraph_skips_headings():
    """Headings should not be treated as paragraphs."""
    md = "# Hello\n\n## Subheading\n\nActual paragraph here with enough words."
    result = extract_first_paragraph(md)
    assert "Actual paragraph" in result


def test_extract_first_paragraph_strips_code():
    """Code blocks should be removed."""
    md = "# Title\n\n```python\nprint('hello')\n```\n\nReal content starts here with enough words."
    result = extract_first_paragraph(md)
    assert result == "Real content starts here with enough words."


def test_extract_first_paragraph_strips_inline_code():
    """Inline code marks and content should be removed."""
    md = "# Title\n\nThe `function()` does things and this paragraph has enough words."
    result = extract_first_paragraph(md)
    assert "`function()`" not in result
    assert "does things and this paragraph has enough words" in result


def test_extract_first_paragraph_strips_images():
    """Image markdown should be removed."""
    md = "# Title\n\nBefore ![alt](img.png) after with enough words for a paragraph."
    result = extract_first_paragraph(md)
    assert "!" not in result
    assert "alt" not in result
    assert "img.png" not in result
    assert "Before after with enough words" in result


def test_extract_first_paragraph_strips_links():
    """Links should be flattened to text."""
    md = "# Title\n\nRead [this guide](https://example.com) for more info and enough words."
    result = extract_first_paragraph(md)
    assert "[" not in result
    assert "this guide" in result


def test_extract_first_paragraph_strips_html():
    """HTML tags should be removed."""
    md = "# Title\n\nSome <em>emphasis</em> here with enough words in the paragraph."
    result = extract_first_paragraph(md)
    assert "<em>" not in result
    assert "emphasis" in result


def test_extract_first_paragraph_short_fallback():
    """If all paragraphs are short, still pick the first non-empty one."""
    md = "# Title\n\nShort.\n\nAlso short."
    result = extract_first_paragraph(md)
    assert result == "Short."


def test_extract_first_paragraph_empty():
    """Empty markdown returns empty string."""
    md = ""
    result = extract_first_paragraph(md)
    assert result == ""


# ── generate_tldr ──────────────────────────────────────────────────────────

def test_generate_tldr_no_key(monkeypatch):
    """No API key should fall back to first paragraph extraction."""
    monkeypatch.delenv("AGENT_PUBLISH_API_KEY", raising=False)
    md = "# Hello\n\nThis is the first paragraph with enough words to count."
    result = generate_tldr(md)
    assert result == "This is the first paragraph with enough words to count."


def test_generate_tldr_with_key(monkeypatch):
    """When API key works, return LLM summary."""
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nThis is content."

    def _urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "A summary of the content."}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp

    with patch("urllib.request.urlopen", _urlopen):
        result = generate_tldr(md)
    assert result == "A summary of the content."


def test_generate_tldr_strips_markdown_fences(monkeypatch):
    """Model wrapping result in markdown fences should have them stripped."""
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nContent."

    def _urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "```markdown\nA summary of the content.\n```"}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp

    with patch("urllib.request.urlopen", _urlopen):
        result = generate_tldr(md)
    assert result == "A summary of the content."


def test_generate_tldr_adds_period(monkeypatch):
    """Summary missing punctuation should get a period appended."""
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nContent."

    def _urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "A summary"}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp

    with patch("urllib.request.urlopen", _urlopen):
        result = generate_tldr(md)
    assert result.endswith(".")
    assert result == "A summary."


def test_generate_tldr_graceful_on_error(monkeypatch):
    """Network error falls back to first paragraph."""
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nFallback paragraph with enough words to be substantial."
    with patch("urllib.request.urlopen", side_effect=OSError("boom")):
        result = generate_tldr(md)
    assert result == "Fallback paragraph with enough words to be substantial."


def test_generate_tldr_explicit_key_overrides_env(monkeypatch):
    """Explicit api_key parameter overrides env var."""
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "env-key")
    md = "# Hello\n\nContent."
    calls = []

    def capture(*a, **kw):
        calls.append(a[0])
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "Summary."}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp

    with patch("urllib.request.urlopen", capture):
        result = generate_tldr(md, api_key="explicit-key")
    assert result == "Summary."
    assert calls[0].headers["Authorization"] == "Bearer explicit-key"
