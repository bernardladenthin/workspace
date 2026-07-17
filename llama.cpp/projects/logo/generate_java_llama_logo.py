#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Generate a parameterised llama.cpp-style shard logo.

The icon is a stylised **J** built from three slanted shards in the visual
language of the llama.cpp mark:

  1. top cap   - short slab at the top of the stem
  2. stem      - tall diagonal spine (the vertical stroke of the J)
  3. hook      - slab reaching left at the bottom (the J hook), rounded corner

All three shards share one italic shear ``k`` and connect through thin,
horizontal seams. Every seam is built from a shared anchor so the pieces
overlap by construction instead of merely kissing at a corner (the bug in the
first draft, where the top cap and stem met at a single point and left a
triangular black gap).

The wordmark stays real ``<text>`` -- the Martian Mono font is embedded as a
base64 ``@font-face`` so nothing is converted to outlines.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path
from xml.sax.saxutils import escape

import logolib
from logolib import MM_ADVANCE, MM_CAP, MM_UPM, BaseConfig, fmt


@dataclass(frozen=True)
class LogoConfig(BaseConfig):
    # Brand colours
    white: str = "#FAFAFA"
    orange: str = "#F65E00"

    # Icon placement (translate + uniform scale of the local icon geometry).
    # When ``auto_layout`` is on, icon_x / icon_y / text_x / text_baseline are
    # computed from the geometry + font metrics so the lockup is always centred.
    auto_layout: bool = True
    gap: float = 300  # space between icon and wordmark (auto_layout only)
    # Fit the icon to a capital letter: scale so its bbox height == fit_cap_em
    # of the font size (0.8 = cap height) and sit it on the baseline.
    fit_cap: bool = True
    fit_cap_em: float = 0.8
    icon_x: float = 1620
    icon_y: float = 690
    icon_scale: float = 0.72

    # --- Icon geometry (local units) -------------------------------------
    # Italic shear: horizontal offset added per unit of height. The top of a
    # shard is shifted right by ``k * height`` relative to its bottom edge.
    shear: float = 0.52

    # Stem: the diagonal spine. Anchored by its BOTTOM-LEFT corner.
    stem_bl_x: float = 300
    stem_bl_y: float = 640
    stem_w: float = 150
    stem_h: float = 360

    # Vertical seam gaps between the three shards.
    gap_top: float = 16
    gap_bottom: float = 16

    # Top cap: a slab above the stem. ``extend_left`` / ``extend_right`` say how
    # far its bottom edge reaches past the stem's top edge on each side.
    cap_enabled: bool = True
    cap_h: float = 132
    cap_extend_left: float = 150
    cap_extend_right: float = 0

    # Bottom part style:
    #   "hook"     - horizontal slab reaching left (the classic J hook)
    #   "parallel" - a shorter parallel copy of the stem (same angle), placed to
    #                the lower-left and centred on the stem's bottom end
    foot_style: str = "parallel"
    foot_height_frac: float = 0.5   # parallel foot height as a fraction of stem_h
    foot_gap: float = 74            # horizontal gap between stem and parallel foot
    foot_center_offset: float = 0.0 # vertical offset of foot centre vs stem bottom

    # Bottom hook (foot_style == "hook"): a slab below the stem reaching left.
    hook_h: float = 150
    hook_extend_left: float = 300
    hook_extend_right: float = 0

    # Rounded outer corners (llama.cpp feel). 0 disables.
    cap_corner_radius: float = 44
    hook_corner_radius: float = 60

    # Optional: mirror the J to the right so J + its mirror (an "L") reads as
    # "JL" for java-llama. Off by default (single J). jl_gap is the space
    # between the two glyphs (local units).
    mirror_jl: bool = False
    jl_gap: float = 300

    # --- Wordmark ---------------------------------------------------------
    text_x: float = 2360
    text_baseline: float = 1470
    font_size: float = 360
    java_text: str = "java-"
    llama_text: str = "llama.cpp"

    # Emit the wordmark as <path> outlines instead of <text> + embedded font.
    # Font/text-independent: no @font-face, no <text>, smaller file, license-clean.
    outline_text: bool = False

    # Debug layer (anchors + seam lines)
    debug: bool = False


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
Point = "tuple[float, float]"


