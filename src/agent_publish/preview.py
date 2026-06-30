"""Preview mode: ephemeral HTTP server for draft HTML with LiveReload."""

import http.server
import shutil
import signal
import socketserver
import tempfile
import threading
import time
from pathlib import Path
from typing import List, Optional

from .converter import convert_file


class PreviewHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves from a configured preview directory."""

    def __init__(self, preview_dir: Path, *args, **kwargs):
        self.preview_dir = preview_dir
        super().__init__(*args, directory=str(preview_dir), **kwargs)

    def log_message(self, format, *args) -> None:
        # Suppress default access logs (too noisy for preview server)
        return


def _make_handler(preview_dir: Path):
    """Factory for creating handler instances bound to preview_dir."""
    def handler(*args, **kwargs):
        return PreviewHandler(preview_dir, *args, **kwargs)
    return handler


class PreviewServer:
    """Ephemeral preview server for draft HTML with auto-rebuild."""

    def __init__(
        self,
        input_path: Path,
        port: int = 8765,
        theme: str = "default",
        custom_css: Optional[str] = None,
        custom_css_path: Optional[Path] = None,
        template_override: Optional[Path] = None,
        entry_type: str = "daily",
        og_image: Optional[str] = None,
        skill_template: Optional[str] = None,
        skill_assets: Optional[List[Path]] = None,
        humanize: bool = False,
        tldr: bool = False,
        tags: bool = False,
        show_toc: bool = True,
        mermaid: bool = True,
        favicon: Optional[Path] = None,
        author: Optional[str] = None,
        site_title: Optional[str] = None,
    ):
        self.input_path = Path(input_path)
        self.port = port
        self.theme = theme
        self.custom_css = custom_css
        self.custom_css_path = custom_css_path
        self.template_override = template_override
        self.entry_type = entry_type
        self.og_image = og_image
        self.skill_template = skill_template
        self.skill_assets = skill_assets
        self.humanize = humanize
        self.tldr = tldr
        self.tags = tags
        self.show_toc = show_toc
        self.mermaid = mermaid
        self.favicon = favicon
        self.author = author
        self.site_title = site_title
        self.preview_dir: Optional[Path] = None
        self.httpd: Optional[socketserver.TCPServer] = None
        self._shutdown_event = threading.Event()

    def _build(self) -> Path:
        """Convert markdown to draft HTML in temp directory. Returns output path."""
        if self.preview_dir is None:
            raise RuntimeError("preview_dir not set")

        result = convert_file(
            input_path=self.input_path,
            output_dir=self.preview_dir,
            entry_type=self.entry_type,
            custom_css=self.custom_css,
            custom_css_path=self.custom_css_path,
            template_override=self.template_override,
            og_image=self.og_image,
            mermaid=self.mermaid,
            favicon=self.favicon,
            author=self.author,
            site_title=self.site_title,
            show_toc=self.show_toc,
            skill_template=self.skill_template,
            skill_assets=self.skill_assets,
            humanize=self.humanize,
            tldr=self.tldr,
            tags=self.tags,
        )

        # Inject noindex meta tag into the HTML
        html = result.output_path.read_text(encoding="utf-8")
        noindex_meta = '<meta name="robots" content="noindex, nofollow">\n'
        if "<head>" in html:
            html = html.replace("<head>", f"<head>\n{noindex_meta}")
        else:
            # Fallback: prepend before <html> or at top
            html = noindex_meta + html

        # Inject LiveReload script
        livereload_script = """
