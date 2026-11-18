"""Build engine for ClaudGL Engine handouts (A4 PDF).

Content files import everything from here, compose HTML fragments with the
helpers below, and call build(). Text arguments are escaped automatically and
accept a small inline markup:

    `code`     -> inline code
    **bold**   -> bold
    ==mark==   -> accent-colored emphasis

Wrap a string in Raw(...) to pass HTML through untouched. Every helper returns
Raw, so helpers can be nested freely.
"""
from __future__ import annotations

import base64
import html
import math
import re
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

ENGINE_DIR = Path(__file__).resolve().parent

# A cp949 console cannot encode every character a build may print (e.g. a dash inside `issues`).
# Replace what it cannot show instead of letting the print kill the build.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# Limits used by the automatic checks reported from build().
MAX_CODE_COLS = 104   # characters that fit in a full-width code block (about 110 do)
MAX_CODE_LINES = 28   # longer blocks usually mean a complete solution leaked in

_HANGUL = re.compile(r"[ㄱ-ㆎ가-힣]")
_issues: list[str] = []
_stats = {"code_blocks": 0, "diagrams": 0, "tables": 0}


class Raw(str):
    """Marks a string as ready-made HTML (never escaped again)."""


def esc(text: str) -> str:
    return html.escape(str(text), quote=False)


_INLINE = [
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*(.+?)\*\*"), r"<b>\1</b>"),
    (re.compile(r"==(.+?)=="), r'<em class="hl">\1</em>'),
]


def T(text) -> Raw:
    """Escape plain text and apply the inline markup. Raw passes through."""
    if isinstance(text, Raw):
        return text
    out = esc(text)
    for pattern, repl in _INLINE:
        out = pattern.sub(repl, out)
    return Raw(out)


def J(*parts) -> Raw:
    """Join blocks (strings or lists of strings) into one Raw fragment."""
    flat: list[str] = []
    for part in parts:
        if part is None:
            continue
        if isinstance(part, (list, tuple)):
            flat.append(J(*part))
        else:
            flat.append(T(part) if not isinstance(part, Raw) else part)
    return Raw("\n".join(flat))


# --------------------------------------------------------------------------
# text blocks
# --------------------------------------------------------------------------

def p(*texts, cls: str = "") -> Raw:
    attr = f' class="{cls}"' if cls else ""
    return Raw("".join(f"<p{attr}>{T(t)}</p>" for t in texts))


def ul(items) -> Raw:
    return Raw("<ul>" + "".join(f"<li>{T(i)}</li>" for i in items) + "</ul>")


def ol(items) -> Raw:
    return Raw("<ol>" + "".join(f"<li>{T(i)}</li>" for i in items) + "</ol>")


def h3(num: str, title) -> Raw:
    n = f'<span class="n">{esc(num)}</span>' if num else ""
    return Raw(f"<h3>{n}{T(title)}</h3>")


def h4(title) -> Raw:
    return Raw(f"<h4>{T(title)}</h4>")


def st(kind: str, label: str | None = None) -> Raw:
    """Status chip. kind: done | wip | todo | opt."""
    default = {"done": "완료", "wip": "진행 중", "todo": "예정", "opt": "선택"}
    return Raw(f'<span class="st {kind}">{esc(label or default[kind])}</span>')


# --------------------------------------------------------------------------
# page structure
# --------------------------------------------------------------------------