def _shard(bl_x: float, bl_y: float, w: float, h: float, k: float):
    """Parallelogram from its bottom-left corner. Top edge sheared right by k*h.

    Returns the four corners clockwise starting at the top-left:
        TL, TR, BR, BL
    """
    tl = (bl_x + k * h, bl_y - h)
    tr = (bl_x + w + k * h, bl_y - h)
    br = (bl_x + w, bl_y)
    bl = (bl_x, bl_y)
    return [tl, tr, br, bl]


def build_icon(c: LogoConfig):
    """Return the three shards as dicts: {'points': [...], 'round': {idx: r}}.

    ``round`` maps a corner index (into ``points``) to a radius; the SVG builder
    turns that corner into a quadratic arc. The stem is the anchor: the cap
    hangs above its top edge and the hook below its bottom edge, both sharing
    the stem's horizontal extent so the seams always overlap.
    """
    k = c.shear

    stem = _shard(c.stem_bl_x, c.stem_bl_y, c.stem_w, c.stem_h, k)
    stem_tl, stem_tr, stem_br, stem_bl = stem

    # The stem's right edge is the "spine". Cap and hook keep their right edge on
    # this one slanted line, so the pieces are offset along the angle (offset =
    # shear * height) instead of being right-flush.
    br_x, base_y = stem_br[0], stem_br[1]

    def right_x_at(y):
        return br_x + k * (base_y - y)

    # --- Top cap: bottom edge sits gap_top above the stem's top edge. -----
    cap_bottom_y = stem_tl[1] - c.gap_top
    cap_w = c.stem_w + c.cap_extend_left + c.cap_extend_right
    cap_rb_x = right_x_at(cap_bottom_y) + c.cap_extend_right
    cap = _shard(cap_rb_x - cap_w, cap_bottom_y, cap_w, c.cap_h, k)

    if c.foot_style == "parallel":
        # A shorter parallel copy of the stem (same angle), placed to the lower
        # left and centred on the stem's bottom end.
        foot_h = c.stem_h * c.foot_height_frac
        center_y = stem_bl[1] + c.foot_center_offset
        foot_bl_y = center_y + foot_h / 2.0
        # right edge sits foot_gap left of the stem's left edge at the foot centre
        foot_rb_x = stem_bl[0] - c.foot_gap + k * (foot_bl_y - center_y)
        hook = _shard(foot_rb_x - c.stem_w, foot_bl_y, c.stem_w, foot_h, k)
        hook_round = {3: c.hook_corner_radius, 1: c.cap_corner_radius}
    else:
        # Horizontal hook: top edge sits gap_bottom below the stem's bottom. Its
        # right edge stays on the spine (shifted LEFT by shear*(gap+hook_h)).
        hook_bottom_y = stem_bl[1] + c.gap_bottom + c.hook_h
        hook_w = c.stem_w + c.hook_extend_left + c.hook_extend_right
        hook_rb_x = right_x_at(hook_bottom_y) + c.hook_extend_right
        hook = _shard(hook_rb_x - hook_w, hook_bottom_y, hook_w, c.hook_h, k)
        hook_round = {3: c.hook_corner_radius}

    shards = []
    if c.cap_enabled and c.cap_h > 0:
        # Cap present: round its top-left; stem stays square (butts into cap).
        shards.append({"id": "j-cap", "points": cap, "round": {0: c.cap_corner_radius}})
        shards.append({"id": "j-stem", "points": stem, "round": {}})
    else:
        # No cap: the stem is the top piece, so round ITS top-left corner.
        shards.append({"id": "j-stem", "points": stem, "round": {0: c.cap_corner_radius}})
    shards.append({"id": "j-hook", "points": hook, "round": hook_round})
    return shards


