#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Fast, dependency-light QA preview of the shard icon (PIL only, no font).

Renders the icon geometry from generate_java_llama_logo.build_icon so the shape
can be checked visually without an SVG/font renderer. Use this to iterate the
"does it read as a J?" question; use a browser for the final font-accurate SVG.

    python preview_icon.py --config java-llama-logo-config.json -o preview.png
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

import generate_java_llama_logo as gen


def _round_polygon(points, round_map, samples=20):
    """Return a densified point list with rounded corners (mirrors the SVG)."""
    n = len(points)
    out = []

    def lerp(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    def cut(i, r, toward):
        p, q = points[i], points[toward]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy) or 1.0
        r = min(r, length * 0.5)
        return (p[0] + dx / length * r, p[1] + dy / length * r)

    for i in range(n):
        r = round_map.get(i, 0)
        if r > 0:
            a = cut(i, r, (i - 1) % n)
            b = cut(i, r, (i + 1) % n)
            out.append(a)
            for s in range(1, samples):
                t = s / samples
                p0 = lerp(a, points[i], t)
                p1 = lerp(points[i], b, t)
                out.append(lerp(p0, p1, t))
            out.append(b)
        else:
            out.append(points[i])
    return out


def render(config_path, out_path, scale=1.2, margin=60):
    c = gen.load_config(Path(config_path) if config_path else None)
    shards = gen.build_icon(c)

    polys = [_round_polygon(s["points"], s["round"]) for s in shards]
    allpts = [p for poly in polys for p in poly]
    minx = min(p[0] for p in allpts) - margin
    maxx = max(p[0] for p in allpts) + margin
    miny = min(p[1] for p in allpts) - margin
    maxy = max(p[1] for p in allpts) + margin

    W = int((maxx - minx) * scale)
    H = int((maxy - miny) * scale)
    img = Image.new("RGB", (W, H), (17, 17, 17))
    d = ImageDraw.Draw(img)

    def T(p):
        return ((p[0] - minx) * scale, (p[1] - miny) * scale)

    fill = tuple(int(c.white.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    for poly in polys:
        d.polygon([T(p) for p in poly], fill=fill)

    img.save(out_path)
    print(f"wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", default="java-llama-logo-config.json")
    ap.add_argument("-o", "--output", default="preview_icon.png")
    ap.add_argument("--scale", type=float, default=1.2)
    args = ap.parse_args()
    render(args.config, args.output, scale=args.scale)
