"""Tests for the tags module."""

from unittest.mock import patch, MagicMock
import pytest

from agent_publish.tags import (
    _get_api_config,
    _clean_tag,
    _simple_stem,
    suggest_tags_zero_token,
    suggest_tags,
)


def test_simple_stem():
    assert _simple_stem("agents") == "agent"
    assert _simple_stem("categories") == "category"
    assert _simple_stem("glass") == "glass"
    assert _simple_stem("ai") == "ai"


def test_clean_tag_basic():
    assert _clean_tag("Hello World") == "hello-world"
    assert _clean_tag("  spaces  ") == "spaces"
    assert _clean_tag("A") is None

def test_clean_tag_inline_code():
    assert _clean_tag("`code` tag") == "tag"

def test_clean_tag_link():
    assert _clean_tag("[Link Text](https://example.com)") == "link-text"

def test_clean_tag_html():
    assert _clean_tag("Some <em>emphasis</em> here") == "some-emphasis-here"

def test_clean_tag_number_only():
    assert _clean_tag("42") is None

def test_clean_tag_stop_word():
    assert _clean_tag("the") is None
    assert _clean_tag("and") is None

def test_clean_tag_file_extension():
    assert _clean_tag("hello.py") is None
    assert _clean_tag("config.json") is None


def test_extract_from_headings():
    md = "# Tag Suggestion System\n\n## How Tags Work\n\nThis is content."
    tags = suggest_tags_zero_token(md)
    assert "tag-suggestion-system" in tags or "tag" in tags


def test_extract_from_bold():
    md = "# Title\n\nThis article covers **Artificial Intelligence** and **Machine Learning**."
    tags = suggest_tags_zero_token(md)
    assert len(tags) > 0


def test_extract_from_capitalized_phrases():
    md = "# Title\n\nAgent Tina is working on Smart Tag Discovery in the Open Source Project."
    tags = suggest_tags_zero_token(md)
    assert len(tags) > 0
    assert "smart-tag-discovery" in tags or "tina" in tags or "agent-tina" in tags


def test_extract_from_lists():
    md = "# Features\n\n- Multi-Platform Support\n- Dark Mode\n- Auto Tagging"
    tags = suggest_tags_zero_token(md)
    assert len(tags) >= 2
    assert any("multi-platform" in t or "dark-mode" in t or "auto-tagging" in t for t in tags)


def test_deduplication_by_stem():
    md = "# Title\n\n## AI agents\n\n**agent** driven workflow."
    tags = suggest_tags_zero_token(md)
    stems = {_simple_stem(t) for t in tags}
    assert "agent" in stems
    agent_tags = [t for t in tags if "agent" in t]
    assert len(agent_tags) <= 1


def test_limits_count():
    md = "# Title\n\n" + "\n\n".join([f"## Heading {i}" for i in range(1, 20)])
    tags = suggest_tags_zero_token(md, count=3)
    assert len(tags) <= 3  # deduped by simple_stem returns ≤ count


def test_ignores_code_blocks():
    md = ("# Title\n\n" +
          chr(96)*3 + "python\n" +
          "def artificial_intelligence(): pass\n" +
          chr(96)*3 +
          "\n\nThis is about Real Intelligence.")
    tags = suggest_tags_zero_token(md)
    assert "artificial-intelligence" not in tags
    assert "real-intelligence" in tags or "intelligence" in tags


def test_empty_content():
    tags = suggest_tags_zero_token("")
    assert tags == []


def test_suggest_tags_no_key(monkeypatch):
    monkeypatch.delenv("AGENT_PUBLISH_API_KEY", raising=False)
    md = "# Hello\n\nThis article covers **Artificial Intelligence** and its applications."
    tags = suggest_tags(md)
    assert isinstance(tags, list)
    assert len(tags) > 0


def test_suggest_tags_with_key(monkeypatch):
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nContent."
    fence = chr(96)*3 + "json"
    def _urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices":[{"message":{"content":'["ai","machine-learning","automation"]'}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", _urlopen):
        tags = suggest_tags(md)
    assert "ai" in tags
    assert "machine-learning" in tags
    assert "automation" in tags


def test_suggest_tags_llm_with_markdown_fences(monkeypatch):
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nContent."
    raw = chr(96)*3 + "json" + chr(10) + '["tag-one", "tag-two"]' + chr(10) + chr(96)*3
    assert chr(10) in raw, "mock LLM response must contain literal newlines"
    def _urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices":[{"message":{"content": raw}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", _urlopen):
        tags = suggest_tags(md)
    assert "tag-one" in tags
    assert "tag-two" in tags


def test_suggest_tags_graceful_on_error(monkeypatch):
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\n**Smart Tags** for categorization."
    with patch("urllib.request.urlopen", side_effect=OSError("boom")):
        tags = suggest_tags(md)
    assert isinstance(tags, list)
    assert len(tags) > 0


def test_suggest_tags_explicit_key_overrides_env(monkeypatch):
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "env-key")
    md = "# Hello\n\nContent."
    calls = []
    def capture(*a, **kw):
        calls.append(a[0])
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices":[{"message":{"content":'["override"]'}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", capture):
        tags = suggest_tags(md, api_key="explicit-key")
    assert "override" in tags
    assert "Bearer explicit-key" in calls[0].headers["Authorization"]


def test_suggest_tags_dedupes_llm_tags(monkeypatch):
    import json
    monkeypatch.setenv("AGENT_PUBLISH_API_KEY", "sk-test")
    md = "# Hello\n\nContent."
    def _urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"choices":[{"message":{"content":'["agent", "agents", "ai"]'}}]}
        ).encode("utf-8")
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp
    with patch("urllib.request.urlopen", _urlopen):
        tags = suggest_tags(md)
    assert len(tags) == 2
    assert "agent" in tags
    assert "ai" in tags