def cover(eyebrow, title, heading, sub, info, note=None, toc=None) -> Raw:
    """Cover page.

    title   -- big display line (identifier or project name); Raw may contain
               <span class="ac"> for the accent color
    heading -- Korean title under it
    info    -- [(label, value), ...]
    note    -- (title, body) rendered as the dark box
    toc     -- [chapter title, ...]
    """
    rows = "".join(f'<tr><td class="k">{T(k)}</td><td>{T(v)}</td></tr>' for k, v in info)
    parts = [
        '<section class="cover">',
        '<div class="bar"></div>',
        f'<div class="eyebrow">{T(eyebrow)}</div>',
        f"<h1>{T(title)}</h1>",
        f"<h2>{T(heading)}</h2>",
        f'<p class="sub">{T(sub)}</p>',
        f'<table class="info">{rows}</table>',
    ]
    if note:
        parts.append(box("dark", note[0], note[1]))
    if toc:
        half = (len(toc) + 1) // 2
        cols = []
        for chunk, start in ((toc[:half], 1), (toc[half:], half + 1)):
            rows_html = "".join(
                f'<div class="row"><span class="n">{i}</span><span>{T(t)}</span></div>'
                for i, t in enumerate(chunk, start=start)
            )
            cols.append(f'<div class="col">{rows_html}</div>')
        parts.append(f'<div class="toc">{"".join(cols)}</div>')
    parts.append("</section>")
    return Raw("\n".join(parts))


def chapter(n, title, body, lead=None, pb: bool = False, side=None) -> Raw:
    """Chapter. The heading, lead and first block are kept on one page.

    body -- list of blocks; pb=True starts the chapter on a new page.
    """
    blocks = list(body) if isinstance(body, (list, tuple)) else [body]
    blocks = [b for b in blocks if b]
    side_html = f'<span class="side">{T(side)}</span>' if side else ""
    head = (
        f'<div class="ch-head"><span class="num">{esc(n)}</span>'
        f'<span class="title">{T(title)}</span>{side_html}</div>'
    )
    lead_html = f'<p class="lead">{T(lead)}</p>' if lead else ""
    first = J(blocks[0]) if blocks else ""
    rest = J(blocks[1:]) if len(blocks) > 1 else ""
    cls = ' class="pb"' if pb else ""
    return Raw(f'<section{cls}><div class="keep">{head}{lead_html}{first}</div>{rest}</section>')


def keep(*blocks) -> Raw:
    """Keep blocks together on one page (e.g. a heading with its table)."""
    return Raw(f'<div class="keep">{J(*blocks)}</div>')


def pagebreak() -> Raw:
    return Raw('<div class="pb"></div>')


# --------------------------------------------------------------------------
# tables and boxes
# --------------------------------------------------------------------------

class Group(str):
    """A full-width group heading row inside table() rows."""


def table(cols, header, rows, cell_cls=None, sum_row=None, compact: bool = False) -> Raw:
    """Table with a dark header.

    rows may contain Group("label") entries; each renders as a heading row
    spanning all columns.

    cols     -- column widths in percent
    cell_cls -- per-column td class: lab | num | r | c | "" (also applied to th
                for r/c so headers line up)
    sum_row  -- optional closing row rendered as a total line
    compact  -- tighter rows for long lists
    """
    _stats["tables"] += 1
    cell_cls = cell_cls or [""] * len(cols)

    def th(i, h):
        cls = cell_cls[i] if cell_cls[i] in ("r", "c") else ""
        attr = f' class="{cls}"' if cls else ""
        return f'<th{attr} style="width:{cols[i]}%">{T(h)}</th>'

    def tr(cells, cls=""):
        tds = "".join(
            f'<td class="{cell_cls[i]}">{T(c)}</td>' if cell_cls[i] else f"<td>{T(c)}</td>"
            for i, c in enumerate(cells)
        )
        attr = f' class="{cls}"' if cls else ""
        return f"<tr{attr}>{tds}</tr>"

    head = "".join(th(i, h) for i, h in enumerate(header))
    body = "".join(
        f'<tr class="grp"><td colspan="{len(cols)}">{T(r)}</td></tr>' if isinstance(r, Group) else tr(r)
        for r in rows
    )
    if sum_row:
        body += tr(sum_row, "sum")
    cls = "t compact" if compact else "t"
    return Raw(f'<table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')


BOX_TITLES = {
    "point": "핵심",
    "why": "왜 이렇게 하는가",
    "ue": "UE5에서는",
    "cs": "CS 메모",
    "api": "다른 API에서는",
    "warn": "함정",
    "hint": "힌트",
    "decide": "결정할 것",
    "dark": "읽는 법",
    "ex": "예시",
}


