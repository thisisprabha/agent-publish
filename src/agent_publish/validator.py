"""Validation and eval for agent-publish."""

import html.parser
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VerificationResult:
    success: bool
    status: Optional[str]
    error: Optional[str]


@dataclass
class AntiSlopViolation:
    severity: str  # 'error' or 'warning'
    category: str  # e.g. 'filler_phrases', 'heading_hierarchy', etc.
    details: str


class AntiSlopChecker:
    """Post-conversion quality gate: regex/heuristic checks only. Zero tokens."""

    # AI slop filler phrases (case-insensitive regex)
    FILLER_PATTERNS = [
        re.compile(
            r'\b(seamless|unleash|elevate|revolutionize|game-changing?|cutting-edge|next-gen|world-class|empower(ing)?|unlock(ing)?)\b',  # noqa: E501
            re.IGNORECASE,
        ),
        re.compile(
            r'\b(quietly trusted by|innovative solution|transformative|disrupt(ive)?|supercharge|skyrocket|deep dive|landscape)\b',  # noqa: E501
            re.IGNORECASE,
        ),
        re.compile(
            r'\b(holistic|synergy|leverag(e|ing)|paradigm shift|at scale|thought leader|optimize your workflow)\b',  # noqa: E501
            re.IGNORECASE,
        ),
    ]

    # Code block without class="language-*" (highlighted by CodeHilite)
    _CODE_NO_LANG_RE = re.compile(
        r'<pre[^>]*>\s*<code(?![^>]*class="[^"]*language)[^>]*>',
        re.IGNORECASE,
    )

    # Orphan links: <a href="#"> or <a href="">
    _ORPHAN_LINK_RE = re.compile(
        r'<a\s+[^>]*href=["\'](#|)["\']',
        re.IGNORECASE,
    )

    def check(self, html_content: str) -> list[AntiSlopViolation]:
        violations: list[AntiSlopViolation] = []

        # 1. Filler phrases in visible text
        self._check_fillers(html_content, violations)

        # 2. Heading hierarchy: h1 must exist before h2, no level skips > 1
        self._check_heading_hierarchy(html_content, violations)

        # 3. Empty sections: headings with no visible content after them
        self._check_empty_sections(html_content, violations)

        # 4. Code blocks without language tags
        self._check_code_has_language(html_content, violations)

        # 5. Orphan links
        self._check_orphan_links(html_content, violations)

        return violations

    def _check_fillers(self, html: str, violations: list) -> None:
        """Find filler slop phrases in visible text."""
        text = self._strip_html_tags(html)
        for pattern in self.FILLER_PATTERNS:
            for match in pattern.finditer(text):
                violations.append(
                    AntiSlopViolation(
                        severity="warning",
                        category="filler_phrases",
                        details=f"Filler phrase: '{match.group(0)}'",
                    )
                )

    def _check_heading_hierarchy(self, html: str, violations: list) -> None:
        """Check heading levels: h1 before h2, no skips > 1."""
        pattern = re.compile(r'<h([1-6])', re.IGNORECASE)
        levels = [int(m.group(1)) for m in pattern.finditer(html)]
        if not levels:
            violations.append(
                AntiSlopViolation(
                    severity="error",
                    category="heading_hierarchy",
                    details="No headings found (at least one h1 required)",
                )
            )
            return

        if 1 not in levels:
            violations.append(
                AntiSlopViolation(
                    severity="error",
                    category="heading_hierarchy",
                    details="No <h1> found",
                )
            )

        # h2+ must not appear before first h1
        first_h1_idx = next(
            (i for i, v in enumerate(levels) if v == 1),
            None,
        )
        if first_h1_idx is not None:
            bad_before = [
                i for i, v in enumerate(levels)
                if i < first_h1_idx and v >= 2
            ]
            if bad_before:
                violations.append(
                    AntiSlopViolation(
                        severity="error",
                        category="heading_hierarchy",
                        details="Subheading found before first <h1>",
                    )
                )

        # No level skips > 1 (e.g., h1 -> h3 without h2)
        for i in range(1, len(levels)):
            if levels[i] > levels[i - 1] and levels[i] - levels[i - 1] > 1:
                violations.append(
                    AntiSlopViolation(
                        severity="warning",
                        category="heading_hierarchy",
                        details=f"Heading level skip: h{levels[i - 1]} → h{levels[i]}",  # noqa: E501
                    )
                )

    def _check_empty_sections(self, html: str, violations: list) -> None:
        """Detect headings that have no content after them until next heading."""
        parts = re.split(
            r'(<h[1-6][^>]*>.*?</h[1-6]>)', html, flags=re.IGNORECASE | re.DOTALL
        )
        for i, part in enumerate(parts):
            if re.match(r'<h[1-6]', part, re.IGNORECASE):
                next_part = parts[i + 1] if i + 1 < len(parts) else ""
                stripped = re.sub(r'<[^>]+>', '', next_part).strip()
                stripped = re.sub(r'&nbsp;|\s+', ' ', stripped).strip()
                if stripped == "":
                    violations.append(
                        AntiSlopViolation(
                            severity="warning",
                            category="empty_sections",
                            details="Section with heading but no visible content",
                        )
                    )

    def _check_code_has_language(self, html: str, violations: list) -> None:
        """Warn if code blocks found without language=\"...\" class."""
        for _ in self._CODE_NO_LANG_RE.finditer(html):
            violations.append(
                AntiSlopViolation(
                    severity="warning",
                    category="code_language",
                    details="Code block without language tag",
                )
            )

    def _check_orphan_links(self, html: str, violations: list) -> None:
        """Warn about links with empty or hash-only hrefs."""
        for _ in self._ORPHAN_LINK_RE.finditer(html):
            violations.append(
                AntiSlopViolation(
                    severity="warning",
                    category="orphan_links",
                    details="Link with empty or '#' href",
                )
            )

    def _strip_html_tags(self, html: str) -> str:
        """Remove scripts, styles, comments, and all HTML tags from content."""
        text = re.sub(
            r'<script[^>]*>.*?</script>',
            ' ', html, flags=re.DOTALL | re.IGNORECASE,
        )
        text = re.sub(
            r'<style[^>]*>.*?</style>',
            ' ', text, flags=re.DOTALL | re.IGNORECASE,
        )
        text = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
        text = text.replace('&mdash;', '—').replace('&ndash;', '–').replace(
            '&hellip;', '…'
        )
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace(
            '&gt;', '>'
        )
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class _H1Parser(html.parser.HTMLParser):
    """Simple HTML parser to detect presence of an <h1> tag."""

    def __init__(self) -> None:
        super().__init__()
        self.has_h1 = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag.lower() == "h1":
            self.has_h1 = True

    def handle_endtag(self, tag: str) -> None:
        pass


