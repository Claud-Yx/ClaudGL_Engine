"""Inspection images for a handout PDF.

Usage:
    python sheet.py <pdf> <out_dir> <prefix>              contact sheets (6 pages each)
    python sheet.py <pdf> <out_dir> <prefix> --page N     one page, enlarged

Contact sheets catch layout problems (stranded headings, big gaps, broken
blocks); the single-page mode is for reading text, code and table cells.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
from PIL import Image

PER_SHEET = 6
COLS = 3
THUMB_DPI = 58
PAGE_DPI = 120
GAP = 14
BACKGROUND = (120, 124, 132)


def page_image(page, dpi: int) -> Image.Image:
    pix = page.get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def contact_sheets(doc, out_dir: Path, prefix: str) -> list[Path]:
    written = []
    for first in range(0, doc.page_count, PER_SHEET):
        thumbs = [page_image(doc[i], THUMB_DPI) for i in range(first, min(first + PER_SHEET, doc.page_count))]
        w, h = thumbs[0].size
        rows = (len(thumbs) + COLS - 1) // COLS
        sheet = Image.new("RGB", (COLS * w + (COLS + 1) * GAP, rows * h + (rows + 1) * GAP), BACKGROUND)
        for i, thumb in enumerate(thumbs):
            x = GAP + (i % COLS) * (w + GAP)
            y = GAP + (i // COLS) * (h + GAP)
            sheet.paste(thumb, (x, y))
        path = out_dir / f"{prefix}_sheet_{first + 1:02d}-{first + len(thumbs):02d}.png"
        sheet.save(path)
        written.append(path)
    return written


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    pdf_path, out_dir, prefix = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    out_dir.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf_path) as doc:
        if "--page" in sys.argv:
            number = int(sys.argv[sys.argv.index("--page") + 1])
            path = out_dir / f"{prefix}_p{number:02d}.png"
            page_image(doc[number - 1], PAGE_DPI).save(path)
            print(path)
            return
        print(f"pages: {doc.page_count}")
        for path in contact_sheets(doc, out_dir, prefix):
            print(path)


if __name__ == "__main__":
    main()