def box(kind: str, title, body) -> Raw:
    """Callout box. kind: point | why | ue | cs | api | warn | hint | decide | dark | ex.

    "ex" is a worked example: one concrete case with real numbers or a real
    call, shown apart from the lesson's own code. body may be a list of blocks.
    """
    label = T(title) if title else BOX_TITLES[kind]
    inner = J(body) if isinstance(body, (list, tuple)) else T(body)
    if not inner.lstrip().startswith(("<p", "<ul", "<ol", "<div", "<table")):
        inner = f"<p>{inner}</p>"
    return Raw(f'<div class="box {kind}"><div class="bt">{label}</div>{inner}</div>')


def cards(items, cols: int = 2) -> Raw:
    """Comparison cards. items: [(title, subtitle, body, footer), ...]."""
    out = []
    for title, sub, body, foot in items:
        foot_html = f'<div class="cf">{T(foot)}</div>' if foot else ""
        out.append(
            f'<div class="card"><div class="ct">{T(title)}</div><div class="cs">{T(sub)}</div>'
            f'<div class="cb">{T(body)}</div>{foot_html}</div>'
        )
    style = f"grid-template-columns:repeat({cols},1fr)"
    return Raw(f'<div class="cards" style="{style}">{"".join(out)}</div>')


def ox(good, bad) -> Raw:
    """Right/wrong pair. Each side: (main, description)."""
    return Raw(
        '<div class="ox">'
        f'<div class="o"><span class="mk">○</span><div><div class="m">{T(good[0])}</div>'
        f'<div class="d">{T(good[1])}</div></div></div>'
        f'<div class="x"><span class="mk">×</span><div><div class="m">{T(bad[0])}</div>'
        f'<div class="d">{T(bad[1])}</div></div></div>'
        "</div>"
    )


# --------------------------------------------------------------------------
# code
# --------------------------------------------------------------------------

CODE_TAGS = {
    "sketch": "선언 스케치",
    "usage": "사용 예",
    "syntax": "문법",
    "bad": "안티패턴",
    "now": "현재 코드",
}


def code(src: str, lang: str = "cpp", title=None, tag: str | None = None, hl=None, start: int | None = None) -> Raw:
    """Syntax-highlighted code block.

    tag   -- sketch | usage | syntax | bad | now (shown top right)
    start -- real line number of the first line; shows a line-number gutter.
             Use it when quoting repository code so the text can say file:line.
    hl    -- lines to highlight: real line numbers when start is given,
             otherwise 1-based positions inside src

    Mentor rule: handouts never carry complete implementations. Use code() for
    declarations, call-site examples, 1-3 line API syntax and anti-patterns.
    Comments inside code must be English.
    """
    _stats["code_blocks"] += 1
    src = src.strip("\n")
    lines = src.split("\n")
    name = title or f"code block #{_stats['code_blocks']}"
    if _HANGUL.search(src):
        _issues.append(f"hangul in code: {name}")
    longest = max(len(line) for line in lines) + (7 if start else 0)  # the gutter takes 7 columns
    if longest > MAX_CODE_COLS:
        _issues.append(f"code line too long ({longest} cols): {name}")
    # Quoted repository code (tag "now") is the user's own work, not a leaked solution.
    if len(lines) > MAX_CODE_LINES and tag != "now":
        _issues.append(f"code block too long ({len(lines)} lines, complete solution?): {name}")

    inner = highlight(src, get_lexer_by_name(lang), HtmlFormatter(nowrap=True)).rstrip("\n")
    if hl or start:
        # Highlighted lines are block-level spans, so they end the line themselves
        # and must not be followed by a newline character.
        marks = set(hl or [])
        parts = []
        for i, line in enumerate(inner.split("\n"), start=1):
            number = start + i - 1 if start else i
            gutter = f'<span class="lno">{number}</span>' if start else ""
            if number in marks:
                parts.append(f'<span class="hll">{gutter}{line or " "}</span>')
            else:
                parts.append(f"{gutter}{line}\n")
        inner = "".join(parts).rstrip("\n")

    head = ""
    if title or tag:
        tag_html = ""
        if tag:
            cls = "tag bad" if tag == "bad" else "tag"
            tag_html = f'<span class="{cls}">{esc(CODE_TAGS.get(tag, tag))}</span>'
        head = f'<div class="chd"><span class="file">{esc(title or "")}</span>{tag_html}</div>'
    return Raw(f'<div class="code">{head}<pre>{inner}</pre></div>')


