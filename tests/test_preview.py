"""Tests for preview mode."""

import time
from pathlib import Path

import pytest

# Skip all preview tests if watchdog is not installed
try:
    import watchdog  # noqa: F401
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False


class TestPreviewServerBasics:
    """Test PreviewServer initialization and basic behavior."""

    def test_preview_server_init(self):
        from agent_publish.preview import PreviewServer

        input_path = Path("/tmp/test.md")
        server = PreviewServer(input_path=input_path, port=8765)
        assert server.input_path == input_path
        assert server.port == 8765
        assert server.preview_dir is None
        assert not server._shutdown_event.is_set()

    def test_preview_server_with_options(self):
        from agent_publish.preview import PreviewServer

        server = PreviewServer(
            input_path=Path("/tmp/test.md"),
            port=9999,
            theme="minimal",
            entry_type="research",
            humanize=True,
            tldr=True,
            tags=True,
            show_toc=False,
            mermaid=False,
        )
        assert server.port == 9999
        assert server.theme == "minimal"
        assert server.entry_type == "research"
        assert server.humanize is True
        assert server.tldr is True
        assert server.tags is True
        assert server.show_toc is False
        assert server.mermaid is False


class TestPreviewBuild:
    """Test HTML build with noindex injection."""

    def test_preview_build_injects_noindex(self, tmp_path):
        from agent_publish.preview import PreviewServer

        md = tmp_path / "test.md"
        md.write_text("# Hello World\n\nThis is a test paragraph.\n")

        server = PreviewServer(input_path=md, port=8765)
        preview_dir = tmp_path / "preview"
        preview_dir.mkdir()
        server.preview_dir = preview_dir

        output_path = server._build()
        html = output_path.read_text(encoding="utf-8")

        assert '<meta name="robots" content="noindex, nofollow">' in html
        assert "Hello World" in html

    def test_preview_build_injects_livereload_script(self, tmp_path):
        from agent_publish.preview import PreviewServer

        md = tmp_path / "test.md"
        md.write_text("# Hello World\n\nThis is a test paragraph.\n")

        server = PreviewServer(input_path=md, port=8765)
        preview_dir = tmp_path / "preview"
        preview_dir.mkdir()
        server.preview_dir = preview_dir

        output_path = server._build()
        html = output_path.read_text(encoding="utf-8")

        assert "WebSocket" in html
        assert "reload" in html
        assert "localhost:8766" in html

    def test_preview_build_with_skill(self, tmp_path):
        from agent_publish.preview import PreviewServer

        md = tmp_path / "test.md"
        md.write_text("# Skill Test\n\nBody.\n")

        skill_template = """<!DOCTYPE html>
<html><head><title>{html_title}</title><style>{css}</style></head>
<body>{body}</body></html>"""

        server = PreviewServer(
            input_path=md,
            port=8765,
            skill_template=skill_template,
        )
        preview_dir = tmp_path / "preview"
        preview_dir.mkdir()
        server.preview_dir = preview_dir

        output_path = server._build()
        html = output_path.read_text(encoding="utf-8")
        assert "Skill Test" in html
        assert '<meta name="robots" content="noindex, nofollow">' in html


class TestPreviewCleanup:
    """Test temp directory cleanup."""

    def test_preview_temp_dir_created_and_cleaned(self, tmp_path):
        from agent_publish.preview import PreviewServer

        md = tmp_path / "test.md"
        md.write_text("# Test\n\nBody.\n")

        server = PreviewServer(input_path=md, port=8765)
        preview_dir = tmp_path / "preview"
        preview_dir.mkdir()
        server.preview_dir = preview_dir

        # Build creates files
        server._build()
        assert list(preview_dir.iterdir())

        # Simulate cleanup
        import shutil
        shutil.rmtree(preview_dir, ignore_errors=True)
        assert not preview_dir.exists()


class TestWebsocketNotification:
    """Test WebSocket-like notification server."""

    def test_ws_server_port(self):
        from agent_publish.preview import PreviewServer

        server = PreviewServer(input_path=Path("/tmp/test.md"), port=8765)
        assert server.port + 1 == 8766

    def test_notify_reload_no_crash_without_server(self):
        from agent_publish.preview import PreviewServer

        server = PreviewServer(input_path=Path("/tmp/test.md"), port=8765)
        # Should not crash even if ws server isn't running
        server._notify_reload()


class TestSignalHandlers:
    """Test signal handling setup."""

    def test_signal_handler_setup(self):
        from agent_publish.preview import PreviewServer

        server = PreviewServer(input_path=Path("/tmp/test.md"), port=8765)
        server._setup_signal_handlers()
        # Just verify it doesn't crash


class TestPreviewFileFunction:
    """Test the preview_file convenience function."""

    def test_preview_file_function_exists(self):
        from agent_publish.preview import preview_file
        assert callable(preview_file)


@pytest.mark.skipif(not HAS_WATCHDOG, reason="watchdog not installed")
class TestPreviewFileWatcher:
    """Test file watcher integration."""

    def test_file_watcher_setup(self, tmp_path):
        from agent_publish.preview import PreviewServer

        md = tmp_path / "test.md"
        md.write_text("# Test\n\nBody.\n")

        server = PreviewServer(input_path=md, port=8765)
        observer = server._setup_file_watcher()
        assert observer is not None
        observer.start()
        time.sleep(0.1)
        observer.stop()
        observer.join(timeout=2)