def icon_shards(c: LogoConfig):
    """Single J, or J + its horizontal mirror ("L") reading as "JL"."""
    shards = build_icon(c)
    if not c.mirror_jl:
        return shards
    maxx = max(p[0] for s in shards for p in s["points"])
    off = 2 * maxx + c.jl_gap  # x' = off - x mirrors then shifts right past the J
    mirrored = [
        {"id": s["id"] + "-mirror",
         "points": [(off - x, y) for (x, y) in s["points"]],
         "round": dict(s["round"])}
        for s in shards
    ]
    return shards + mirrored


def _rounded_path(points, round_map):
    """Build an SVG path for a polygon, rounding the corners named in round_map.

    A rounded corner is cut back along both adjacent edges by ``r`` and bridged
    with a quadratic Bezier through the original vertex.
    """
    n = len(points)

    def cut(i, r, toward):
        p = points[i]
        q = points[toward]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = (dx * dx + dy * dy) ** 0.5 or 1.0
        r = min(r, length * 0.5)
        return (p[0] + dx / length * r, p[1] + dy / length * r)

    segs = []
    for i in range(n):
        r = round_map.get(i, 0)
        prev_i = (i - 1) % n
        next_i = (i + 1) % n
        if r > 0:
            a = cut(i, r, prev_i)  # entry point on the incoming edge
            b = cut(i, r, next_i)  # exit point on the outgoing edge
            if i == 0:
                segs.append(f"M {fmt(a[0])} {fmt(a[1])}")
            else:
                segs.append(f"L {fmt(a[0])} {fmt(a[1])}")
            segs.append(f"Q {fmt(points[i][0])} {fmt(points[i][1])} {fmt(b[0])} {fmt(b[1])}")
        else:
            cmd = "M" if i == 0 else "L"
            segs.append(f"{cmd} {fmt(points[i][0])} {fmt(points[i][1])}")
    segs.append("Z")
    return " ".join(segs)


# ---------------------------------------------------------------------------
# Font embedding
# ---------------------------------------------------------------------------
def font_face_style(c: LogoConfig) -> str:
    if not c.embed_font:
        return ""
    rule = logolib.font_face_rule(c.font_path, c.font_family, c.font_weight)
    return "\n  <defs><style>\n    " + rule + "\n  </style></defs>"