def console(text, title: str = "출력") -> Raw:
    """Dark block for program output. Raw text may use span classes dim/warn/err/ok."""
    body = text if isinstance(text, Raw) else esc(text.strip("\n"))
    return Raw(f'<div class="console"><div class="chd">{esc(title)}</div><pre>{body}</pre></div>')


def tree(text: str) -> Raw:
    """File tree. Mark lines with a trailing ' +' (new file) or ' #note'."""
    out = []
    for line in text.strip("\n").split("\n"):
        note = ""
        if "  #" in line:
            line, note = line.split("  #", 1)
            note = f'<span class="note">  {esc(note.strip())}</span>'
        if line.rstrip().endswith(" +"):
            out.append(f'<span class="new">{esc(line.rstrip()[:-2])}</span>{note}')
        else:
            out.append(f"{esc(line)}{note}")
    return Raw(f'<div class="tree"><pre>{chr(10).join(out)}</pre></div>')


# --------------------------------------------------------------------------
# diagrams
# --------------------------------------------------------------------------

def _cell(item, cls: str) -> str:
    """item: 'title' | (title, sub) | (title, sub, kind)."""
    if isinstance(item, str):
        item = (item,)
    title = item[0]
    sub = item[1] if len(item) > 1 else None
    kind = item[2] if len(item) > 2 else ""
    sub_html = f'<div class="s">{T(sub)}</div>' if sub else ""
    return f'<div class="{cls} {kind}"><div class="t">{T(title)}</div>{sub_html}</div>'


def flow(items, caption=None) -> Raw:
    """Left-to-right pipeline: chip -> chip -> chip. kind: accent | dark."""
    _stats["diagrams"] += 1
    chips = [_cell(i, "chip") for i in items]
    body = '<span class="arrow">→</span>'.join(chips)
    cap = f'<p class="cap">{T(caption)}</p>' if caption else ""
    return Raw(f'<div class="keep"><div class="flow">{body}</div>{cap}</div>')


def layers(rows, caption=None) -> Raw:
    """Stacked architecture layers, top to bottom.

    rows: [(layer name, [cell, ...]), ...]; cell kind: accent | dark | ghost.
    """
    _stats["diagrams"] += 1
    out = []
    for name, cells in rows:
        cells_html = "".join(_cell(c, "cell") for c in cells)
        out.append(f'<div class="layer"><div class="lname">{T(name)}</div>{cells_html}</div>')
    cap = f'<p class="cap">{T(caption)}</p>' if caption else ""
    return Raw(f'<div class="keep"><div class="layers">{"".join(out)}</div>{cap}</div>')


def iface(name: str, members, stereotype: str = "interface", note=None) -> Raw:
    """Small class card: name, member signatures, optional note.

    Put several inside cards-like grids with grid(...).
    """
    body = "<br>".join(esc(m) for m in members)
    note_html = f'<div class="in">{T(note)}</div>' if note else ""
    return Raw(
        f'<div class="iface"><div class="ih"><div class="st0">{esc(stereotype.upper())}</div>'
        f'<div class="nm">{esc(name)}</div></div><div class="im">{body}</div>{note_html}</div>'
    )


def grid(items, cols: int = 2) -> Raw:
    """Plain grid for iface() cards or other blocks."""
    style = f"grid-template-columns:repeat({cols},1fr)"
    return Raw(f'<div class="cards" style="{style}">{"".join(items)}</div>')


