#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Tests for preview_icon.py (needs Pillow, like the script itself).

Run from this directory:

    python -m unittest test_preview_icon
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from PIL import Image  # noqa: E402

import generate_java_llama_logo as gen  # noqa: E402
import logolib  # noqa: E402
import preview_icon  # noqa: E402

CONFIG = HERE / "java-llama-logo-config.json"


class PreviewIconTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _render(self, config_path):
        out = self.tmp / "preview.png"
        preview_icon.render(str(config_path) if config_path else None, out)
        with Image.open(out) as image:
            image.load()
            return image.copy()

    def _white_pixels(self, image, config):
        white = tuple(int(config.white.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        pixels = image.load()
        return sum(1 for y in range(image.height) for x in range(image.width) if pixels[x, y] == white)

    def test_the_shipped_config_renders(self):
        # preview_icon.py called gen.load_config, which the generator never had
        # (workspace issue #74): every run ended in an AttributeError.
        image = self._render(CONFIG)
        config = logolib.load_config(gen.LogoConfig, CONFIG)
        self.assertGreater(image.width, 0)
        self.assertGreater(image.height, 0)
        self.assertGreater(self._white_pixels(image, config), 0, "the shards are drawn")

    def test_the_defaults_render_without_a_config(self):
        image = self._render(None)
        self.assertGreater(self._white_pixels(image, gen.LogoConfig()), 0)

    def test_an_unknown_config_key_is_refused(self):
        bad = self.tmp / "bad.json"
        bad.write_text(json.dumps({"no_such_key": 1}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "no_such_key"):
            preview_icon.render(str(bad), self.tmp / "unused.png")

    def test_the_mirrored_l_is_previewed_like_the_svg_draws_it(self):
        # The SVG draws icon_shards; with mirror_jl the "L" stands right of the J
        # and the preview is wider by it.
        raw = json.loads(CONFIG.read_text(encoding="utf-8"))
        single = dict(raw, mirror_jl=False)
        mirrored = dict(raw, mirror_jl=True)
        paths = []
        for name, values in (("single.json", single), ("mirrored.json", mirrored)):
            path = self.tmp / name
            path.write_text(json.dumps(values), encoding="utf-8")
            paths.append(path)
        one = self._render(paths[0])
        two = self._render(paths[1])
        config = logolib.load_config(gen.LogoConfig, paths[0])
        self.assertGreater(two.width, one.width + config.jl_gap)
        self.assertEqual(two.height, one.height)
        # the "L" is the J mirrored: as many pixels again, up to the rasterization of the edges
        single_white = self._white_pixels(one, config)
        self.assertAlmostEqual(self._white_pixels(two, config), 2 * single_white, delta=0.02 * single_white)


if __name__ == "__main__":
    unittest.main()
