"""Tests for agent-publish."""

import tempfile
from pathlib import Path

import pytest

from agent_publish.converter import _clean_slug, _generate_fingerprint, convert_file
from agent_publish.validator import Validator


def test_fingerprint():
    """Test fingerprint generation."""
    fp1 = _generate_fingerprint("hello world")
    fp2 = _generate_fingerprint("hello world")
    fp3 = _generate_fingerprint("different content")
    
    assert fp1 == fp2
    assert fp1 != fp3
    assert len(fp1) == 12


def test_clean_slug():
    """Test slug cleaning."""
    assert _clean_slug("Hello World") == "hello-world"
    assert _clean_slug("Cron Job: Daily Report") == "daily-report"
    assert _clean_slug("Research Report: Findings") == "findings"
    assert _clean_slug("2024-01-01 10:00 - Meeting Notes") == "meeting-notes"
    assert _clean_slug("!!! @@@ ###") == "untitled"
    assert _clean_slug("---") == "untitled"


def test_converter():
    """Test markdown to HTML conversion."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "test.md"
        input_file.write_text("# Test Report\n\nSome content.")
        
        result = convert_file(input_file, Path(tmp), "daily")
        
        assert result.title == "Test Report"
        assert result.fingerprint
        assert result.output_path.exists()
        
        html = result.output_path.read_text()
        assert "<title>Test Report</title>" in html
        assert "<h1>Test Report</h1>" in html
        assert '<meta charset="UTF-8">' in html


def test_converter_custom_css_path():
    """Test conversion with custom CSS file path."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "test.md"
        input_file.write_text("# Custom CSS\n\nContent.")
        css_file = Path(tmp) / "custom.css"
        css_file.write_text("body { background: #bada55; }")
        
        result = convert_file(input_file, Path(tmp), "daily", custom_css_path=css_file)
        html = result.output_path.read_text()
        assert "background: #bada55" in html


def test_converter_template_override():
    """Test conversion with a custom template file."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "test.md"
        input_file.write_text("# Templated\n\nContent.")
        tpl_file = Path(tmp) / "my.html"
        tpl_file.write_text(
            '<!DOCTYPE html><html><head><title>{title}</title></head>'
            '<body><h1>{title}</h1><div class="date">{date}</div>'
            '<div class="fp">{fingerprint}</div><style>{css}</style>'
            '<div class="body">{body}</div></body></html>'
        )
        
        result = convert_file(input_file, Path(tmp), "daily", template_override=tpl_file)
        html = result.output_path.read_text()
        assert '<div class="date">' in html
        assert '<div class="fp">' in html
        assert '<div class="body">' in html
        assert "<h1>Templated</h1>" in html


def test_converter_braces_in_markdown():
    """Test that markdown containing {braces} doesn't crash template formatting."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "test.md"
        input_file.write_text(
            "# Braces Test\n\n"
            "Here is a Python f-string: `name = {example}`\n\n"
            "And a dict literal: `data = {{'key': 'value'}}`\n"
        )
        
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        
        assert result.title == "Braces Test"
        assert "{example}" in html
        assert "{{'key': 'value'}}" in html
        assert "<h1>Braces Test</h1>" in html


def test_validator():
    """Test HTML validation."""
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "test.html"
        html_path.write_text(
            '<!DOCTYPE html><html><head><title>Test</title>'
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width">'
            '<style>body{color:red}</style></head>'
            '<body><h1>Title</h1></body></html>'
        )
        
        validator = Validator()
        result = validator.verify_file(html_path)
        
        assert result.success


def test_validator_h1_with_attributes():
    """Test HTML validation passes when h1 has attributes."""
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "test.html"
        html_path.write_text(
            '<!DOCTYPE html><html><head><title>Test</title>'
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width">'
            '<style>body{color:red}</style></head>'
            '<body><h1 class="title" id="main">Title</h1></body></html>'
        )

        validator = Validator()
        result = validator.verify_file(html_path)

        assert result.success


def test_validator_h1_with_inline_html():
    """Test HTML validation passes when h1 contains inline HTML."""
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "test.html"
        html_path.write_text(
            '<!DOCTYPE html><html><head><title>Test</title>'
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width">'
            '<style>body{color:red}</style></head>'
            '<body><h1>Title <em>styled</em> text</h1></body></html>'
        )

        validator = Validator()
        result = validator.verify_file(html_path)

        assert result.success