def roadmap(rows, total: float, caption=None) -> Raw:
    """Horizontal bars. rows: [(part label, title, start, length, value text, kind)].

    start/length share the unit of total (e.g. hours); kind: '' | accent | ghost.
    """
    _stats["diagrams"] += 1
    out = []
    for part, title, start, length, value, kind in rows:
        left = 100.0 * start / total
        width = max(100.0 * length / total, 1.0)
        out.append(
            f'<div class="rr"><div class="rl"><div class="p">{T(part)}</div><div class="t">{T(title)}</div></div>'
            f'<div class="track"><div class="bar {kind}" style="left:{left:.2f}%;width:{width:.2f}%"></div></div>'
            f'<div class="rv">{T(value)}</div></div>'
        )
    cap = f'<p class="cap">{T(caption)}</p>' if caption else ""
    return Raw(f'<div class="keep"><div class="road">{"".join(out)}</div>{cap}</div>')


class Fig:
    """Drawn figure (inline SVG) for pictures the HTML helpers cannot make:
    memory layouts, pipelines with branches, coordinate systems, geometry.

    Coordinates are figure units. The figure is scaled to the text width, so
    with the default width of 660 one unit is about 0.26 mm and a font size of
    11.5 prints close to the body text. Every method returns self, so calls
    can be chained; render() gives the block to put into a chapter.

    kind (boxes): "" | accent | dark | soft | ghost | plain
    kind (lines and arrows): "" | accent | muted, optionally with " dash"
    kind (text): t (bold) | s (small, muted) | mono | accent | light
    """

    def __init__(self, height: float, width: float = 660):
        self.w, self.h = width, height
        self._items: list[str] = []

    @staticmethod
    def _cls(base: str, kind: str) -> str:
        return f"{base} {kind}".strip()

    def box(self, x, y, w, h, title=None, sub=None, kind: str = "", r: float = 6):
        """Rounded rectangle with an optional centered title and smaller second line."""
        self._items.append(
            f'<rect class="{self._cls("bx", kind)}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>')
        light = " light" if kind == "dark" else ""
        cx = x + w / 2
        if title and sub:
            self.text(cx, y + h / 2 - 2.5, title, kind="t" + light)
            self.text(cx, y + h / 2 + 11.5, sub, kind="s" + light, size=9.5)
        elif title:
            self.text(cx, y + h / 2 + 4, title, kind="t" + light)
        return self

    def text(self, x, y, s, kind: str = "", anchor: str = "middle", size: float = 11.5):
        """One line of text. anchor: start | middle | end."""
        self._items.append(
            f'<text class="{kind}" x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">{esc(s)}</text>')
        return self

    def line(self, *points, kind: str = ""):
        """Polyline through (x, y) points."""
        pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in points)
        self._items.append(f'<polyline class="{self._cls("ln", kind)}" points="{pts}"/>')
        return self

    def arrow(self, *points, kind: str = ""):
        """Polyline through the points with an arrowhead at the last one."""
        (x1, y1), (x2, y2) = points[-2], points[-1]
        length = math.hypot(x2 - x1, y2 - y1) or 1.0
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        size = 7.0
        bx, by = x2 - ux * size, y2 - uy * size
        self.line(*points[:-1], (bx, by), kind=kind)
        head = kind.replace(" dash", "").replace("dash", "").strip()
        self._items.append(
            f'<polygon class="{self._cls("ah", head)}" points="{x2:.1f},{y2:.1f} '
            f'{bx - uy * size * 0.5:.1f},{by + ux * size * 0.5:.1f} '
            f'{bx + uy * size * 0.5:.1f},{by - ux * size * 0.5:.1f}"/>')
        return self

    def dot(self, x, y, r: float = 3, kind: str = ""):
        self._items.append(f'<circle class="{self._cls("ah", kind)}" cx="{x}" cy="{y}" r="{r}"/>')
        return self

    def raw(self, svg: str):
        """Escape hatch: append ready-made SVG markup."""
        self._items.append(svg)
        return self

    def render(self, caption=None) -> Raw:
        _stats["diagrams"] += 1
        svg = (f'<svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img">'
               + "".join(self._items) + "</svg>")
        cap = f'<p class="cap">{T(caption)}</p>' if caption else ""
        return Raw(f'<div class="fig">{svg}{cap}</div>')


