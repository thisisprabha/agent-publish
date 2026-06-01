"""Validation and eval for agent-publish."""

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
            ("h1", r"<h1>[^<]+</h1>"),
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
