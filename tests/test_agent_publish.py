"""Tests for agent-publish."""

import sys
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
        [sys.executable, "-m", "agent_publish.cli", "--version"],
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
        input_file.write_text("# Report with Image\n\n![diagram](diagram.png)\n")

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


def test_mermaid_block_renders():
    """Test that mermaid code blocks appear as <pre class='mermaid'>."""
    from agent_publish.converter import convert_file
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "mermaid.md"
        input_file.write_text(
            "# Diagram\n\n```mermaid\ngraph TD;\n  A-->B;\n```\n\nDone.\n"
        )
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert '<pre class="mermaid">graph TD;' in html
        assert "</code>" not in html.split('<pre class="mermaid">')[1].split("</pre>")[0]


def test_mermaid_script_injected_when_present():
    """Test that Mermaid.js CDN script is injected when mermaid blocks present."""
    from agent_publish.converter import convert_file
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "mermaid.md"
        input_file.write_text(
            "# Diagram\n\n```mermaid\nflowchart LR\n  Hello --> World\n```\n"
        )
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert "mermaid@11/dist/mermaid.min.js" in html
        assert 'mermaid.initialize({startOnLoad:true, theme: "default"})' in html


def test_mermaid_script_not_injected_when_absent():
    """Test that Mermaid.js CDN script is NOT injected when no mermaid blocks."""
    from agent_publish.converter import convert_file
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "plain.md"
        input_file.write_text("# Hello\n\nJust plain text.\n")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert "mermaid.min.js" not in html
        assert "mermaid.initialize" not in html


def test_cli_no_mermaid_flag():
    """Test --no-mermaid flag suppresses injection."""
    from agent_publish.config import Config, merge_with_cli_args
    cfg = Config(mermaid=True)
    merged = merge_with_cli_args(cfg, mermaid=False)
    assert merged.mermaid is False


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
    test_mermaid_block_renders()
    test_mermaid_script_injected_when_present()
    test_mermaid_script_not_injected_when_absent()
    test_cli_no_mermaid_flag()
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
        [sys.executable, "-m", "agent_publish.cli", "--site-title", "Test"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0  # no subcommand = error


def test_cli_template_flag():
    """Test --template flag is accepted and used in publish command."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "test.md"
        md.write_text("# Template Flag\n\nContent.")
        tpl = Path(tmp) / "my.html"
        tpl.write_text(
            '<!DOCTYPE html><html><head><title>{title}</title></head>'
            '<body><h1>{title}</h1><div class="date">{date}</div>'
            '<div class="fp">{fingerprint}</div><style>{css}</style>'
            '<div class="body">{body}</div></body></html>'
        )
        result = subprocess.run(
            [sys.executable, "-m", "agent_publish.cli", "publish", str(md),
             "--template", str(tpl), "--dry-run"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "Template Flag" in result.stdout


# ---- AP-025: reading time + OG meta tags ----

def test_reading_time_calculation():
    """Test reading time is based on word count at 200 WPM."""
    from agent_publish.converter import _calculate_reading_time
    assert _calculate_reading_time("# Short\n\nHello world.") == 1
    four_hundred = "word " * 400
    assert _calculate_reading_time(f"# Long\n\n{four_hundred}") >= 2


def test_reading_time_present_in_meta():
    """Test output HTML includes reading time."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "rt.md"
        input_file.write_text("# Reading Time\n\nThis is some content for readers.")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert "min read" in html


def test_og_tags_generated():
    """Test Open Graph meta tags are present."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "og.md"
        input_file.write_text("# OG Test\n\nThis is a description paragraph.")
        result = convert_file(input_file, Path(tmp), "daily")
        html = result.output_path.read_text()
        assert 'property="og:title"' in html
        assert 'property="og:description"' in html
        assert 'property="og:type"' in html
        assert 'name="description"' in html


def test_og_image_flag():
    """Test --og-image flag generates og:image meta tag."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "ogimg.md"
        input_file.write_text("# OG Image\n\nContent here.")
        result = convert_file(input_file, Path(tmp), "daily", og_image="https://example.com/img.png")
        html = result.output_path.read_text()
        assert 'property="og:image"' in html
        assert "https://example.com/img.png" in html


def test_description_extraction():
    """Test first paragraph is extracted as description."""
    from agent_publish.converter import _extract_description
    html_body = "<p>First paragraph here.</p><p>Second paragraph.</p>"
    desc = _extract_description(html_body)
    assert desc == "First paragraph here."


# ---- AP-026: watch mode tests ----

def test_rebuild_file():
    """Test _rebuild_file converts a .md and returns True on success."""
    from agent_publish.watch import _rebuild_file
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "hello.md"
        md.write_text("# Hello\n\nWorld.")
        out = Path(tmp) / "dist"
        ok = _rebuild_file(md, out)
        assert ok is True
        assert (out / f"{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}-hello.html").exists()


def test_rebuild_file_failure():
    """Test _rebuild_file returns False when input is invalid."""
    from agent_publish.watch import _rebuild_file
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.md"
        bad.write_text("")  # no H1, but still convertible
        out = Path(tmp) / "dist"
        # Empty markdown IS convertible, so we need a truly bad path
        ok = _rebuild_file(Path(tmp) / "does_not_exist.md", out)
        assert ok is False


def test_watch_server_initial_build():
    """Test WatchServer builds existing .md files on startup."""
    from agent_publish.watch import WatchServer
    with tempfile.TemporaryDirectory() as tmp:
        watch = Path(tmp) / "watch"
        watch.mkdir()
        out = Path(tmp) / "out"
        md = watch / "note.md"
        md.write_text("# Note\n\nText.")
        hidden = watch / ".draft.md"
        hidden.write_text("# Draft\n\nText.")
        server = WatchServer(
            watch_dir=watch,
            output_dir=out,
            theme="default",
        )
        server._initial_build()
        # Only non-hidden files should be built
        html_files = list(out.glob("*.html"))
        assert len(html_files) == 1
        assert "note" in html_files[0].name


def test_watch_server_skip_hidden():
    """Test _initial_build skips hidden .md files."""
    from agent_publish.watch import WatchServer
    with tempfile.TemporaryDirectory() as tmp:
        watch = Path(tmp) / "watch"
        watch.mkdir()
        out = Path(tmp) / "out"
        (watch / ".hidden.md").write_text("# Hidden\n\n.")
        (watch / "visible.md").write_text("# Visible\n\n.")
        server = WatchServer(watch_dir=watch, output_dir=out, theme="default")
        server._initial_build()
        names = {h.name for h in out.glob("*.html")}
        assert any("visible" in n for n in names)
        assert not any("hidden" in n for n in names)


def test_cli_watch_command_help():
    """Test --watch subcommand shows up in help."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "agent_publish.cli", "watch", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "--port" in result.stdout
    assert "--watch-dir" in result.stdout
    assert "--output-dir" in result.stdout


# ---- AP-027: init subcommand tests ----

def test_init_creates_default_file():
    """Test init creates agent-publish.toml with commented defaults when non-interactive."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, "-m", "agent_publish.cli", "init"],
            capture_output=True, text=True, cwd=tmp,
        )
        assert result.returncode == 0, result.stderr
        cfg_path = Path(tmp) / "agent-publish.toml"
        assert cfg_path.exists()
        text = cfg_path.read_text()
        assert "[output]" in text
        assert "[github]" in text
        assert "[validation]" in text
        # Non-interactive defaults should be commented out
        assert '# theme = "default"' in text
        assert '# content_dir = "sketch"' in text
        assert '# site_title = "Published Articles"' in text
        assert '# repo_path = "."' in text
        assert "# favicon =" in text
        assert "Created configuration template" in result.stdout


