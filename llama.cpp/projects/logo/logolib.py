#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Shared infrastructure for the logo generators.

Holds everything that is identical across ``generate_java_llama_logo.py`` and
``generate_srcmorph_logo.py``: number formatting, the Martian Mono metrics, font
embedding, config load/write, PNG export, and a ``BaseConfig`` with the common
canvas/font fields. The per-logo geometry and ``build_svg`` stay in each script,
so each logo keeps its own full flexibility.
"""

from __future__ import annotations

import base64
import json
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_FONT = HERE / "MartianMono-Regular.ttf"

# Martian Mono metrics (units per em = 1000).
MM_UPM = 1000.0
MM_ADVANCE = 700.0   # every glyph is monospaced at 0.7 em
MM_CAP = 800.0       # cap height


@dataclass(frozen=True)
class BaseConfig:
    """Fields shared by every logo. Subclasses add colours, geometry, wordmark."""

    # Canvas
    width: float = 7500
    height: float = 2500
    background: str = "#111111"

    # Wordmark font (embedded as base64 so text stays real <text>, no outlines)
    font_family: str = "Martian Mono"
    font_path: str = ""   # empty -> DEFAULT_FONT
    embed_font: bool = True
    font_weight: int = 400
    letter_spacing: float = 0


def fmt(value: float) -> str:
    """Compact number formatting for SVG coordinates."""
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def font_face_rule(font_path: str, family: str, weight: int) -> str:
    """Return the bare ``@font-face { ... }`` rule with the font base64-embedded.

    Callers wrap this in their own ``<defs><style>`` however they like, so the
    exact surrounding markup stays each script's decision.
    """
    path = Path(font_path) if font_path else DEFAULT_FONT
    if not path.exists():
        raise SystemExit(f"Font not found for embedding: {path}")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        f"@font-face {{ font-family: '{family}'; font-style: normal; "
        f"font-weight: {weight}; "
        f"src: url(data:font/ttf;base64,{b64}) format('truetype'); }}"
    )


def load_config(cls, path: Path | None):
    """Load a JSON config into dataclass ``cls`` (unknown keys are rejected)."""
    config = cls()
    if path is None:
        return config
    raw = json.loads(path.read_text(encoding="utf-8"))
    allowed = {f.name for f in fields(cls)}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError(f"Unknown config keys: {', '.join(unknown)}")
    return replace(config, **raw)


def write_default_config(cls, path: Path) -> None:
    path.write_text(
        json.dumps(asdict(cls()), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def render_png(svg_path: Path, out: Path, width: int) -> None:
    """Rasterise an SVG file to PNG via resvg (honours the embedded font)."""
    try:
        import resvg_py  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("PNG export needs: pip install resvg-py") from exc
    out.write_bytes(bytes(resvg_py.svg_to_bytes(svg_path=str(svg_path), width=width)))
