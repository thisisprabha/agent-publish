"""Image optimization pipeline for agent-publish.

When --optimize-images is passed, compress JPEG/PNG in place, convert
oversized PNG to WebP, strip EXIF. Zero dependency: pure Python PIL or skip.
Generates images_report.json with before/after sizes.
"""

import json
from pathlib import Path
from typing import Dict, List


def optimize_images(
    images_dir: Path,
    quality: int = 85,
    max_png_bytes: int = 500_000,
    webp: bool = True,
    strip_exif: bool = True,
) -> Dict:
    """Optimize images in a directory using PIL if available.

    Args:
        images_dir: Directory containing images
        quality: JPEG quality 1-100
        max_png_bytes: PNGs above this size get converted to WebP
        webp: Whether to convert large PNGs to WebP
        strip_exif: Whether to strip EXIF metadata

    Returns:
        Dict with report list, total_original, total_after, total_saved
    """
    report: List[Dict] = []
    total_original = 0
    total_after = 0

    try:
        from PIL import Image

        has_pil = True
    except ImportError:
        has_pil = False

    if not images_dir.exists():
        return {
            "report": [],
            "total_original": 0,
            "total_saved": 0,
            "error": f"Images directory not found: {images_dir}",
        }

    image_files = sorted(
        f for f in images_dir.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png")
    )

    if not image_files:
        return {"report": [], "total_original": 0, "total_saved": 0}

    for img_path in image_files:
        original_size = img_path.stat().st_size
        total_original += original_size
        ext = img_path.suffix.lower()

        if not has_pil:
            total_after += original_size
            report.append(
                {
                    "file": img_path.name,
                    "original_bytes": original_size,
                    "after_bytes": original_size,
                    "saved_bytes": 0,
                    "action": "skipped — Pillow not installed",
                }
            )
            continue

        try:
            img = Image.open(img_path)

            if ext in (".jpg", ".jpeg"):
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                exif = img.info.get("exif", b"") if not strip_exif else b""
                img.save(
                    str(img_path),
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                    exif=exif if exif else None,
                )
                action = f"compressed JPEG (quality={quality})"
                if strip_exif:
                    action += " — stripped EXIF"
                after_path = img_path

            elif ext == ".png":
                if webp and original_size > max_png_bytes:
                    webp_path = img_path.with_suffix(".webp")
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")
                    img.save(str(webp_path), format="WEBP", quality=quality)

                    after_size = webp_path.stat().st_size
                    if after_size < original_size:
                        img_path.unlink()
                        after_path = webp_path
                        action = f"converted to WebP (quality={quality})"
                    else:
                        webp_path.unlink()
                        _optimize_png(img, img_path)
                        after_path = img_path
                        action = "PNG optimized (quantized)"
                else:
                    _optimize_png(img, img_path)
                    after_path = img_path
                    action = "PNG optimized (quantized)"

            after_size = after_path.stat().st_size
            total_after += after_size
            saved = original_size - after_size
            report.append(
                {
                    "file": (
                        img_path.name
                        if after_path.suffix == img_path.suffix
                        else f"{img_path.stem}.webp"
                    ),
                    "original_bytes": original_size,
                    "after_bytes": after_size,
                    "saved_bytes": saved,
                    "saved_pct": round(saved / original_size * 100, 1)
                    if original_size
                    else 0,
                    "action": action,
                }
            )

            img.close()

        except Exception as e:
            total_after += original_size
            report.append(
                {
                    "file": img_path.name,
                    "original_bytes": original_size,
                    "after_bytes": original_size,
                    "saved_bytes": 0,
                    "action": f"error: {e}",
                }
            )

    total_saved = total_original - total_after
    return {
        "report": report,
        "total_original": total_original,
        "total_after": total_after,
        "total_saved": total_saved,
        "total_saved_pct": round(total_saved / total_original * 100, 1)
        if total_original
        else 0,
    }


def _optimize_png(img, output_path: Path):
    """Quantize PNG to 256 colors for size reduction."""
    try:
        if img.mode in ("RGBA", "RGB"):
            img_q = img.quantize(colors=256, method=0)
            img_q.save(str(output_path), format="PNG", optimize=True)
        else:
            img.save(str(output_path), format="PNG", optimize=True)
    except Exception:
        img.save(str(output_path), format="PNG", optimize=True)


def write_report(report_data: Dict, output_dir: Path) -> Path:
    report_path = output_dir / "images_report.json"
    report_path.write_text(
        json.dumps(report_data, indent=2, default=str), encoding="utf-8"
    )
    return report_path