def test_publisher_cache_dedup():
    """Test GitPublisher fingerprint deduplication."""
    import uuid
    from agent_publish.publisher import GitPublisher
    
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / "sketch").mkdir()
        
        # Create a dummy HTML file
        html_path = repo / "sketch" / "test.html"
        html_path.write_text("<html><body>test</body></html>")
        
        # Write a minimal git config so git commands don't fail
        import subprocess
        subprocess.run(
            ["git", "-C", str(repo), "init"],
            capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@test.com"],
            capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "Test"],
            capture_output=True, text=True,
        )
        
        publisher = GitPublisher(
            repo_path=repo,
            base_url="https://example.com",
            content_dir="sketch",
            auto_push=False,
        )
        
        # First publish should succeed
        result1 = publisher.publish(
            html_path=html_path,
            title="Test",
            fingerprint="fp123",
        )
        assert result1.success
        
        # Second publish with same fingerprint should be cached
        result2 = publisher.publish(
            html_path=html_path,
            title="Test",
            fingerprint="fp123",
        )
        assert result2.success
        assert "cached" in result2.message.lower()


def test_cli_version_flag():
    """Test --version flag returns version from pyproject.toml."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "agent_publish.cli", "--version"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "agent-publish" in result.stdout


# ---- Config tests ----

def test_load_config_toml():
    """Test loading TOML config."""
    from agent_publish.config import load_config
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "agent-publish.toml"
        cfg_path.write_text(
            '[output]\ntheme = "minimal"\nbase_url = "https://example.com"\n'
            'content_dir = "notes"\ncustom_css_path = "style.css"\n'
            '[github]\nrepo_path = "/tmp/repo"\nauto_push = false\n'
            'commit_prefix = "[pub]"\n'
            '[validation]\nverify_reachable = false\n'
        )
        css_file = Path(tmp) / "style.css"
        css_file.write_text("body{color:blue}")

        cfg = load_config(cfg_path)
        assert cfg.theme == "minimal"
        assert cfg.base_url == "https://example.com"
        assert cfg.output_dir == "notes"
        assert cfg.custom_css_path.resolve() == css_file.resolve()
        assert cfg.github_repo_path == "/tmp/repo"
        assert cfg.github_auto_push is False
        assert cfg.github_commit_prefix == "[pub]"
        assert cfg.validation_verify_reachable is False


def test_load_config_yaml():
    """Test loading YAML config."""
    from agent_publish.config import load_config
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "agent-publish.yaml"
        cfg_path.write_text(
            "output:\n"
            "  theme: brutalist\n"
            "  base_url: \"https://yaml.example.com\"\n"
            "  content_dir: pages\n"
            "github:\n"
            "  repo_path: \"/tmp/gh\"\n"
            "  auto_push: true\n"
            "  commit_prefix: \"🚀\"\n"
            "validation:\n"
            "  verify_reachable: true\n"
        )
        cfg = load_config(cfg_path)
        assert cfg.theme == "brutalist"
        assert cfg.base_url == "https://yaml.example.com"
        assert cfg.output_dir == "pages"
        assert cfg.github_repo_path == "/tmp/gh"
        assert cfg.github_auto_push is True
        assert cfg.github_commit_prefix == "🚀"


def test_load_config_defaults_when_missing():
    """Test defaults are applied when config file is missing."""
    from agent_publish.config import load_config
    with tempfile.TemporaryDirectory() as tmp:
        nonexistent = Path(tmp) / "does-not-exist.toml"
        cfg = load_config(nonexistent)
        assert cfg.theme == "default"
        assert cfg.output_dir == "sketch"
        assert cfg.base_url == ""
        assert cfg.github_auto_push is True


def test_load_config_validates_custom_css_path():
    """Test FileNotFoundError raised for missing custom CSS."""
    from agent_publish.config import load_config
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "bad.toml"
        cfg_path.write_text('[output]\ncustom_css_path = "/nope/missing.css"\n')
        with pytest.raises(FileNotFoundError):
            load_config(cfg_path)


def test_load_config_validates_template_override():
    """Test FileNotFoundError raised for missing template override."""
    from agent_publish.config import load_config
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "bad.yaml"
        cfg_path.write_text("output:\n  template_override: /nope/missing.html\n")
        with pytest.raises(FileNotFoundError):
            load_config(cfg_path)


def test_merge_with_cli_args():
    """Test CLI args override config values."""
    from agent_publish.config import Config, merge_with_cli_args
    cfg = Config(theme="default", base_url="https://old.com")
    merged = merge_with_cli_args(cfg, theme="minimal", base_url="https://new.com")
    assert merged.theme == "minimal"
    assert merged.base_url == "https://new.com"


# ---- Asset/image tests ----

def test_copy_assets_rewrites_src():
    """Test that copy_assets rewrites local image src paths."""
    from agent_publish.assets import copy_assets
    with tempfile.TemporaryDirectory() as tmp:
        image = Path(tmp) / "my-image.png"
        image.write_text("fake-png-data")
        html = '<p><img src="my-image.png" alt="test"></p>'
        updated, copied = copy_assets(html, base_dir=Path(tmp), output_dir=Path(tmp))
        assert len(copied) == 1
        assert copied[0].exists()
        assert 'src="images/my-image.png"' in updated


def test_copy_assets_skips_remote():
    """Test that copy_assets leaves remote URLs unchanged."""
    from agent_publish.assets import copy_assets
    html = '<p><img src="https://example.com/image.png" alt="remote"></p>'
    updated, copied = copy_assets(html, base_dir=Path("/tmp"), output_dir=Path("/tmp"))
    assert not copied
    assert 'src="https://example.com/image.png"' in updated


def test_converter_with_image():
    """Test markdown conversion copies referenced images."""
    with tempfile.TemporaryDirectory() as tmp:
        image = Path(tmp) / "diagram.png"
        image.write_text("fake-png-data")
        input_file = Path(tmp) / "report.md"
        input_file.write_text(f"# Report with Image\n\n![diagram](diagram.png)\n")

        result = convert_file(input_file, Path(tmp), "daily")

        assert result.assets_copied
        assert any(a.name == "diagram.png" for a in result.assets_copied)
        html = result.output_path.read_text()
        assert 'src="images/diagram.png"' in html


def test_converter_generates_toc():
    """Test that multi-header markdown gets a table of contents."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "toc-test.md"
        input_file.write_text(
            "# Top Level\n\nIntro.\n\n"
            "## Section A\n\nContent A.\n\n"
            "### Sub A1\n\nDeep.\n\n"
            "## Section B\n\nContent B.\n"
        )
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()

        assert '<nav class="toc">' in html
        assert 'href="#section-a"' in html
        assert 'href="#sub-a1"' in html
        assert 'href="#section-b"' in html
        assert 'id="section-a"' in html
        assert 'id="sub-a1"' in html


