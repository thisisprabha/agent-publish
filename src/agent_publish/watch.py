"""Watch mode: local dev server with auto-rebuild on .md changes."""

import http.server
import socketserver
import threading
from pathlib import Path
from typing import Optional

from .converter import convert_file


class RebuildHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler that serves from a configured output directory."""

    def __init__(self, output_dir: Path, *args, **kwargs):
        self.output_dir = output_dir
        super().__init__(*args, directory=str(output_dir), **kwargs)

    def log_message(self, format, *args) -> None:
        # Suppress default access logs (too noisy for dev server)
        return


def make_handler(output_dir: Path):
    """Factory for creating handler instances bound to output_dir."""
    def handler(*args, **kwargs):
        return RebuildHandler(output_dir, *args, **kwargs)
    return handler


def _rebuild_file(
    input_path: Path,
    output_dir: Path,
    theme: str = "default",
    custom_css: Optional[str] = None,
    custom_css_path: Optional[Path] = None,
    template_override: Optional[Path] = None,
    entry_type: str = "daily",
    og_image: Optional[str] = None,
) -> bool:
    """Rebuild a single markdown file. Returns True on success."""
    try:
        convert_file(
            input_path=input_path,
            output_dir=output_dir,
            entry_type=entry_type,
            custom_css=custom_css,
            custom_css_path=custom_css_path,
            template_override=template_override,
            og_image=og_image,
        )
        return True
    except Exception:
        return False


class WatchServer:
    """Watch markdown files for changes and serve on localhost."""

    def __init__(
        self,
        watch_dir: Path,
        output_dir: Path,
        port: int = 8080,
        theme: str = "default",
        custom_css: Optional[str] = None,
        custom_css_path: Optional[Path] = None,
        template_override: Optional[Path] = None,
        entry_type: str = "daily",
        og_image: Optional[str] = None,
    ):
        self.watch_dir = Path(watch_dir)
        self.output_dir = Path(output_dir)
        self.port = port
        self.theme = theme
        self.custom_css = custom_css
        self.custom_css_path = custom_css_path
        self.template_override = template_override
        self.entry_type = entry_type
        self.og_image = og_image

    def _initial_build(self):
        """Build all existing .md files on startup."""
        for md in self.watch_dir.rglob("*.md"):
            if md.name.startswith("."):
                continue  # skip hidden files
            _rebuild_file(
                md,
                self.output_dir,
                theme=self.theme,
                custom_css=self.custom_css,
                custom_css_path=self.custom_css_path,
                template_override=self.template_override,
                entry_type=self.entry_type,
                og_image=self.og_image,
            )

    def _serve(self):
        """Start blocking HTTP server in current thread."""
        handler = make_handler(self.output_dir)
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        self.httpd.serve_forever()

    def _setup_observer(self):
        """Set up watchdog observer for .md file changes."""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:  # pragma: no cover
            raise ImportError(
                "watchdog is required for --watch mode. "
                "Install it with: pip install watchdog"
            )

        class MdHandler(FileSystemEventHandler):
            def __init__(handler_self, server: "WatchServer"):
                handler_self.server = server

            def on_modified(handler_self, event):
                if event.is_directory:
                    return
                if not event.src_path.endswith(".md"):
                    return
                md_path = Path(event.src_path)
                if md_path.name.startswith("."):
                    return
                # Debounce: skip rapid-fire events within 500ms
                import time
                handler_self._last = getattr(handler_self, "_last", {})
                now = time.time()
                if handler_self._last.get(md_path, 0) > now - 0.5:
                    return
                handler_self._last[md_path] = now

                # Strip common temp file prefixes (vim swap, etc)
                if not md_path.exists():
                    return

                ok = _rebuild_file(
                    md_path,
                    handler_self.server.output_dir,
                    theme=handler_self.server.theme,
                    custom_css=handler_self.server.custom_css,
                    custom_css_path=handler_self.server.custom_css_path,
                    template_override=handler_self.server.template_override,
                    entry_type=handler_self.server.entry_type,
                    og_image=handler_self.server.og_image,
                )
                status = "✓ rebuilt" if ok else "✗ failed"
                print(f"  {status}: {md_path.name}")

            def on_created(handler_self, event):
                handler_self.on_modified(event)

        observer = Observer()
        observer.schedule(MdHandler(self), str(self.watch_dir), recursive=True)
        return observer

    def start(self) -> None:
        """Start the watch server: initial build, then serve + watch."""
        import time

        # Ensure output dir exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initial build
        print(f"  Building all .md files in {self.watch_dir}...")
        self._initial_build()
        print(f"  Output directory: {self.output_dir.resolve()}")

        # Start HTTP server in background thread
        server_thread = threading.Thread(target=self._serve, daemon=True)
        server_thread.start()
        url = f"http://localhost:{self.port}"
        print(f"  Server running at {url}\n")
        print("  Watching for changes (Ctrl+C to stop)...\n")

        # Start watchdog observer
        observer = self._setup_observer()
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n  Stopping server...")
            observer.stop()
            observer.join()
            if hasattr(self, "httpd"):
                self.httpd.shutdown()
            server_thread.join(timeout=2)
            print("  Done.")
