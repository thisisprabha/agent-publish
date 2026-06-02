"""Validation and eval for agent-publish."""

import html.parser
import urllib.request
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VerificationResult:
    success: bool
    status: Optional[str]
    error: Optional[str]


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
            return VerificationResult(success=False, status=None, error="File not found")
        
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
            req = urllib.request.Request(url, headers={
                'User-Agent': 'agent-publish/0.1.0 (validator)',
            })
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return VerificationResult(
                        success=True,
                        status=f"HTTP {response.status}",
                        error=None,
                    )
                else:
                    return VerificationResult(
                        success=False,
                        status=f"HTTP {response.status}",
                        error=f"Unexpected status: {response.status}",
                    )
        except Exception as e:
            return VerificationResult(success=False, status=None, error=str(e))
