"""Tests for agent-publish."""

from pathlib import Path
import tempfile

from agent_publish.converter import convert_file, _generate_fingerprint, _clean_slug
from agent_publish.state import check_duplicate, save_fingerprint
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


def test_state_dedup():
    """Test fingerprint deduplication."""
    is_dup, fp = check_duplicate("test-key", "content")
    assert not is_dup
    
    save_fingerprint("test-key", fp)
    
    is_dup, fp2 = check_duplicate("test-key", "content")
    assert is_dup


if __name__ == "__main__":
    test_fingerprint()
    test_clean_slug()
    test_converter()
    test_validator()
    test_state_dedup()
    print("All tests passed!")
