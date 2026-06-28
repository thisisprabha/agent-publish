"""Run ruff check on extracted Python code blocks and emit code_report.json."""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Fence for Python code blocks
_PY_FENCE_RE = re.compile(r'^```python\s*\n(.*?)\n?^```', re.MULTILINE | re.DOTALL)


def _extract_python_blocks(md_content: str) -> list[str]:
    return [m.group(1).lstrip('\n') for m in _PY_FENCE_RE.finditer(md_content)]


def lint_code_blocks(
    md_content: str,
    source_name: str,
    output_dir: Path,
    *,
    ruff_path: str | None = None,
) -> dict[str, Any]:
    """Extract Python code blocks, run ruff check, write code_report.json.

    Returns the report dict (also written to code_report.json in output_dir).
    If ruff is unavailable, an error entry is written instead and no blocks
    are linted.
    """
    ruff = ruff_path or "ruff"
    blocks = _extract_python_blocks(md_content)

    report: dict[str, Any] = {
        "source": source_name,
        "blocks_total": len(blocks),
        "blocks_with_issues": 0,
        "total_violations": 0,
        "blocks": [],
    }

    if not blocks:
        _write_report(report, output_dir)
        return report

    # Check ruff availability
    try:
        subprocess.run(
            [ruff, "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        report["error"] = f"ruff not available ({sys.executable})"
        _write_report(report, output_dir)
        return report

    for idx, block in enumerate(blocks):
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            encoding="utf-8",
            delete=False,
        ) as tmp:
            tmp.write(block)
            tmp_path = tmp.name

        try:
            proc = subprocess.run(
                [ruff, "check", "--output-format", "json", tmp_path],
                capture_output=True,
                text=True,
            )
            violations: list[dict[str, Any]] = []
            if proc.returncode != 0 and proc.stdout.strip():
                try:
                    raw = json.loads(proc.stdout)
                    if isinstance(raw, list) and raw:
                        file_result = raw[0]
                        violations_raw = file_result.get("violations", [])
                        for v in violations_raw:
                            violations.append({
                                "code": v.get("code", ""),
                                "message": v.get("message", ""),
                                "line": v.get("location", {}).get("row", 0),
                                "column": v.get("location", {}).get("column", 0),
                            })
                except json.JSONDecodeError:
                    violations.append({
                        "code": "",
                        "message": proc.stdout.strip(),
                        "line": 0,
                        "column": 0,
                    })

            block_entry: dict[str, Any] = {
                "block_index": idx,
                "lines": block.count("\n") + 1,
                "violations": violations,
            }
            if proc.returncode == 0:
                block_entry["status"] = "clean"
            else:
                block_entry["status"] = "issues"
                report["blocks_with_issues"] += 1
                report["total_violations"] += len(violations)

            report["blocks"].append(block_entry)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    _write_report(report, output_dir)
    return report


def _write_report(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "code_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
