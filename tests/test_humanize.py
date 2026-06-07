"""Tests for the humanize module."""

import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent_publish.humanize import humanize_markdown, _get_api_config


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


# ── humanize_markdown ───────────────────────────────────────────────────────

def _make_urlopen_mock(content: str):
    """Build a urlopen mock that returns the given content string."""
    def _urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": content}}]
        }).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    return _urlopen


def test_humanize_skips_without_key(monkeypatch):
    """No API key → returns original markdown unchanged."""
    monkeypatch.delenv("AGENT_PUBLISH_API_KEY", raising=False)
    md = "# Hello\n\nThis is a test."
    assert humanize_markdown(md) == md


def test_humanize_explicit_key():
    """When API key is passed explicitly and call succeeds."""
    md = "# Hello\n\nThis is a test."
    with patch("urllib.request.urlopen", _make_urlopen_mock("# Hello\n\nThis works!")):
        result = humanize_markdown(md, api_key="sk-test")
    assert result == "# Hello\n\nThis works!"


def test_humanize_strips_markdown_fences():
    """Model sometimes wraps response in markdown fences; we strip them."""
    md = "# Hello"
    with patch("urllib.request.urlopen", _make_urlopen_mock("```markdown\n# Hello\n```")):
        result = humanize_markdown(md, api_key="sk-test")
    assert result == "# Hello"


def test_humanize_graceful_on_network_error(monkeypatch):
    """Any urllib error returns original markdown."""
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nThis is a test."
    with patch("urllib.request.urlopen", side_effect=OSError("boom")):
        result = humanize_markdown(md)
    assert result == md


def test_humanize_graceful_on_json_parse_error(monkeypatch):
    """Malformed JSON response returns original markdown."""
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello"
    def bad_resp(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = b"not json"
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", bad_resp):
        result = humanize_markdown(md)
    assert result == md


def test_humanize_custom_prompt(monkeypatch):
    """Custom prompt template with {content} placeholder."""
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello"
    prompt = "Rewrite this:\n{content}"
    calls = []
    def capture(*a, **kw):
        calls.append(a[0])  # a[0] is the Request object
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": "# Hi"}}]
        }).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", capture):
        result = humanize_markdown(md, prompt_template=prompt)
    assert result == "# Hi"
    assert len(calls) == 1
    payload = json.loads(calls[0].data.decode("utf-8"))
    assert "Rewrite this:" in payload["messages"][0]["content"]
    assert "# Hello" in payload["messages"][0]["content"]
    assert payload["model"] == "gpt-4o-mini"


def test_humanize_explicit_model_and_base(monkeypatch):
    """api_base and model parameters override env defaults."""
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello"
    calls = []
    def capture(*a, **kw):
        calls.append(a[0])
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": "# Hello"}}]
        }).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", capture):
        result = humanize_markdown(md, api_base="https://api.x.ai/v1", model="grok-2")
    assert result == "# Hello"
    assert calls[0].full_url == "https://api.x.ai/v1/chat/completions"
    payload = json.loads(calls[0].data.decode("utf-8"))
    assert payload["model"] == "grok-2"


def test_humanize_explicit_key_overrides_env(monkeypatch):
    """Explicit api_key parameter takes precedence over env var."""
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "env-key")
    md = "# Hello"
    calls = []
    def capture(*a, **kw):
        calls.append(a[0])
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": "# Hello"}}]
        }).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", capture):
        result = humanize_markdown(md, api_key="explicit-key")
    assert result == "# Hello"
    # The request should use the explicit key
    assert calls[0].headers["Authorization"] == "Bearer explicit-key"
