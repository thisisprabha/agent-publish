"""Tests for schema validation, exporters, and image optimization."""

import tempfile
from pathlib import Path

import pytest

# ---- AP-039: Schema tests ----


def test_extract_frontmatter():
    from agent_publish.schema import extract_frontmatter

    fm, body = extract_frontmatter(
        "---\ntitle: Hello\ntype: daily\n---\n\n# Content\n"
    )
    assert fm == {"title": "Hello", "type": "daily"}
    assert "Content" in body


def test_extract_frontmatter_none():
    from agent_publish.schema import extract_frontmatter

    fm, body = extract_frontmatter("# No frontmatter\n\nJust content.")
    assert fm is None
    assert body == "# No frontmatter\n\nJust content."


def test_extract_frontmatter_bad_yaml():
    from agent_publish.schema import extract_frontmatter

    fm, body = extract_frontmatter(
        "---\n[[bad yaml\n---\n\n# Content\n"
    )
    assert fm is None
    assert body == "---\n[[bad yaml\n---\n\n# Content\n"


def test_extract_frontmatter_not_dict():
    from agent_publish.schema import extract_frontmatter

    fm, body = extract_frontmatter(
        "---\n- item1\n- item2\n---\n\n# Content\n"
    )
    assert fm is None


def test_default_schema_validation():
    from agent_publish.schema import DEFAULT_SCHEMA, validate_frontmatter

    errors = validate_frontmatter(
        {"title": "Test", "type": "daily", "tags": ["a", "b"]}, DEFAULT_SCHEMA
    )
    assert errors == []


def test_default_schema_invalid_type():
    from agent_publish.schema import DEFAULT_SCHEMA, validate_frontmatter

    errors = validate_frontmatter(
        {"title": "Test", "type": "invalid"}, DEFAULT_SCHEMA
    )
    assert len(errors) == 1
    assert errors[0]["field"] == "type"
    assert "one of" in errors[0]["error"]
    assert errors[0]["severity"] == "warning"


def test_default_schema_int_type_check():
    from agent_publish.schema import validate_frontmatter

    schema = {"count": {"type": "int", "default": 0}}
    errors = validate_frontmatter({"count": "not-int"}, schema)
    assert len(errors) == 1
    assert "integer" in errors[0]["error"]


def test_default_schema_bool_type_check():
    from agent_publish.schema import validate_frontmatter

    schema = {"draft": {"type": "bool", "default": False}}
    errors = validate_frontmatter({"draft": "yes"}, schema)
    assert len(errors) == 1
    assert "boolean" in errors[0]["error"]


def test_default_schema_list_type_check():
    from agent_publish.schema import validate_frontmatter

    schema = {"tags": {"type": "list", "default": []}}
    errors = validate_frontmatter({"tags": "not-a-list"}, schema)
    assert len(errors) == 1
    assert "list" in errors[0]["error"]


def test_merge_schemas():
    from agent_publish.schema import DEFAULT_SCHEMA, merge_schemas

    user = {
        "title": {"required": True},
        "subtitle": {"type": "str", "default": ""},
    }
    merged = merge_schemas(DEFAULT_SCHEMA, user)
    assert merged["title"]["required"] is True
    assert merged["title"]["type"] == "str"
    assert "subtitle" in merged
    assert merged["subtitle"]["default"] == ""


def test_apply_defaults():
    from agent_publish.schema import DEFAULT_SCHEMA, apply_defaults

    fm = {"title": "Hello"}
    result = apply_defaults(fm, DEFAULT_SCHEMA)
    assert result["type"] == "daily"
    assert result["author"] == ""
    assert result["tags"] == []
    assert result["draft"] is False


def test_apply_defaults_no_override():
    from agent_publish.schema import DEFAULT_SCHEMA, apply_defaults

    fm = {"title": "Hello", "type": "research", "author": "Me"}
    result = apply_defaults(fm, DEFAULT_SCHEMA)
    assert result["type"] == "research"
    assert result["author"] == "Me"


# ---- AP-036: Exporters tests ----


def test_register_exporter():
    from agent_publish.exporters import _exporters, get_exporter, register_exporter

    def custom_exporter(html, path, meta):
        return path

    register_exporter("txt", custom_exporter)
    assert get_exporter("txt") is custom_exporter
    _exporters.pop("txt", None)


def test_list_exporters():
    from agent_publish.exporters import list_exporters

    exps = list_exporters()
    assert "html" in exps
    assert "epub" in exps
    assert "md" in exps
    assert "pdf" in exps


def test_export_html():
    from agent_publish.exporters import export_result

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.html"
        results = export_result("<html></html>", out, ["html"])
        assert "html" in results
        assert results["html"] == out