# --------------------------------------------------------------------------
# function reference
# --------------------------------------------------------------------------

MAX_SIG_COLS = 100    # characters that fit in the signature line of a function card


def fn(name: str, signature: str, summary, params=None, returns=None, fails=None, notes=None,
       lib: str = "") -> Raw:
    """Function reference card: what a library function does and how to call it.

    signature -- the declaration as written in the library header (may span lines)
    summary   -- one or two sentences: what the call does
    params    -- [(parameter name(s), meaning), ...]; names take inline markup
    returns   -- what comes back
    fails     -- how a failure shows up and when it happens
    notes     -- [(label, text), ...] extra rows such as ("부르는 순서", "...")
    lib       -- where it comes from, shown at the top right ("GLFW 3.4", "OpenGL")

    A card documents someone else's API. It says what the function needs and
    gives, never where the lesson's own code should call it.
    """
    sig = signature.strip("\n")
    if _HANGUL.search(sig):
        _issues.append(f"hangul in signature: {name}")
    longest = max(len(line) for line in sig.split("\n"))
    if longest > MAX_SIG_COLS:
        _issues.append(f"signature line too long ({longest} cols): {name}")
    sig_html = highlight(sig, get_lexer_by_name("cpp"), HtmlFormatter(nowrap=True)).rstrip("\n")

    rows = []
    if params:
        rows.append('<tr class="grp"><td colspan="2">인자</td></tr>')
        rows += [f'<tr><td class="pn">{T(pname)}</td><td>{T(meaning)}</td></tr>' for pname, meaning in params]
    extra = []
    if returns:
        extra.append(("돌려주는 값", returns))
    if fails:
        extra.append(("실패하면", fails))
    extra += list(notes or [])
    rows += [f'<tr><td class="pl">{T(label)}</td><td>{T(text)}</td></tr>' for label, text in extra]

    lib_html = f'<span class="lib">{esc(lib)}</span>' if lib else ""
    table_html = f'<table>{"".join(rows)}</table>' if rows else ""
    return Raw(
        f'<div class="fn"><div class="fh"><span class="nm">{esc(name)}</span>{lib_html}</div>'
        f'<pre class="sig">{sig_html}</pre><div class="fs">{T(summary)}</div>{table_html}</div>'
    )


# --------------------------------------------------------------------------
# missions, checks, questions
# --------------------------------------------------------------------------

def steps(items) -> Raw:
    """Implementation mission. items: [(title, description, [hint, ...]), ...].

    Hints go from light to specific; they point at a direction, never at the
    finished code.
    """
    out = []
    for i, item in enumerate(items, start=1):
        title, desc = item[0], item[1]
        hints = item[2] if len(item) > 2 else []
        hints_html = "".join(
            f'<div class="h"><span class="hl0">힌트 {j}</span>{T(h)}</div>'
            for j, h in enumerate(hints, start=1)
        )
        out.append(
            f'<div class="step"><div class="sn">{i}</div><div class="sb"><div class="t">{T(title)}</div>'
            f'<div class="d">{T(desc)}</div>{hints_html}</div><div class="cb"></div></div>'
        )
    return Raw(f'<div class="steps">{"".join(out)}</div>')


def checklist(items) -> Raw:
    """Completion criteria with empty check boxes."""
    rows = "".join(f'<div class="ci"><div class="cb"></div><div class="tx">{T(i)}</div></div>' for i in items)
    return Raw(f'<div class="check">{rows}</div>')


def exgroup(tag: str, title, hint=None, body=None) -> Raw:
    hint_html = f'<span class="hn">{T(hint)}</span>' if hint else ""
    head = f'<div class="exg"><span class="tg">{esc(tag)}</span><span class="tt">{T(title)}</span>{hint_html}</div>'
    return Raw(head + (J(body) if body else ""))


