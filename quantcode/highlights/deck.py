"""Render-Engine fuer Instagram-Story-Highlight-Cover.

HighlightDeck baut eine Serie von 1080x1920-PNGs: eine Titel-Folie
(slide_title) plus beliebig viele Inhalts-Folien (slide_text).
Headline-Text unterstuetzt einfache Akzent-Markierung per *wort*.
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import brand

_MARKUP_RE = re.compile(r"\*(.+?)\*")
_LEADING_PUNCT_RE = re.compile(r"^[,.:;!?)\]]+")


def _tokenize(text: str) -> list[tuple[str, bool]]:
    """Zerlegt Text in (wort, ist_akzent)-Tupel. *wort* wird zu Akzentfarbe.

    Satzzeichen direkt nach einer *Akzent*-Markierung werden an das
    vorherige Wort angehaengt, damit z.B. "*Muster*," nicht als
    "Muster ," mit unschoenem Leerzeichen vor dem Komma gerendert wird.
    """
    tokens: list[tuple[str, bool]] = []
    pos = 0
    for m in _MARKUP_RE.finditer(text):
        for w in text[pos:m.start()].split():
            tokens.append((w, False))
        for w in m.group(1).split():
            tokens.append((w, True))
        pos = m.end()
    for w in text[pos:].split():
        tokens.append((w, False))
    return _merge_leading_punct(tokens)


def _merge_leading_punct(tokens: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
    merged: list[tuple[str, bool]] = []
    for word, accent in tokens:
        m = _LEADING_PUNCT_RE.match(word)
        if m and merged:
            punct = m.group(0)
            rest = word[len(punct):]
            prev_word, prev_accent = merged[-1]
            merged[-1] = (prev_word + punct, prev_accent)
            if rest:
                merged.append((rest, accent))
        else:
            merged.append((word, accent))
    return merged


def _wrap_tokens(draw: ImageDraw.ImageDraw, tokens, font: ImageFont.FreeTypeFont, max_width: int):
    """Gruppiert Tokens in Zeilen, die max_width nicht ueberschreiten."""
    lines: list[list[tuple[str, bool]]] = [[]]
    space_w = draw.textlength(" ", font=font)
    cur_w = 0.0
    for word, accent in tokens:
        w = draw.textlength(word, font=font)
        added = w if not lines[-1] else w + space_w
        if lines[-1] and cur_w + added > max_width:
            lines.append([(word, accent)])
            cur_w = w
        else:
            lines[-1].append((word, accent))
            cur_w += added
    return [ln for ln in lines if ln]


class HighlightDeck:
    """Baut eine Highlight-Serie (Titel + Inhalts-Folien) und exportiert PNGs."""

    def __init__(self, thema: str, out_dir: str | Path):
        self.thema = thema
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._slide_index = 0

        self._f_display_xl = ImageFont.truetype(brand.FONT_DISPLAY_BOLD, 132)
        self._f_display_lg = ImageFont.truetype(brand.FONT_DISPLAY_BOLD, 58)
        self._f_body = ImageFont.truetype(brand.FONT_BODY, 34)
        self._f_mono_sm = ImageFont.truetype(brand.FONT_MONO, 24)
        self._f_mono_label = ImageFont.truetype(brand.FONT_MONO_BOLD, 26)
        self._f_mono_tiny = ImageFont.truetype(brand.FONT_MONO, 22)

    def _new_canvas(self) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        img = Image.new("RGB", (brand.WIDTH, brand.HEIGHT), brand.BG)
        return img, ImageDraw.Draw(img)

    def _draw_logo(self, draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0):
        """Zeichnet die QuantCode-AI-Candlestick-Wortmarke (aus dem Post-Design)."""
        bars = [(0, 8, 30), (12, 0, 40), (24, -4, 24)]
        for dx, dy, h in bars:
            bx = x + dx * scale
            top = y + dy * scale
            draw.line([(bx, top), (bx, top + h * scale)], fill=brand.ACCENT, width=max(2, int(3 * scale)))
            draw.rectangle(
                [bx - 4 * scale, top + h * 0.3 * scale, bx + 4 * scale, top + h * 0.75 * scale],
                fill=brand.ACCENT,
            )

    def _footer(self, draw: ImageDraw.ImageDraw):
        y = brand.HEIGHT - 92
        draw.line([(brand.MARGIN_X, y), (brand.WIDTH - brand.MARGIN_X, y)], fill=brand.BORDER, width=2)
        draw.text((brand.MARGIN_X, y + 20), brand.DISCLAIMER, font=self._f_mono_tiny, fill=brand.FAINT)
        handle_w = draw.textlength(brand.HANDLE, font=self._f_mono_tiny)
        draw.text((brand.WIDTH - brand.MARGIN_X - handle_w, y + 20), brand.HANDLE, font=self._f_mono_tiny, fill=brand.MUTED)

    def _save(self, img: Image.Image):
        self._slide_index += 1
        path = self.out_dir / f"{self._slide_index:02d}.png"
        img.save(path)
        return path

    def slide_title(self, wort: str, untertitel: str) -> Path:
        """Folie 1: nur das Thema als grosses Wort, zentriert, plus Untertitel."""
        img, draw = self._new_canvas()

        self._draw_logo(draw, brand.WIDTH / 2 - 220, brand.HEIGHT / 2 - 200, scale=1.6)

        word = wort.upper()
        w = draw.textlength(word, font=self._f_display_xl)
        draw.text(
            ((brand.WIDTH - w) / 2, brand.HEIGHT / 2 - 60),
            word, font=self._f_display_xl, fill=brand.TEXT,
        )

        sub_w = draw.textlength(untertitel, font=self._f_mono_sm)
        draw.text(
            ((brand.WIDTH - sub_w) / 2, brand.HEIGHT / 2 + 100),
            untertitel, font=self._f_mono_sm, fill=brand.MUTED,
        )

        self._footer(draw)
        return self._save(img)

    def slide_text(self, eyebrow: str, headline: str, body: str) -> Path:
        """Inhalts-Folie: Eyebrow-Label, Headline mit *Akzent*-Markup, Fliesstext."""
        img, draw = self._new_canvas()

        y = 220
        self._draw_logo(draw, brand.MARGIN_X, y - 10, scale=0.8)
        draw.text((brand.MARGIN_X + 70, y), eyebrow.upper(), font=self._f_mono_label, fill=brand.ACCENT)

        y += 90
        max_w = brand.WIDTH - 2 * brand.MARGIN_X
        tokens = _tokenize(headline)
        lines = _wrap_tokens(draw, tokens, self._f_display_lg, max_w)
        line_h = 72
        for line in lines:
            x = brand.MARGIN_X
            for word, accent in line:
                color = brand.ACCENT if accent else brand.TEXT
                draw.text((x, y), word, font=self._f_display_lg, fill=color)
                x += draw.textlength(word + " ", font=self._f_display_lg)
            y += line_h

        y += 30
        body_tokens = [(w, False) for w in body.split()]
        body_lines = _wrap_tokens(draw, body_tokens, self._f_body, max_w)
        for line in body_lines:
            text = " ".join(w for w, _ in line)
            draw.text((brand.MARGIN_X, y), text, font=self._f_body, fill=brand.MUTED)
            y += 48

        self._footer(draw)
        return self._save(img)
