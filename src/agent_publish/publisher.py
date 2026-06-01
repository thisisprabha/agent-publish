"""GitHub Pages publishing with cache-aware deployment."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PublishResult:
    success: bool
    url: Optional[str]
    commit_hash: Optional[str]
    message: str


class GitPublisher:
    """Publish HTML to GitHub Pages with fingerprint tracking."""
    
    def __init__(
        self,
        repo_path: Path,
        base_url: str,
        content_dir: str = "sketch",
        auto_push: bool = True,
        commit_prefix: str = "📦",
    ):
        self.repo_path = Path(repo_path)
        self.base_url = base_url.rstrip('/')
        self.content_dir = content_dir
        self.auto_push = auto_push
        self.commit_prefix = commit_prefix
        self._fingerprint_file = self.repo_path / ".agent_publish_cache"
    
    def _load_cache(self) -> dict:
        """Load published fingerprints cache."""
        if self._fingerprint_file.exists():
            return json.loads(self._fingerprint_file.read_text())
        return {}
    
    def _save_cache(self, cache: dict):
        """Save fingerprints cache."""
        self._fingerprint_file.write_text(json.dumps(cache, indent=2))
    
    def _is_duplicate(self, fingerprint: str, output_name: str) -> bool:
        """Check if content already published."""
        cache = self._load_cache()
        return cache.get(output_name) == fingerprint
    
    def publish(
        self,
        html_path: Path,
        title: str,
        fingerprint: str,
    ) -> PublishResult:
        """Publish HTML file to GitHub Pages.
        
        Args:
            html_path: Path to generated HTML file
            title: Content title for commit message
            fingerprint: Content fingerprint for dedup
            
        Returns:
            PublishResult with URL and status
        """
        output_name = html_path.name
        
        # Check for duplicates
        if self._is_duplicate(fingerprint, output_name):
            return PublishResult(
                success=True,
                url=f"{self.base_url}/{self.content_dir}/{output_name}",
                commit_hash=None,
                message="[cached] Content unchanged, using existing publish",
            )
        
        # Copy to repo
        target_dir = self.repo_path / self.content_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / output_name
        target_path.write_text(html_path.read_text(), encoding='utf-8')
        
        # Git operations
        try:
            subprocess.run(
                ["git", "-C", str(self.repo_path), "add", "."],
                check=True, capture_output=True, text=True,
            )
            
            # Check if there are changes
            status = subprocess.run(
                ["git", "-C", str(self.repo_path), "status", "--porcelain"],
                check=True, capture_output=True, text=True,
            )
            
            if not status.stdout.strip():
                return PublishResult(
                    success=True,
                    url=f"{self.base_url}/{self.content_dir}/{output_name}",
                    commit_hash=None,
                    message="[clean] No new changes to publish",
                )
            
            # Commit
            commit_msg = f"{self.commit_prefix} {title[:50]}"
            subprocess.run(
                ["git", "-C", str(self.repo_path), "commit", "-m", commit_msg],
                check=True, capture_output=True, text=True,
            )
            
            # Get commit hash
            commit_hash = subprocess.run(
                ["git", "-C", str(self.repo_path), "rev-parse", "--short", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            
            # Push
            if self.auto_push:
                subprocess.run(
                    ["git", "-C", str(self.repo_path), "push", "origin", "main"],
                    check=True, capture_output=True, text=True,
                )
            
            # Update cache
            cache = self._load_cache()
            cache[output_name] = fingerprint
            self._save_cache(cache)
            
            url = f"{self.base_url}/{self.content_dir}/{output_name}"
            return PublishResult(
                success=True,
                url=url,
                commit_hash=commit_hash,
                message=f"Published to {url}",
            )
            
        except subprocess.CalledProcessError as e:
            return PublishResult(
                success=False,
                url=None,
                commit_hash=None,
                message=f"Git error: {e.stderr or e.stdout}",
            )


def publish(
    html_path: Path,
    title: str,
    fingerprint: str,
    repo_path: Path,
    base_url: str,
    **kwargs,
) -> PublishResult:
    """Convenience function for one-off publishing."""
    publisher = GitPublisher(repo_path, base_url, **kwargs)
    return publisher.publish(html_path, title, fingerprint)