<script>
(function() {
    const ws = new WebSocket('ws://localhost:8766');
    ws.onmessage = function(event) {
        if (event.data === 'reload') location.reload();
    };
    ws.onclose = function() {
        setTimeout(function() { location.reload(); }, 2000);
    };
})();
</script>
"""
        if "</body>" in html:
            html = html.replace("</body>", f"{livereload_script}</body>")
        else:
            html = html + livereload_script + "\n"

        result.output_path.write_text(html, encoding="utf-8")
        return result.output_path

    def _serve(self):
        """Start blocking HTTP server in current thread."""
        assert self.preview_dir is not None
        handler = _make_handler(self.preview_dir)
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        self.httpd.serve_forever()

    def _setup_file_watcher(self):
        """Set up watchdog observer for input file changes."""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:  # pragma: no cover
            raise ImportError(
                "watchdog is required for --preview mode. "
                "Install it with: pip install watchdog"
            )

        class FileHandler(FileSystemEventHandler):
            def __init__(handler_self, server: "PreviewServer"):
                handler_self.server = server
                handler_self._last_rebuild = 0.0

            def on_modified(handler_self, event):
                if event.is_directory:
                    return
                path = Path(event.src_path)
                if path.name.startswith("."):
                    return
                if path.resolve() != handler_self.server.input_path.resolve():
                    return
                # Debounce: 500ms
                now = time.time()
                if now - handler_self._last_rebuild < 0.5:
                    return
                handler_self._last_rebuild = now
                if not path.exists():
                    return
                try:
                    handler_self.server._build()
                    handler_self.server._notify_reload()
                    print(f"  [preview] rebuilt: {path.name}")
                except Exception as exc:
                    print(f"  [preview] rebuild failed: {exc}")

        observer = Observer()
        watch_dir = self.input_path.parent
        observer.schedule(FileHandler(self), str(watch_dir), recursive=False)
        return observer

    def _setup_websocket_server(self):
        """Start a simple WebSocket-like notification server on port+1."""
        import socket

        def _ws_handler():
            addr = ("", self.port + 1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(addr)
                sock.listen(5)
                sock.settimeout(1.0)
                clients = []
                while not self._shutdown_event.is_set():
                    try:
                        conn, _ = sock.accept()
                        clients.append(conn)
                    except socket.timeout:
                        continue
                    except OSError:
                        break
                # Notify all connected clients to reload
                for client in clients:
                    try:
                        client.sendall(b'reload')
                        client.close()
                    except Exception:
                        pass
            finally:
                try:
                    sock.close()
                except Exception:
                    pass

        ws_thread = threading.Thread(target=_ws_handler, daemon=True)
        ws_thread.start()
        return ws_thread

    def _notify_reload(self):
        """Notify connected WebSocket clients to reload."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(("localhost", self.port + 1))
            sock.sendall(b'reload')
            sock.close()
        except Exception:
            pass

    def _setup_signal_handlers(self):
        """Set up SIGINT handler for graceful shutdown."""
        def _handle_sigint(signum, frame):
            print("\n  [preview] shutting down...")
            self._shutdown_event.set()
            if self.httpd:
                self.httpd.shutdown()
            raise KeyboardInterrupt

        signal.signal(signal.SIGINT, _handle_sigint)

    def start(self) -> None:
        """Start the preview server: build, serve, watch, cleanup on exit."""
        # Create temp directory
        self.preview_dir = Path(tempfile.mkdtemp(prefix="agent-publish-preview-"))

        # Build initial draft
        output_path = self._build()
        url = f"http://localhost:{self.port}"
        file_url = f"{url}/{output_path.name}"

        print(f"  [preview] draft built: {output_path.name}")
        print(f"  [preview] serving at {file_url}")
        print("  [preview] press Ctrl+C to stop and cleanup\n")

        # Start HTTP server in background thread
        server_thread = threading.Thread(target=self._serve, daemon=True)
        server_thread.start()

        # Start file watcher
        try:
            observer = self._setup_file_watcher()
            observer.start()
        except ImportError:
            print("  [preview] watchdog not installed — file changes won't auto-reload")
            observer = None

        # Start WebSocket notification server
        ws_thread = self._setup_websocket_server()

        # Set up signal handlers
        self._setup_signal_handlers()

        try:
            while not self._shutdown_event.is_set():
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            print("  [preview] cleaning up...")
            self._shutdown_event.set()
            if self.httpd:
                self.httpd.shutdown()
            server_thread.join(timeout=2)
            if observer:
                observer.stop()
                observer.join(timeout=2)
            ws_thread.join(timeout=2)
            # Delete temp directory
            if self.preview_dir and self.preview_dir.exists():
                shutil.rmtree(self.preview_dir, ignore_errors=True)
            print("  [preview] done.")


def preview_file(
    input_path: Path,
    port: int = 8765,
    theme: str = "default",
    custom_css: Optional[str] = None,
    custom_css_path: Optional[Path] = None,
    template_override: Optional[Path] = None,
    entry_type: str = "daily",
    og_image: Optional[str] = None,
    skill_template: Optional[str] = None,
    skill_assets: Optional[List[Path]] = None,
    humanize: bool = False,
    tldr: bool = False,
    tags: bool = False,
    show_toc: bool = True,
    mermaid: bool = True,
    favicon: Optional[Path] = None,
    author: Optional[str] = None,
    site_title: Optional[str] = None,
) -> None:
    """Convenience function to start a preview server for a single file."""
    server = PreviewServer(
        input_path=input_path,
        port=port,
        theme=theme,
        custom_css=custom_css,
        custom_css_path=custom_css_path,
        template_override=template_override,
        entry_type=entry_type,
        og_image=og_image,
        skill_template=skill_template,
        skill_assets=skill_assets,
        humanize=humanize,
        tldr=tldr,
        tags=tags,
        show_toc=show_toc,
        mermaid=mermaid,
        favicon=favicon,
        author=author,
        site_title=site_title,
    )
    server.start()