def test_export_markdown():
    from agent_publish.exporters import export_result

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        results = export_result(
            "<html></html>",
            out,
            ["md"],
            {"markdown": "# Hello\n\nWorld."},
        )
        assert "md" in results
        md_path = results["md"]
        assert md_path.suffix == ".md"
        assert md_path.read_text() == "# Hello\n\nWorld."


def test_export_epub():
    from agent_publish.exporters import export_result

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        html = (
            "<!DOCTYPE html><html><head><title>Test</title>"
            "<style>body{color:red}</style></head>"
            "<body><h1>Hello</h1><p>World</p></body></html>"
        )
        results = export_result(
            html,
            out,
            ["epub"],
            {"title": "My Book", "author": "Alice", "date": "2024-01-01"},
        )
        assert "epub" in results
        epub_path = results["epub"]
        assert epub_path.suffix == ".epub"
        assert epub_path.exists()

        import zipfile

        with zipfile.ZipFile(epub_path) as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "META-INF/container.xml" in names
            assert "OEBPS/content.opf" in names
            assert "OEBPS/content.xhtml" in names

            opf = zf.read("OEBPS/content.opf").decode("utf-8")
            assert "My Book" in opf
            assert "Alice" in opf

            xhtml = zf.read("OEBPS/content.xhtml").decode("utf-8")
            assert "<h1>Hello</h1>" in xhtml


def test_export_multiple_formats():
    from agent_publish.exporters import export_result

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        html = (
            "<!DOCTYPE html><html><head><title>Test</title>"
            "<style>body{color:red}</style></head>"
            "<body><h1>Hello</h1></body></html>"
        )
        results = export_result(
            html,
            out,
            ["epub", "md"],
            {"title": "Test", "markdown": "# Hello\n\nWorld."},
        )
        assert "epub" in results
        assert "md" in results
        assert results["epub"].suffix == ".epub"
        assert results["md"].suffix == ".md"


def test_export_unknown_format():
    from agent_publish.exporters import export_result

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        results = export_result("<html></html>", out, ["xyz"])
        assert "xyz" not in results


# ---- AP-037: Image optimizer tests ----


def test_optimize_images_empty_dir():
    from agent_publish.image_optimizer import optimize_images

    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp) / "images"
        img_dir.mkdir()
        report = optimize_images(img_dir)
        assert report["total_original"] == 0
        assert report["total_saved"] == 0
        assert report["report"] == []


def test_optimize_images_missing_dir():
    from agent_publish.image_optimizer import optimize_images

    report = optimize_images(Path("/nonexistent/images"))
    assert "error" in report


try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


@pytest.mark.skipif(not HAS_PIL, reason="Pillow not installed")
def test_optimize_jpeg():
    from agent_publish.image_optimizer import optimize_images

    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp) / "images"
        img_dir.mkdir()
        img_path = img_dir / "photo.jpg"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(str(img_path), format="JPEG", quality=95)
        img_path.stat().st_size

        report = optimize_images(img_dir)
        assert report["report"]
        assert any(
            "compressed" in entry["action"] or "error" in entry["action"]
            for entry in report["report"]
        )


@pytest.mark.skipif(not HAS_PIL, reason="Pillow not installed")
def test_optimize_png_to_webp():
    from agent_publish.image_optimizer import optimize_images

    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp) / "images"
        img_dir.mkdir()
        img_path = img_dir / "big.png"
        img = Image.new("RGB", (800, 600), color="blue")
        img.save(str(img_path), format="PNG")
        img_path.stat().st_size

        report = optimize_images(img_dir, max_png_bytes=1)
        assert report["report"]
        assert any(
            "converted to WebP" in entry["action"] for entry in report["report"]
        )


@pytest.mark.skipif(not HAS_PIL, reason="Pillow not installed")
def test_optimize_small_png():
    from agent_publish.image_optimizer import optimize_images

    with tempfile.TemporaryDirectory() as tmp:
        img_dir = Path(tmp) / "images"
        img_dir.mkdir()
        img_path = img_dir / "small.png"
        img = Image.new("RGB", (10, 10), color="green")
        img.save(str(img_path), format="PNG")

        report = optimize_images(img_dir, max_png_bytes=100_000_000)
        assert report["report"]
        assert any(
            "PNG optimized" in entry["action"] for entry in report["report"]
        )


def test_write_report():
    from agent_publish.image_optimizer import write_report

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        data = {"report": [], "total_original": 1000, "total_saved": 200}
        report_path = write_report(data, out)
        assert report_path.name == "images_report.json"
        assert report_path.exists()
        import json

        loaded = json.loads(report_path.read_text())
        assert loaded["total_original"] == 1000
        assert loaded["total_saved"] == 200
