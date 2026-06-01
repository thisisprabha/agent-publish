"""State-aware cron template for agent-publish.

Prevents the "same research every day" failure mode by tracking content fingerprints.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

STATE_DIR = Path("~/.hermes/cron/state/agent-publish").expanduser()


def get_content_fingerprint(content: str) -> str:
    """Generate content fingerprint for dedup."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def check_duplicate(key: str, content: str) -> tuple[bool, str]:
    """Check if content is duplicate vs previous run.
    
    Returns:
        (is_duplicate, fingerprint)
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    current_fp = get_content_fingerprint(content)
    state_file = STATE_DIR / f"{key}.json"
    
    if state_file.exists():
        prev = json.loads(state_file.read_text())
        if prev.get("fingerprint") == current_fp:
            return True, current_fp
    
    return False, current_fp


def save_fingerprint(key: str, fingerprint: str):
    """Save fingerprint for future dedup."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = STATE_DIR / f"{key}.json"
    state_file.write_text(json.dumps({
        "fingerprint": fingerprint,
        "last_run": datetime.now().isoformat(),
    }, indent=2))


def should_publish(input_path: Path, force: bool = False) -> tuple[bool, str, str]:
    """Check if file should be published.
    
    Returns:
        (should_publish, fingerprint, status_message)
    """
    if force:
        content = input_path.read_text()
        return True, get_content_fingerprint(content), "Force publish enabled"
    
    content = input_path.read_text()
    is_dup, fp = check_duplicate(str(input_path), content)
    
    if is_dup:
        return False, fp, "[SILENT] Content unchanged since last publish"
    
    return True, fp, f"Content changed, fingerprint: {fp[:8]}..."
