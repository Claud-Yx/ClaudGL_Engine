"""Render a handout HTML file to an A4 PDF with headless Chrome or Edge.

Usage: python render.py <in.html> <out.pdf>

No extra packages are needed: the installed browser does the printing. Page
footers and page numbers come from CSS @page margin boxes (Chromium 131+).
Set HANDOUT_BROWSER to force a specific browser executable.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_browser() -> str:
    forced = os.environ.get("HANDOUT_BROWSER")
    if forced:
        return forced
    for path in CANDIDATES:
        if Path(path).exists():
            return path
    raise SystemExit("No Chrome or Edge found. Set HANDOUT_BROWSER to the browser path.")


def render(html_path, pdf_path) -> int:
    """Print html_path to pdf_path and return the page count (-1 without PyMuPDF).

    PDF names carry a version (_v<N>). If pdf_path is locked, that version is
    open in a viewer, which means it was already handed over: bump the version
    in curriculum.py instead of overwriting it.
    """
    html_path = Path(html_path).resolve()
    target = Path(pdf_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = target.with_name(target.stem + "_tmp.pdf")
    if pdf_path.exists():
        pdf_path.unlink()

    # A throwaway profile keeps this run apart from the browser the user has open.
    with tempfile.TemporaryDirectory(prefix="handout-profile-", ignore_cleanup_errors=True) as profile:
        cmd = [
            find_browser(),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--disable-extensions",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            "--virtual-time-budget=4000",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if not pdf_path.exists():
        raise SystemExit(f"PDF was not written.\n{result.stderr[-2000:]}")

    try:
        os.replace(pdf_path, target)
    except PermissionError:
        pdf_path.unlink(missing_ok=True)
        raise SystemExit(
            f"{target.name} is open in a viewer. If this version was already handed over, "
            "bump its version in curriculum.py and build again; otherwise close the viewer."
        )

    try:
        import pymupdf

        with pymupdf.open(target) as doc:
            return doc.page_count
    except ImportError:
        return -1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(f"wrote {sys.argv[2]} ({render(sys.argv[1], sys.argv[2])} pages)")
