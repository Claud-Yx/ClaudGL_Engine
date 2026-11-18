"""Write the static font files that build() embeds into _build/fonts.

Usage: python -I _engine/make_fonts.py      (from Docs/Handouts, with the handout venv)

Chrome prints a variable font (one file with a weight axis) as Type3 glyphs,
and Acrobat redraws Type3 text on every scroll, so a handout set in a variable
font crawls in Acrobat. This script pins each needed weight of the variable
body font into its own static file, and copies the static code font so that a
"current user only" install does not matter either.

Needs fonttools in the venv. Run it once per PC; _build/ is not in git.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

OUT_DIR = Path(__file__).resolve().parent.parent / "_build" / "fonts"

FONT_DIRS = [
    Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts",
]

# Variable source -> weights used by base.css. Output: <Family>-<weight>.ttf
VARIABLE = {
    "Noto Sans KR": ("NotoSansKR-VF.ttf", [400, 600, 700]),
}

# Static files copied as they are. Output: <Family>-<weight>.ttf
STATIC = {
    "Pragmasevka": {400: "pragmasevka-regular.ttf", 700: "pragmasevka-bold.ttf"},
}


STYLE = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
         600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}


def rename(font: TTFont, family: str, weight: int) -> None:
    """Name a pinned instance by its weight (it keeps the default instance's names otherwise)."""
    style = STYLE[weight]
    ps = f"{family.replace(' ', '')}-{style}"
    table = font["name"]
    table.names = [n for n in table.names if n.nameID not in (1, 2, 3, 4, 6, 16, 17, 25)]
    for name_id, text in ((1, family), (2, style), (3, ps), (4, f"{family} {style}"), (6, ps)):
        table.setName(text, name_id, 3, 1, 0x409)


def find(name: str) -> Path:
    for folder in FONT_DIRS:
        path = folder / name
        if path.exists():
            return path
    raise SystemExit(f"{name} is not installed (looked in {', '.join(map(str, FONT_DIRS))})")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for family, (source, weights) in VARIABLE.items():
        src = find(source)
        for weight in weights:
            out = OUT_DIR / f"{family}-{weight}.ttf"
            font = instancer.instantiateVariableFont(TTFont(src), {"wght": weight}, updateFontNames=False)
            font["OS/2"].usWeightClass = weight
            rename(font, family, weight)
            font.save(out)
            print(f"wrote {out.name} ({out.stat().st_size // 1024} KB)")

    for family, files in STATIC.items():
        for weight, name in files.items():
            out = OUT_DIR / f"{family}-{weight}.ttf"
            shutil.copyfile(find(name), out)
            print(f"wrote {out.name} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