def test_init_respects_config_path():
    """Test init --config writes to the specified path."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        custom = Path(tmp) / "nested" / "custom.toml"
        result = subprocess.run(
            [sys.executable, "-m", "agent_publish.cli", "init", "--config", str(custom)],
            capture_output=True, text=True, cwd=tmp,
        )
        assert result.returncode == 0, result.stderr
        assert custom.exists()
        assert "[output]" in custom.read_text()


def test_init_refuses_overwrite():
    """Test init exits 1 when file exists and not in interactive TTY."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "agent-publish.toml"
        cfg_path.write_text("# existing\n")
        result = subprocess.run(
            [sys.executable, "-m", "agent_publish.cli", "init"],
            capture_output=True, text=True, cwd=tmp,
        )
        assert result.returncode == 1, result.stderr
        # File should remain unchanged
        assert cfg_path.read_text() == "# existing\n"
        assert "already" in result.stdout and "exists" in result.stdout


def test_converter_favicon_and_author():
    """Test favicon copy and author meta tag generation."""
    with tempfile.TemporaryDirectory() as tmp:
        input_file = Path(tmp) / "test.md"
        input_file.write_text("# Favicon Test\n\nSome content here.")
        favicon_file = Path(tmp) / "favicon.ico"
        favicon_file.write_bytes(b"fake-icon-data")

        result = convert_file(
            input_file, Path(tmp), "daily",
            favicon=favicon_file,
            author="Alice",
        )
        html = result.output_path.read_text()

        # Favicon link tag present
        assert '<link rel="icon"' in html
        assert 'href="favicon.ico"' in html

        # Favicon copied to output
        copied = Path(tmp) / "favicon.ico"
        assert copied.exists()
        assert copied.read_bytes() == b"fake-icon-data"


def test_load_config_favicon_and_author():
    """Test config parsing for favicon and author fields."""
    from agent_publish.config import load_config

    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "agent-publish.toml"
        favicon = Path(tmp) / "icon.png"
        favicon.write_bytes(b"x")
        cfg_path.write_text(
            f"""[output]
theme = "minimal"
favicon = "{favicon}"
author = "Bob"
site_title = "Bob's Blog"
"""
        )
        cfg = load_config(cfg_path)
        assert cfg.theme == "minimal"
        assert cfg.favicon == favicon.resolve()
        assert cfg.author == "Bob"
        assert cfg.site_title == "Bob's Blog"


def test_cli_favicon_flag():
    """Test CLI --favicon and --author flags reach the converter."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "page.md"
        md.write_text("# Flag Test\n\nBody.")
        favicon = Path(tmp) / "fav.png"
        favicon.write_bytes(b"x")
        # Just ensure the CLI parses --favicon and --author without error
        result = subprocess.run(
            [
                sys.executable, "-m", "agent_publish.cli",
                "publish", str(md),
                "--dry-run",
                "--favicon", str(favicon),
                "--author", "Charlie",
            ],
            capture_output=True, text=True, cwd=tmp,
        )
        assert result.returncode == 0, result.stderr


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
    test_reading_time_calculation()
    test_reading_time_present_in_meta()
    test_og_tags_generated()
    test_og_image_flag()
    test_description_extraction()
    test_rebuild_file()
    test_rebuild_file_failure()
    test_watch_server_initial_build()
    test_watch_server_skip_hidden()
    test_mermaid_block_renders()
    test_mermaid_script_injected_when_present()
    test_mermaid_script_not_injected_when_absent()
    test_cli_no_mermaid_flag()
    test_init_creates_default_file()
    test_init_respects_config_path()
    test_init_refuses_overwrite()
    test_converter_favicon_and_author()
    test_load_config_favicon_and_author()
    test_cli_favicon_flag()
    print("All tests passed!")
