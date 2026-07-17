#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Generate the srcmorph logo: the wordmark with a blurred/"morphing" m.

There is no separate icon. The wordmark is real ``<text>`` with the font
embedded (no outlines): ``src`` in white, ``morph`` in orange -- and the leading
``m`` of ``morph`` is the "morph": it stays sharp on the left and smears /
dissolves toward the right.

The m is built from N copies of the glyph at increasing Gaussian blur, each
faded in over a soft, overlapping gradient band in x, so the blur ramps smoothly
across the glyph with no slice seams. ``directional`` chooses a horizontal smear
vs a round defocus.

    python generate_srcmorph_logo.py -c srcmorph-logo-config.json \
        -o srcmorph-generated.svg --png srcmorph.png
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import logolib
from logolib import MM_ADVANCE, MM_CAP, MM_UPM, BaseConfig, clamp01, fmt

# Ink bounds of the lowercase "m" glyph in font units: xMin, xMax.
M_INK_X0, M_INK_X1 = 76.0, 628.0


@dataclass(frozen=True)
class SrcmorphConfig(BaseConfig):
    # Wordmark
    font_size: float = 620
    src_text: str = "src"
    morph_text: str = "morph"
    src_color: str = "#FAFAFA"     # white
    morph_color: str = "#F65E00"   # orange

    # "Morph" applied to the leading glyph of morph_text (the m):
    # the m comes IN blurred from the left and sharpens toward the right, where
    # it joins the cleanly-written "orph". Built from N layers whose blur ramps
    # down left->right, each faded in over a soft overlapping gradient band.
    m_layers: int = 8            # more = smoother blur ramp
    max_blur_em: float = 0.10    # blur at the m's left edge (fraction of font_size)
    blur_power: float = 2.2      # >1 keeps more of the m sharp on the right
    fade_to: float = 0.0         # left-edge opacity (0 = the m emerges from nothing)
    directional: bool = True     # True = horizontal smear, False = round defocus

    # Extra gap only BEFORE the m (between "src" and "morph"); the m + "orph"
    # stay adjacent so "morph" reads as one clean word.
    space_before_em: float = 0.40
    space_after_em: float = 0.0

    # Layout
    auto_layout: bool = True
    text_x: float = 1500         # manual mode
    text_baseline: float = 1500  # manual mode

    # Emit the wordmark as <path> outlines instead of <text> + embedded font.
    # The blur filters move onto the outlined groups, so the morph is preserved.
    outline_text: bool = False


def font_face_style(c: SrcmorphConfig) -> str:
    if not c.embed_font:
        return ""
    return logolib.font_face_rule(c.font_path, c.font_family, c.font_weight)


def advance(c: SrcmorphConfig) -> float:
    return (MM_ADVANCE / MM_UPM) * c.font_size + c.letter_spacing


def morph_glyph(c: SrcmorphConfig, glyph: str, gx: float, baseline: float):
    """(defs, body) for the m: blurred at the left, sharpening to the right.

    N copies of the glyph are drawn; the blur ramps down from the left edge to 0
    at the right, and each copy is faded in over a soft, overlapping gradient
    band in x, so the ramp is smooth (no slice seams) and the left dissolves.
    """
    F = c.font_size
    xa = gx + M_INK_X0 / MM_UPM * F   # left edge of the m ink (offset 0)
    xb = gx + M_INK_X1 / MM_UPM * F   # right edge of the m ink (offset 1)
    max_blur = c.max_blur_em * F
    n = max(2, c.m_layers)
    span = 1.0 / (n - 1)

    glyph_d = None
    if c.outline_text:
        glyph_d, _ = logolib.text_to_path_d(
            glyph, F, gx, baseline, c.letter_spacing, c.font_path
        )

    defs, body = [], []
    for i in range(n):
        p = i / (n - 1)               # 0 = leftmost (blurry), 1 = rightmost (sharp)
        blur = max_blur * ((1.0 - p) ** c.blur_power)
        std = f"{fmt(blur)} 0" if c.directional else fmt(blur)
        defs.append(
            f'<filter id="mf{i}" x="-120%" y="-120%" width="420%" height="420%">'
            f'<feGaussianBlur stdDeviation="{std}"/></filter>'
        )
        p0, p1, p2 = clamp01(p - span), p, clamp01(p + span)
        left = "1" if i == 0 else "0"
        right = "1" if i == n - 1 else "0"
        stops = (
            f'<stop offset="0" stop-color="#fff" stop-opacity="{left}"/>'
            f'<stop offset="{fmt(p0)}" stop-color="#fff" stop-opacity="{left}"/>'
            f'<stop offset="{fmt(p1)}" stop-color="#fff" stop-opacity="1"/>'
            f'<stop offset="{fmt(p2)}" stop-color="#fff" stop-opacity="{right}"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="{right}"/>'
        )
        defs.append(
            f'<linearGradient id="mg{i}" gradientUnits="userSpaceOnUse" '
            f'x1="{fmt(xa)}" y1="0" x2="{fmt(xb)}" y2="0">{stops}</linearGradient>'
        )
        defs.append(
            f'<mask id="mm{i}" maskUnits="userSpaceOnUse" x="0" y="0" '
            f'width="{fmt(c.width)}" height="{fmt(c.height)}">'
            f'<rect width="{fmt(c.width)}" height="{fmt(c.height)}" fill="url(#mg{i})"/></mask>'
        )
        op = c.fade_to + (1.0 - c.fade_to) * p   # left dissolves, right solid
        if c.outline_text:
            inner = (
                f'<path d="{glyph_d}" fill="{c.morph_color}" filter="url(#mf{i})"/>'
            )
        else:
            inner = (
                f'<text x="{fmt(gx)}" y="{fmt(baseline)}" font-family="{c.font_family}, monospace" '
                f'font-size="{fmt(F)}" fill="{c.morph_color}" filter="url(#mf{i})">{glyph}</text>'
            )
        body.append(f'<g mask="url(#mm{i})" opacity="{fmt(op)}">{inner}</g>')
    return "".join(defs), "".join(body)


