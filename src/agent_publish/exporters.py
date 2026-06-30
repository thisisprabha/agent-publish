"""Multi-format export plugin system for agent-publish.

Hook-based architecture: register_exporter(ext, callable).
Built-in: html, md, epub, pdf.
"""

import re
import zipfile
from pathlib import Path
from typing import Callable, Dict, List, Optional

_exporters: Dict[str, Callable] = {}


def register_exporter(
    ext: str, export_fn: Callable[[str, Path, dict], Path]
) -> None:
    """Register an exporter for a file format.

    Args:
        ext: File extension (e.g. 'epub', 'pdf')
        export_fn: (html_content, output_path, metadata) -> exported_path
    """
    _exporters[ext.strip().lower()] = export_fn


def get_exporter(ext: str) -> Optional[Callable]:
    return _exporters.get(ext.strip().lower())


def list_exporters() -> List[str]:
    return sorted(_exporters.keys())


# ---- Built-in exporters ----


def _export_html(html_content: str, output_path: Path, metadata: dict) -> Path:
    return output_path


def _export_markdown(html_content: str, output_path: Path, metadata: dict) -> Path:
    md_content = metadata.get("markdown", "")
    out = output_path.with_suffix(".md")
    out.write_text(md_content, encoding="utf-8")
    return out


def _export_epub(html_content: str, output_path: Path, metadata: dict) -> Path:
    title = metadata.get("title", "Untitled")
    title_esc = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    author = metadata.get("author", "agent-publish")
    date = metadata.get("date", "")

    epub_path = output_path.with_suffix(".epub")

    container_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles>\n'
        '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
        '  </rootfiles>\n'
        "</container>"
    )

    opf = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">\n'
        f'  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f"    <dc:title>{title_esc}</dc:title>\n"
        f"    <dc:creator>{author}</dc:creator>\n"
        f"    <dc:date>{date}</dc:date>\n"
        f"    <dc:language>en</dc:language>\n"
        f"    <meta property=\"dcterms:modified\">{date}</meta>\n"
        f"  </metadata>\n"
        '  <manifest>\n'
        '    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>\n'
        '  </manifest>\n'
        '  <spine>\n'
        '    <itemref idref="content"/>\n'
        '  </spine>\n'
        "</package>"
    )

    css_match = re.search(r"<style>(.*?)</style>", html_content, re.DOTALL)
    styles = css_match.group(1) if css_match else ""

    body_match = re.search(r"<body[^>]*>(.*?)</body>", html_content, re.DOTALL)
    body = body_match.group(1) if body_match else html_content
    body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.DOTALL)

    xhtml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
        f"<head><title>{title_esc}</title>"
        f'<style type="text/css">{styles}</style>'
        "</head>\n"
        f"<body>{body}</body>\n"
        "</html>"
    )

    mimetype = "application/epub+zip"

    with zipfile.ZipFile(epub_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/content.xhtml", xhtml)

    return epub_path


def _export_pdf(html_content: str, output_path: Path, metadata: dict) -> Path:
    try:
        from weasyprint import HTML

        pdf_path = output_path.with_suffix(".pdf")
        HTML(string=html_content).write_pdf(str(pdf_path))
        return pdf_path
    except ImportError:
        raise RuntimeError(
            "WeasyPrint is not installed. Install it with: pip install weasyprint"
        )


register_exporter("html", _export_html)
register_exporter("md", _export_markdown)
register_exporter("epub", _export_epub)
register_exporter("pdf", _export_pdf)


def export_result(
    html_content: str,
    output_path: Path,
    formats: List[str],
    metadata: Optional[dict] = None,
) -> Dict[str, Optional[Path]]:
    """Export HTML to one or more formats.

    Args:
        html_content: Full HTML document string
        output_path: Base output path (suffix changes per format)
        formats: List of format extensions (e.g. ['epub', 'pdf'])
        metadata: Dict with title, author, date, markdown content

    Returns:
        Dict mapping format extension to exported Path (or None on failure)
    """
    meta = metadata or {}
    results: Dict[str, Optional[Path]] = {}
    for fmt in formats:
        fmt = fmt.strip().lower()
        exporter = _exporters.get(fmt)
        if exporter is None:
            continue
        try:
            exported = exporter(html_content, output_path, meta)
            results[fmt] = exported
        except Exception:
            results[fmt] = None
    return results
