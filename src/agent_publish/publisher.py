"""GitHub Pages publishing with cache-aware deployment."""

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from . import index as index_mod


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
        theme_css: Optional[str] = None,
        site_title: str = "Published Articles",
        generate_index: bool = True,
        generate_feed: bool = True,
    ):
        self.repo_path = Path(repo_path)
        self.base_url = base_url.rstrip('/')
        self.content_dir = content_dir
        self.auto_push = auto_push
        self.commit_prefix = commit_prefix
        self.theme_css = theme_css
        self.site_title = site_title
        self._generate_index = generate_index
        self._generate_feed = generate_feed
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
    
    def _generate_index_and_feed(self):
        """Regenerate index.html and feed.xml after publish."""
        if not self._generate_index and not self._generate_feed:
            return
        output_dir = self.repo_path / self.content_dir
        if not output_dir.exists():
            return
        gen = index_mod.IndexGenerator(
            output_dir=output_dir,
            base_url=f"{self.base_url}/{self.content_dir}",
            theme_css=self.theme_css,
        )
        if self._generate_index:
            gen.generate_index(site_title=self.site_title)
        if self._generate_feed:
            gen.generate_feed(site_title=self.site_title, site_url=self.base_url)
    
    def publish(
        self,
        html_path: Path,
        title: str,
        fingerprint: str,
        asset_paths: Optional[List[Path]] = None,
    ) -> PublishResult:
        """Publish HTML file to GitHub Pages.
        
        Args:
            html_path: Path to generated HTML file
            title: Content title for commit message
            fingerprint: Content fingerprint for dedup
            asset_paths: Optional list of asset files to copy alongside the HTML
            
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
        
        # Copy any assets
        if asset_paths:
            for asset in asset_paths:
                if asset.exists():
                    relative = asset.relative_to(asset.parent.parent)
                    asset_target = target_dir / relative
                    asset_target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(asset, asset_target)
        
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
            
            # Regenerate index + feed
            if self._generate_index or self._generate_feed:
                self._generate_index_and_feed()
                # Re-commit if index/feed changed
                subprocess.run(
                    ["git", "-C", str(self.repo_path), "add", "."],
                    check=True, capture_output=True, text=True,
                )
                # Re-commit if index changed
                status2 = subprocess.run(
                    ["git", "-C", str(self.repo_path), "status", "--porcelain"],
                    check=True, capture_output=True, text=True,
                )
                if status2.stdout.strip():
                    subprocess.run(
                        ["git", "-C", str(self.repo_path), "commit", "-m", f"{self.commit_prefix} regenerate index + feed"],
                        check=True, capture_output=True, text=True,
                    )
            
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
    asset_paths: Optional[List[Path]] = None,
    **kwargs,
) -> PublishResult:
    """Convenience function for one-off publishing."""
    publisher = GitPublisher(repo_path, base_url, **kwargs)
    return publisher.publish(html_path, title, fingerprint, asset_paths=asset_paths)