# ---------------------------------------------------------------------------
# SVG
# ---------------------------------------------------------------------------
def _icon_local_bbox(shards):
    pts = [p for s in shards for p in s["points"]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def solve_layout(c: LogoConfig, shards):
    """Return (icon_x, icon_y, text_x, text_baseline) centring the lockup.

    The whole icon+wordmark block is centred horizontally and vertically on the
    canvas; the icon's vertical midpoint is aligned to the wordmark's optical
    centre (midway between cap line and baseline).
    """
    if not c.auto_layout:
        return c.icon_x, c.icon_y, c.icon_scale, c.text_x, c.text_baseline

    minx, miny, maxx, maxy = _icon_local_bbox(shards)
    fs = c.font_size
    cap_px = (MM_CAP / MM_UPM) * fs
    optical_center = c.height / 2.0
    text_baseline = optical_center + cap_px / 2.0

    if c.fit_cap:
        scale = (c.fit_cap_em * fs) / (maxy - miny)
    else:
        scale = c.icon_scale

    iw = (maxx - minx) * scale
    n = len(c.java_text) + len(c.llama_text)
    text_w = n * (MM_ADVANCE / MM_UPM) * fs + c.letter_spacing * max(0, n - 1)

    lock_w = iw + c.gap + text_w
    left = (c.width - lock_w) / 2.0
    icon_x = left - minx * scale
    text_x = left + iw + c.gap

    if c.fit_cap:
        # baseline-align: the icon's bottom sits on the text baseline.
        icon_y = text_baseline - maxy * scale
    else:
        icon_y = optical_center - ((miny + maxy) / 2.0) * scale

    return icon_x, icon_y, scale, text_x, text_baseline


def build_svg(c: LogoConfig) -> str:
    shards = icon_shards(c)
    icon_x, icon_y, icon_scale, text_x, text_baseline = solve_layout(c, shards)

    icon_paths = []
    for s in shards:
        d = _rounded_path(s["points"], s["round"])
        icon_paths.append(f'    <path id="{s["id"]}" d="{d}"/>')
    icon_body = "\n".join(icon_paths)

    debug_layer = ""
    if c.debug:
        lines = []
        for s in shards:
            for (x, y) in s["points"]:
                lines.append(
                    f'      <circle cx="{fmt(x)}" cy="{fmt(y)}" r="7" '
                    f'fill="none" stroke="#00D4FF" stroke-width="3"/>'
                )
        debug_layer = (
            '\n    <g id="debug-guides">\n' + "\n".join(lines) + "\n    </g>"
        )

    if c.outline_text:
        style = ""
        desc = "Shard J icon in the llama.cpp style with an outlined wordmark."
        java_d, split_x = logolib.text_to_path_d(
            c.java_text, c.font_size, text_x, text_baseline, c.letter_spacing, c.font_path
        )
        llama_d, _ = logolib.text_to_path_d(
            c.llama_text, c.font_size, split_x, text_baseline, c.letter_spacing, c.font_path
        )
        wordmark = (
            f'  <g id="wordmark">\n'
            f'    <path id="java-part" d="{java_d}" fill="{c.orange}"/>\n'
            f'    <path id="llama-part" d="{llama_d}" fill="{c.white}"/>\n'
            f'  </g>'
        )
    else:
        style = font_face_style(c)
        desc = "Shard J icon in the llama.cpp style with an embedded-font wordmark."
        font_family = escape(c.font_family, {'"': "&quot;"})
        java_text = escape(c.java_text)
        llama_text = escape(c.llama_text)
        wordmark = (
            f'  <text id="wordmark" x="{fmt(text_x)}" y="{fmt(text_baseline)}"\n'
            f'        font-family="{font_family}, monospace"\n'
            f'        font-size="{fmt(c.font_size)}px"\n'
            f'        font-weight="{c.font_weight}"\n'
            f'        letter-spacing="{fmt(c.letter_spacing)}px">'
            f'<tspan id="java-part" fill="{c.orange}">{java_text}</tspan>'
            f'<tspan id="llama-part" fill="{c.white}">{llama_text}</tspan></text>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{fmt(c.width)}" height="{fmt(c.height)}" viewBox="0 0 {fmt(c.width)} {fmt(c.height)}"
     fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>java-llama.cpp cover</title>
  <desc>{desc}</desc>{style}

  <rect id="background" width="{fmt(c.width)}" height="{fmt(c.height)}" fill="{c.background}"/>

  <g id="j-symbol" transform="translate({fmt(icon_x)} {fmt(icon_y)}) scale({fmt(icon_scale)})" fill="{c.white}">
{icon_body}{debug_layer}
  </g>

{wordmark}
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=Path("java-llama-cpp-generated.svg"))
    parser.add_argument("-c", "--config", type=Path, help="JSON file overriding defaults")
    parser.add_argument("--write-default-config", type=Path, help="Write the default JSON config and exit")
    parser.add_argument("--debug", action="store_true", help="Render construction anchors")
    parser.add_argument("--outline-text", action="store_true",
                        help="Emit the wordmark as <path> outlines (no embedded font, no <text>)")
    parser.add_argument("--png", type=Path, help="Also rasterise a PNG (needs 'pip install resvg-py')")
    parser.add_argument("--png-width", type=int, default=2250, help="PNG width in px")
    args = parser.parse_args()

    if args.write_default_config:
        logolib.write_default_config(LogoConfig, args.write_default_config)
        return

    config = logolib.load_config(LogoConfig, args.config)
    if args.debug:
        config = replace(config, debug=True)
    if args.outline_text:
        config = replace(config, outline_text=True)

    svg = build_svg(config)
    args.output.write_text(svg, encoding="utf-8")

    if args.png:
        logolib.render_png(args.output, args.png, args.png_width)


if __name__ == "__main__":
    main()
