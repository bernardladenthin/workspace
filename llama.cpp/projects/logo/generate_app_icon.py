#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Generate a square **app icon** from the java-llama.cpp shard-``J``.

Reuses the icon geometry from ``generate_java_llama_logo.py`` (the three shards
``j-cap`` / ``j-stem`` / ``j-hook`` and its rounded-path builder) and drops the
wordmark, centring the ``J`` on a square canvas. No font is involved, so the
output is pure ``<path>`` geometry.

Two shapes:

  * **full icon** - the J on a filled square (background baked in). Used for the
    legacy launcher PNGs and the Play-Store 512 icon.
  * **adaptive foreground** - the J on a transparent square, scaled into the
    adaptive-icon *safe zone* (center ~66% of the 108dp canvas) so nothing is
    clipped when the launcher masks it to a circle / squircle / rounded square.

``--android-set DIR`` writes a complete, drop-in ``res/`` tree:

    ic_launcher.svg / ic_launcher_foreground.svg / ic_launcher_background.svg
    ic_launcher-512.png                              (Play Store)
    res/mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher.png            (48..192)
    res/mipmap-{m,h,xh,xxh,xxxh}dpi/ic_launcher_foreground.png (108..432)
    res/mipmap-anydpi-v26/ic_launcher.xml            (adaptive descriptor)
    res/values/ic_launcher_background.xml            (background colour)

    python generate_app_icon.py -c java-llama-logo-config.json \
        --android-set app-icon
"""

from __future__ import annotations

import argparse
from pathlib import Path

import logolib
from logolib import fmt

import generate_java_llama_logo as jl

# Android launcher-icon edge lengths in px, per density bucket.
# Legacy square icon (mipmap/ic_launcher.png):
LEGACY_PX = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
# Adaptive foreground/background (108dp canvas) at the same buckets:
FOREGROUND_PX = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}

# Content fill fractions of the square.
FULL_FRAC = 0.72        # legacy icon: the J fills most of the tile, small margin
# Adaptive foreground: the J's farthest ink (the diagonal hook / cap tips) must
# stay inside the 66dp-of-108dp safe-zone circle (diameter fraction ~0.61) so it
# is never clipped by a circular launcher mask. 0.52 keeps a small margin.
SAFE_FRAC = 0.52


def build_icon_svg(
    config: "jl.LogoConfig",
    size: float,
    fill: str,
    background: str,
    content_frac: float,
) -> str:
    """Return a square SVG with the shard-J centred and scaled to ``content_frac``.

    ``background`` == ``"none"`` emits a transparent icon (adaptive foreground);
    any colour value bakes a full-bleed background rect behind the J.
    """
    shards = jl.icon_shards(config)
    minx, miny, maxx, maxy = jl._icon_local_bbox(shards)
    w, h = maxx - minx, maxy - miny
    scale = content_frac * size / max(w, h)
    cw, ch = w * scale, h * scale
    # Centre the icon bbox on the square.
    tx = (size - cw) / 2.0 - minx * scale
    ty = (size - ch) / 2.0 - miny * scale

    paths = []
    for s in shards:
        d = jl._rounded_path(s["points"], s["round"])
        paths.append(f'    <path id="{s["id"]}" d="{d}"/>')
    body = "\n".join(paths)

    bg = "" if background == "none" else (
        f'\n  <rect id="background" width="{fmt(size)}" height="{fmt(size)}" '
        f'fill="{background}"/>'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{fmt(size)}" height="{fmt(size)}" viewBox="0 0 {fmt(size)} {fmt(size)}"
     fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>java-llama.cpp app icon</title>
  <desc>Square app-icon crop of the llama.cpp-style shard J.</desc>{bg}
  <g id="j-symbol" transform="translate({fmt(tx)} {fmt(ty)}) scale({fmt(scale)})" fill="{fill}">
{body}
  </g>
</svg>
"""


def _solid_svg(size: float, color: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{fmt(size)}" height="{fmt(size)}" viewBox="0 0 {fmt(size)} {fmt(size)}"
     xmlns="http://www.w3.org/2000/svg">
  <title>java-llama.cpp app-icon background</title>
  <rect width="{fmt(size)}" height="{fmt(size)}" fill="{color}"/>
</svg>
"""


ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
"""


def _background_color_xml(color: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<resources>\n"
        f'    <color name="ic_launcher_background">{color}</color>\n'
        "</resources>\n"
    )


def write_android_set(config, out_dir: Path, fill: str, background: str) -> None:
    """Write the complete drop-in Android icon tree under ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- SVG masters -----------------------------------------------------
    full_svg = build_icon_svg(config, 1024, fill, background, FULL_FRAC)
    fg_svg = build_icon_svg(config, 1024, fill, "none", SAFE_FRAC)
    bg_svg = _solid_svg(1024, background)
    full_path = out_dir / "ic_launcher.svg"
    fg_path = out_dir / "ic_launcher_foreground.svg"
    (full_path).write_text(full_svg, encoding="utf-8")
    (fg_path).write_text(fg_svg, encoding="utf-8")
    (out_dir / "ic_launcher_background.svg").write_text(bg_svg, encoding="utf-8")

    # --- Play Store 512 --------------------------------------------------
    logolib.render_png(full_path, out_dir / "ic_launcher-512.png", 512)

    # --- Legacy + adaptive-foreground density PNGs -----------------------
    res = out_dir / "res"
    for bucket, px in LEGACY_PX.items():
        d = res / f"mipmap-{bucket}"
        d.mkdir(parents=True, exist_ok=True)
        logolib.render_png(full_path, d / "ic_launcher.png", px)
    for bucket, px in FOREGROUND_PX.items():
        d = res / f"mipmap-{bucket}"
        d.mkdir(parents=True, exist_ok=True)
        logolib.render_png(fg_path, d / "ic_launcher_foreground.png", px)

    # --- Adaptive descriptor + background colour resource ----------------
    anydpi = res / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(ADAPTIVE_XML, encoding="utf-8")
    values = res / "values"
    values.mkdir(parents=True, exist_ok=True)
    (values / "ic_launcher_background.xml").write_text(
        _background_color_xml(background), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-c", "--config", type=Path, help="JSON file overriding defaults")
    parser.add_argument("--fill", help="J colour (default: config 'orange')")
    parser.add_argument("--background", help="Square background, or 'none' (default: config 'background')")
    parser.add_argument("--content-frac", type=float, default=FULL_FRAC,
                        help="J size as a fraction of the square (single-file mode)")
    parser.add_argument("--size", type=float, default=1024, help="SVG canvas size (single-file mode)")
    parser.add_argument("-o", "--output", type=Path, default=Path("app-icon.svg"))
    parser.add_argument("--png", type=Path, help="Also rasterise a PNG (needs 'pip install resvg-py')")
    parser.add_argument("--png-size", type=int, default=512, help="PNG edge length in px")
    parser.add_argument("--android-set", type=Path,
                        help="Write the full drop-in Android res/ tree into this directory")
    args = parser.parse_args()

    config = logolib.load_config(jl.LogoConfig, args.config)
    fill = args.fill or config.orange
    background = args.background or config.background

    if args.android_set:
        write_android_set(config, args.android_set, fill, background)
        return

    svg = build_icon_svg(config, args.size, fill, background, args.content_frac)
    args.output.write_text(svg, encoding="utf-8")
    if args.png:
        logolib.render_png(args.output, args.png, args.png_size)


if __name__ == "__main__":
    main()