def test_converter_no_toc_for_single_header():
    """Test that docs with only an h1 don't get a TOC."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "no-toc.md"
        input_file.write_text("# Just Title\n\nOnly one level of heading.")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()

        assert '<nav class="toc">' not in html


def test_accessibility_skip_link():
    """Test that generated HTML includes a skip-to-content link."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "a11y.md"
        input_file.write_text("# A11y Test\n\nContent.")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert 'class="skip-link"' in html
        assert 'href="#main-content"' in html
        assert 'id="main-content"' in html


def test_accessibility_focus_visible():
    """Test that generated HTML CSS includes focus-visible outlines."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "focus.md"
        input_file.write_text("# Focus Test\n\nContent.")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert ':focus-visible' in html


def test_responsive_breakpoints():
    """Test that generated HTML includes responsive media queries."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "resp.md"
        input_file.write_text("# Responsive Test\n\nContent.")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert '(max-width:640px)' in html
        assert '(max-width:1024px)' in html


def test_print_stylesheet():
    """Test that generated HTML includes print media rules."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "print.md"
        input_file.write_text("# Print Test\n\nContent.")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert '@media print' in html
        assert '.skip-link{display:none}' in html


if __name__ == "__main__":
    test_fingerprint()
    test_clean_slug()
    test_converter()
    test_converter_custom_css_path()
    test_converter_template_override()
    test_validator()
    test_validator_h1_with_attributes()
    test_validator_h1_with_inline_html()
    test_publisher_cache_dedup()
    test_cli_version_flag()
    test_load_config_toml()
    test_load_config_yaml()
    test_load_config_defaults_when_missing()
    test_load_config_validates_custom_css_path()
    test_load_config_validates_template_override()
    test_merge_with_cli_args()
    test_copy_assets_rewrites_src()
    test_copy_assets_skips_remote()
    test_converter_with_image()
    test_converter_generates_toc()
    test_converter_no_toc_for_single_header()
    test_accessibility_skip_link()
    test_accessibility_focus_visible()
    test_responsive_breakpoints()
    test_print_stylesheet()
    print("All tests passed!")


# ---- Index page tests ----

def test_generate_index_page():
    """Test index.html generation with entries."""
    from agent_publish.index import generate_index_page
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        generate_index_page(
            entries=[{
                "title": "Alpha",
                "slug": "alpha",
                "date": "2024-12-01",
                "url": "",
                "fingerprint": "fp1",
            }],
            out_dir=out,
            site_title="Notebook",
            theme="default",
            base_url="",
        )
        index = out / "index.html"
        assert index.exists()
        html = index.read_text()
        assert "Alpha" in html
        assert "2024-12-01" in html
        assert 'href="alpha.html"' in html
        assert "<title>Notebook</title>" in html
        assert '<ul class="entry-list"' in html


def test_generate_index_empty():
    """Test index page with no entries still renders."""
    from agent_publish.index import generate_index_page
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        generate_index_page(
            entries=[],
            out_dir=out,
            site_title="Empty",
            theme="default",
            base_url="",
        )
        html = (out / "index.html").read_text()
        assert 'class="entry-list"' not in html
        assert 'No entries published yet' in html


# ---- RSS feed tests ----

def test_generate_rss_feed():
    """Test RSS feed generation."""
    from agent_publish.feed import generate_rss_feed
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        generate_rss_feed(
            entries=[{
                "title": "Alpha",
                "slug": "alpha",
                "date": "2024-12-01",
                "url": "https://example.com/alpha.html",
                "fingerprint": "fp1",
            }],
            out_dir=out,
            site_title="My Feed",
            base_url="https://example.com",
            description="Test feed",
        )
        rss = out / "feed.xml"
        assert rss.exists()
        xml = rss.read_text()
        assert "<rss version=\"2.0\"" in xml
        assert "<title>My Feed</title>" in xml
        assert "<link>https://example.com</link>" in xml
        assert "<description>Test feed</description>" in xml
        assert "<item>" in xml
        assert "<pubDate>" in xml


def test_generate_rss_empty():
    """Test RSS feed with no entries still renders channel metadata."""
    from agent_publish.feed import generate_rss_feed
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        generate_rss_feed(
            entries=[],
            out_dir=out,
            site_title="Empty Feed",
            base_url="",
            description="Nothing here",
        )
        xml = (out / "feed.xml").read_text()
        assert "<title>Empty Feed</title>" in xml
        assert "<description>Nothing here</description>" in xml
        assert "<item>" not in xml


# ---- CLI config flag tests ----

def test_cli_site_title_flag():
    """Test --site-title flag is accepted."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "agent_publish.cli", "--site-title", "Test"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0  # no subcommand = error


if __name__ == "__main__":
    test_fingerprint()
    test_clean_slug()
    test_converter()
    test_converter_custom_css_path()
    test_converter_template_override()
    test_validator()
    test_validator_h1_with_attributes()
    test_validator_h1_with_inline_html()
    test_publisher_cache_dedup()
    test_cli_version_flag()
    test_load_config_toml()
    test_load_config_yaml()
    test_load_config_defaults_when_missing()
    test_load_config_validates_custom_css_path()
    test_load_config_validates_template_override()
    test_merge_with_cli_args()
    test_copy_assets_rewrites_src()
    test_copy_assets_skips_remote()
    test_converter_with_image()
    test_converter_generates_toc()
    test_converter_no_toc_for_single_header()
    test_accessibility_skip_link()
    test_accessibility_focus_visible()
    test_responsive_breakpoints()
    test_print_stylesheet()
    test_generate_index_page()
    test_generate_index_empty()
    test_generate_rss_feed()
    test_generate_rss_empty()
    print("All tests passed!")