class Validator:
    """Validate published HTML outputs."""

    def verify_file(self, html_path: Path) -> VerificationResult:
        """Verify local HTML file."""
        if not html_path.exists():
            return VerificationResult(
                success=False, status=None, error="File not found"
            )

        content = html_path.read_text(encoding='utf-8')

        # Check required elements
        checks = [
            ("title", r"<title>[^<]+</title>"),
            ("charset", r'charset="UTF-8"'),
            ("viewport", r'content="width=device-width'),
            ("style", r"<style>.*</style>", re.DOTALL),
        ]

        for name, pattern, *flags in checks:
            flag = flags[0] if flags else 0
            if not re.search(pattern, content, flag):
                return VerificationResult(
                    success=False,
                    status=None,
                    error=f"Missing: {name}",
                )

        # Check h1 using proper HTML parser
        h1_parser = _H1Parser()
        h1_parser.feed(content)
        if not h1_parser.has_h1:
            return VerificationResult(
                success=False,
                status=None,
                error="Missing: h1",
            )

        # Check no external CSS deps
        if 'rel="stylesheet"' in content and 'href="http' in content:
            return VerificationResult(
                success=False,
                status=None,
                error="External CSS dependency detected",
            )

        return VerificationResult(success=True, status="Valid HTML", error=None)

    def verify_url(self, url: str, timeout: int = 30) -> VerificationResult:
        """Verify URL is reachable."""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'agent-publish/0.1.0 (validator)',
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return VerificationResult(
                        success=True,
                        status=f"HTTP {response.status}",
                        error=None,
                    )
                return VerificationResult(
                    success=False,
                    status=f"HTTP {response.status}",
                    error=f"Unexpected status: {response.status}",
                )
        except Exception as e:
            return VerificationResult(success=False, status=None, error=str(e))