def solve_layout(c: SrcmorphConfig):
    """Return (text_x, baseline) centring the whole wordmark on the canvas.

    ``text_x`` is the left edge; extra ``space_before/after`` around the m are
    accounted for so the lockup stays centred.
    """
    baseline = c.height / 2.0 + (MM_CAP / MM_UPM) * c.font_size / 2.0
    if not c.auto_layout:
        return c.text_x, baseline
    n = len(c.src_text) + len(c.morph_text)
    extra = (c.space_before_em + c.space_after_em) * c.font_size
    text_w = n * advance(c) - c.letter_spacing + extra
    text_x = (c.width - text_w) / 2.0
    return text_x, baseline


def build_svg(c: SrcmorphConfig) -> str:
    text_x, baseline = solve_layout(c)
    adv = advance(c)

    n_src = len(c.src_text)
    tail = c.morph_text[1:]              # "orph"
    m_char = c.morph_text[:1] or "m"     # "m"

    space_before = c.space_before_em * c.font_size
    space_after = c.space_after_em * c.font_size
    src_x = text_x
    m_x = text_x + n_src * adv + space_before
    tail_x = m_x + adv + space_after

    if c.outline_text:
        src_d, _ = logolib.text_to_path_d(
            c.src_text, c.font_size, src_x, baseline, c.letter_spacing, c.font_path
        )
        tail_d, _ = logolib.text_to_path_d(
            tail, c.font_size, tail_x, baseline, c.letter_spacing, c.font_path
        )
        src_el = f'<path id="src-part" d="{src_d}" fill="{c.src_color}"/>'
        tail_el = f'<path id="orph-part" d="{tail_d}" fill="{c.morph_color}"/>'
    else:
        common = (
            f'font-family="{c.font_family}, monospace" font-size="{fmt(c.font_size)}px" '
            f'font-weight="{c.font_weight}" letter-spacing="{fmt(c.letter_spacing)}px"'
        )
        src_el = f'<text id="src-part" x="{fmt(src_x)}" y="{fmt(baseline)}" {common} fill="{c.src_color}">{c.src_text}</text>'
        tail_el = f'<text id="orph-part" x="{fmt(tail_x)}" y="{fmt(baseline)}" {common} fill="{c.morph_color}">{tail}</text>'
    mdefs, mbody = morph_glyph(c, m_char, m_x, baseline)

    style = "" if c.outline_text else font_face_style(c)
    defs = f"<style>{style}</style>{mdefs}" if style else mdefs

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{fmt(c.width)}" height="{fmt(c.height)}" viewBox="0 0 {fmt(c.width)} {fmt(c.height)}"
     fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>srcmorph cover</title>
  <desc>Wordmark with a morphing (blurred, smearing) m in "morph".</desc>
  <defs>{defs}</defs>

  <rect id="background" width="{fmt(c.width)}" height="{fmt(c.height)}" fill="{c.background}"/>

  <g id="wordmark">
    {src_el}
    <g id="morph-m">{mbody}</g>
    {tail_el}
  </g>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=Path("srcmorph-generated.svg"))
    parser.add_argument("-c", "--config", type=Path, help="JSON file overriding defaults")
    parser.add_argument("--write-default-config", type=Path, help="Write the default JSON config and exit")
    parser.add_argument("--png", type=Path, help="Also rasterise a PNG (needs 'pip install resvg-py')")
    parser.add_argument("--png-width", type=int, default=2250)
    parser.add_argument("--outline-text", action="store_true",
                        help="Emit the wordmark as <path> outlines (no embedded font, no <text>)")
    args = parser.parse_args()

    if args.write_default_config:
        logolib.write_default_config(SrcmorphConfig, args.write_default_config)
        return

    config = logolib.load_config(SrcmorphConfig, args.config)
    if args.outline_text:
        from dataclasses import replace
        config = replace(config, outline_text=True)
    svg = build_svg(config)
    args.output.write_text(svg, encoding="utf-8")

    if args.png:
        logolib.render_png(args.output, args.png, args.png_width)


if __name__ == "__main__":
    main()