def qlist(items, lines: int = 2) -> Raw:
    """Numbered questions with dashed writing lines."""
    out = []
    for i, q in enumerate(items, start=1):
        write = '<div class="wl"></div>' * lines
        out.append(f'<div class="qi"><div class="qn">{i}</div><div class="qb">{T(q)}{write}</div></div>')
    return Raw(f'<div class="ql">{"".join(out)}</div>')


def answers(title, items) -> Raw:
    """Answer list. items: [(answer, why), ...] -- reasoning, not code."""
    rows = "".join(
        f'<div class="ai"><div class="an">{i}.</div><div class="ab">{T(a)}'
        + (f'<div class="w">{T(w)}</div>' if w else "")
        + "</div></div>"
        for i, (a, w) in enumerate(items, start=1)
    )
    return Raw(f'<div class="ans"><div class="at">{T(title)}</div>{rows}</div>')


def glossary_chapter(n, terms, title: str = "용어집", pb: bool = True) -> Raw:
    """Closing glossary. terms: [(term, original, meaning), ...], sorted by term."""
    rows = sorted(terms, key=lambda t: t[0].lower())
    body = table([22, 26, 52], ["용어", "원어·식별자", "뜻"], rows, cell_cls=["lab", "", ""])
    return chapter(n, title, [body], pb=pb)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

_PAGE_CSS = """
@page {{
    size: A4;
    margin: 19mm 18mm 21mm 18mm;
    @bottom-left {{
        content: "{footer}";
        font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
        font-size: 7.4pt; color: #9AA0AA;
    }}
    @bottom-right {{
        content: counter(page) " / " counter(pages);
        font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
        font-size: 7.4pt; color: #9AA0AA;
    }}
}}
@page :first {{
    @bottom-left {{ content: none; }}
    @bottom-right {{ content: none; }}
}}
"""


_FONT_FILE = re.compile(r"^(?P<family>.+)-(?P<weight>\d{3})\.(?P<ext>ttf|otf)$", re.IGNORECASE)


def _local_fonts_css() -> str:
    """@font-face rules for font files placed in _build/fonts (optional).

    Every <Family>-<weight>.ttf file in Docs/Handouts/_build/fonts is embedded
    as a data URL; make_fonts.py writes them. Two reasons to have them: headless
    Chrome and Edge cannot see a font installed "for the current user only", and
    Chrome prints a variable font as Type3 glyphs that Acrobat draws slowly, so
    every font must be a static file. Without that folder this returns "".
    """
    folder = ENGINE_DIR.parent / "_build" / "fonts"
    if not folder.is_dir():
        return ""
    rules = []
    for path in sorted(folder.iterdir()):
        m = _FONT_FILE.match(path.name)
        if not m:
            continue
        ext = m["ext"].lower()
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        kind = "opentype" if ext == "otf" else "truetype"
        rules.append(
            f'@font-face {{ font-family: "{m["family"]}"; font-weight: {m["weight"]}; '
            f'src: url(data:font/{ext};base64,{data}) format("{kind}"); }}'
        )
    return "\n".join(rules)


def build(meta: dict, cover_html: str, sections, out_html) -> dict:
    """Write the HTML file and return check results.

    meta     -- {"title": document title, "footer": running footer text}
    sections -- list of chapter() results

    The returned dict has "issues"; it must be an empty list before the PDF is
    handed over (hangul inside code, over-long code lines, over-long blocks).
    """
    css = (ENGINE_DIR / "base.css").read_text(encoding="utf-8")
    footer = meta["footer"].replace("\\", "\\\\").replace('"', '\\"')
    page_css = _PAGE_CSS.format(footer=footer)
    doc = (
        '<!doctype html>\n<html lang="ko"><head><meta charset="utf-8">'
        f"<title>{esc(meta['title'])}</title>"
        f"<style>{page_css}{_local_fonts_css()}{css}</style></head><body>\n"
        f"{cover_html}\n{J(*sections)}\n</body></html>\n"
    )
    out_path = Path(out_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    return {"html": str(out_path), "issues": list(_issues), **_stats}
