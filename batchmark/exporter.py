"""Export timing reports to files."""

import os
from pathlib import Path
from typing import List, Optional

from batchmark.report import render_report
from batchmark.summary import Summary


SUPPORTED_FORMATS = ("json", "csv", "text")


def export_report(
    summary: Summary,
    results: list,
    output_path: str,
    fmt: Optional[str] = None,
) -> str:
    """Write a rendered report to a file.

    Args:
        summary: Summary object from summarize().
        results: List of TimingResult objects.
        output_path: Destination file path.
        fmt: Format override. If None, inferred from file extension.

    Returns:
        Absolute path of the written file.

    Raises:
        ValueError: If the format is not supported.
        OSError: If the file cannot be written.
    """
    if fmt is None:
        fmt = _infer_format(output_path)

    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from {SUPPORTED_FORMATS}.")

    content = render_report(summary, results, fmt=fmt)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return str(path.resolve())


def export_reports(
    summary: Summary,
    results: list,
    output_dir: str,
) -> List[str]:
    """Write reports in all supported formats to a directory.

    Args:
        summary: Summary object from summarize().
        results: List of TimingResult objects.
        output_dir: Directory where report files will be written.

    Returns:
        List of absolute paths for each written file.
    """
    written = []
    for fmt in SUPPORTED_FORMATS:
        ext = "txt" if fmt == "text" else fmt
        output_path = os.path.join(output_dir, f"report.{ext}")
        written.append(export_report(summary, results, output_path, fmt=fmt))
    return written


def _infer_format(path: str) -> str:
    """Infer report format from file extension."""
    ext = os.path.splitext(path)[-1].lstrip(".").lower()
    mapping = {
        "json": "json",
        "csv": "csv",
        "txt": "text",
        "text": "text",
    }
    return mapping.get(ext, "text")
