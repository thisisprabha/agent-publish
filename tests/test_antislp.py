"""Tests for AntiSlopChecker."""

from agent_publish.validator import AntiSlopChecker


def test_antislop_no_violations_on_clean_html():
    """AntiSlopChecker passes on clean HTML with no slop."""
    html = """<html><body>
<h1>Real Title</h1>
<p>This is actual content with no filler.</p>
<h2>Section One</h2>
<p>More real words here.</p>
<pre><code class="language-python">print("hi")</code></pre>
<p><a href="https://example.com">valid</a></p>
</body></html>"""
    checker = AntiSlopChecker()
    violations = checker.check(html)
    assert len(violations) == 0


def test_antislop_filler_phrases():
    """Detects AI slop filler phrases as warnings."""
    html = "<html><body><h1>Title</h1><p>We will unleash the power.</p></body></html>"
    checker = AntiSlopChecker()
    violations = checker.check(html)
    fillers = [v for v in violations if v.category == "filler_phrases"]
    assert len(fillers) >= 1
    assert fillers[0].severity == "warning"


def test_antislop_code_without_language():
    """Warns when code block lacks language class."""
    html = '<html><body><h1>T</h1><pre><code>no lang</code></pre></body></html>'
    checker = AntiSlopChecker()
    violations = checker.check(html)
    code_v = [v for v in violations if v.category == "code_language"]
    assert len(code_v) == 1
    assert code_v[0].severity == "warning"


def test_antislop_orphan_links():
    """Warns about empty/href-only links."""
    html = '<html><body><h1>T</h1><a href="#">orphan</a></body></html>'
    checker = AntiSlopChecker()
    violations = checker.check(html)
    links = [v for v in violations if v.category == "orphan_links"]
    assert len(links) == 1
    assert links[0].severity == "warning"


def test_antislop_heading_hierarchy_error_no_h1():
    """Error when no h1 exists."""
    html = '<html><body><h2>Section</h2><p>text</p></body></html>'
    checker = AntiSlopChecker()
    violations = checker.check(html)
    h1_errs = [v for v in violations if v.category == "heading_hierarchy" and v.severity == "error"]
    assert any("h1" in v.details or "headings" in v.details for v in h1_errs)


def test_antislop_heading_level_skip():
    """Warning on h1 -> h3 skip."""
    html = '<html><body><h1>T</h1><h3>S</h3><p>text</p></body></html>'
    checker = AntiSlopChecker()
    violations = checker.check(html)
    skips = [v for v in violations if "skip" in v.details]
    assert len(skips) == 1
    assert skips[0].severity == "warning"


def test_antislop_empty_section():
    """Warning when heading has no content before next heading."""
    html = '<html><body><h1>T</h1><h2>E</h2><h3>F</h3><p>ok</p></body></html>'
    checker = AntiSlopChecker()
    violations = checker.check(html)
    empty = [v for v in violations if v.category == "empty_sections"]
    assert len(empty) == 2
    assert all(v.severity == "warning" for v in empty)


def test_antislop_strip_html_excludes_scripts_and_styles():
    """Script/style content should not trigger filler warnings."""
    html = """<html><body><h1>T</h1>
<script>var unleash = true;</script>
<style>.unleash { color: red; }</style>
<p>Clean text.</p>
</body></html>"""
    checker = AntiSlopChecker()
    violations = checker.check(html)
    fillers = [v for v in violations if v.category == "filler_phrases"]
    assert len(fillers) == 0


def test_antislop_h2_before_h1_error():
    """Error when h2 appears before first h1."""
    html = '<html><body><h2>Early</h2><h1>Title</h1><p>x</p></body></html>'
    checker = AntiSlopChecker()
    violations = checker.check(html)
    hier = [v for v in violations if v.category == "heading_hierarchy"]
    assert any("before" in v.details for v in hier)
