#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bernard Ladenthin <bernard.ladenthin@gmail.com>
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Tests for logolib.py and the three generators.

The committed SVGs, PNGs and the Android icon set are the generators' output for the committed
configs, so each is regenerated here and compared byte for byte (PNGs pixel for pixel): a change
to a generator that moves the logo shows up as a failing test, not as a surprise at the next
regeneration. The outlined SVGs need fontTools, the PNGs resvg-py; without them those tests are
skipped, unless LOGO_TESTS_REQUIRE_ALL=1 (set in CI) turns the skip into a failure.

Run from this directory:

    python -m unittest discover -p "test_*.py"
"""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import generate_app_icon as app  # noqa: E402
import generate_java_llama_logo as jl  # noqa: E402
import generate_srcmorph_logo as sm  # noqa: E402
import logolib  # noqa: E402

REQUIRE_ALL = os.environ.get("LOGO_TESTS_REQUIRE_ALL") == "1"

JAVA_LLAMA = (jl, jl.LogoConfig, "java-llama-logo-config.json", "java-llama-cpp")
SRCMORPH = (sm, sm.SrcmorphConfig, "srcmorph-logo-config.json", "srcmorph")
LOGOS = (JAVA_LLAMA, SRCMORPH)

# The committed PNGs are 3000 px wide.
PNG_WIDTH = 3000


def need(module: str) -> None:
    """Skip the test without ``module``, or fail when every test must run."""
    try:
        importlib.import_module(module)
    except ImportError:
        if REQUIRE_ALL:
            raise
        raise unittest.SkipTest(f"{module} is not installed")


def run(*args: str) -> subprocess.CompletedProcess:
    """Run one of the scripts here as a user would, from this directory."""
    result = subprocess.run([sys.executable, *args], cwd=HERE, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(f"{' '.join(args)} exited {result.returncode}:\n{result.stderr}")
    return result


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_same_pixels(test: unittest.TestCase, expected: Path, actual: Path) -> None:
    from PIL import Image, ImageChops

    with Image.open(expected) as a, Image.open(actual) as b:
        test.assertEqual(a.size, b.size, actual.name)
        diff = ImageChops.difference(a.convert("RGBA"), b.convert("RGBA"))
        test.assertIsNone(diff.getbbox(), f"{actual.name} differs from {expected.name}")


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class LogolibTest(TempDirTest):
    def test_fmt_writes_integers_without_a_point_and_trims_decimals(self):
        self.assertEqual(logolib.fmt(3), "3")
        self.assertEqual(logolib.fmt(3.0), "3")
        self.assertEqual(logolib.fmt(-12.0), "-12")
        self.assertEqual(logolib.fmt(2.5), "2.5")
        self.assertEqual(logolib.fmt(1.25), "1.25")
        self.assertEqual(logolib.fmt(1 / 3), "0.333")
        self.assertEqual(logolib.fmt(2.0004), "2")

    def test_clamp01(self):
        self.assertEqual(logolib.clamp01(-0.5), 0.0)
        self.assertEqual(logolib.clamp01(0.25), 0.25)
        self.assertEqual(logolib.clamp01(7), 1.0)

    def test_load_config_without_a_file_is_the_defaults(self):
        for _, cls, _, _ in LOGOS:
            self.assertEqual(logolib.load_config(cls, None), cls())

    def test_load_config_overrides_only_what_the_file_names(self):
        path = self.tmp / "partial.json"
        path.write_text(json.dumps({"white": "#123456"}), encoding="utf-8")
        config = logolib.load_config(jl.LogoConfig, path)
        self.assertEqual(config, replace(jl.LogoConfig(), white="#123456"))

    def test_load_config_refuses_an_unknown_key_by_name(self):
        path = self.tmp / "bad.json"
        path.write_text(json.dumps({"white": "#FFFFFF", "no_such_key": 1}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "no_such_key"):
            logolib.load_config(jl.LogoConfig, path)

    def test_the_committed_configs_load(self):
        for _, cls, config_name, _ in LOGOS:
            self.assertNotEqual(logolib.load_config(cls, HERE / config_name), cls(), config_name)

    def test_a_written_default_config_loads_back_as_the_defaults(self):
        for _, cls, _, _ in LOGOS:
            path = self.tmp / f"{cls.__name__}.json"
            logolib.write_default_config(cls, path)
            self.assertEqual(logolib.load_config(cls, path), cls())

    def test_the_embedded_font_rule_carries_the_family_and_the_font(self):
        rule = logolib.font_face_rule("", "Martian Mono", 400)
        self.assertTrue(rule.startswith("@font-face {"))
        self.assertIn("font-family: 'Martian Mono'", rule)
        self.assertIn("url(data:font/ttf;base64,", rule)

    def test_a_missing_font_stops_with_its_path(self):
        missing = self.tmp / "missing.ttf"
        with self.assertRaises(SystemExit) as raised:
            logolib.font_face_rule(str(missing), "X", 400)
        self.assertIn(str(missing), str(raised.exception))

    def test_text_outlines_advance_by_the_monospaced_width(self):
        need("fontTools")
        d, end_x = logolib.text_to_path_d("ab", 1000, 0, 0)
        self.assertTrue(d)
        self.assertAlmostEqual(end_x, 2 * logolib.MM_ADVANCE)
        _, spaced_end = logolib.text_to_path_d("ab", 1000, 0, 0, letter_spacing=10)
        self.assertAlmostEqual(spaced_end, end_x + 20)


class CommittedOutputTest(TempDirTest):
    """The files in this directory are what the generators write for the committed configs."""

    def test_the_generated_svgs_are_the_generators_output(self):
        for module, cls, config_name, stem in LOGOS:
            config = logolib.load_config(cls, HERE / config_name)
            svg = module.build_svg(config)
            ET.fromstring(svg)
            self.assertEqual(svg, read(HERE / f"{stem}-generated.svg"), stem)

    def test_the_outlined_svgs_are_the_generators_output(self):
        need("fontTools")
        for module, cls, config_name, stem in LOGOS:
            config = replace(logolib.load_config(cls, HERE / config_name), outline_text=True)
            svg = module.build_svg(config)
            ET.fromstring(svg)
            self.assertNotIn("<text", svg, stem)
            self.assertNotIn("@font-face", svg, stem)
            self.assertEqual(svg, read(HERE / f"{stem}-outlined.svg"), stem)

    def test_the_command_lines_write_the_committed_svgs(self):
        for module, _, config_name, stem in LOGOS:
            out = self.tmp / f"{stem}.svg"
            run(Path(module.__file__).name, "-c", config_name, "-o", str(out))
            self.assertEqual(read(out), read(HERE / f"{stem}-generated.svg"), stem)

    def test_the_command_lines_write_a_default_config_that_loads_back(self):
        for module, cls, _, stem in LOGOS:
            out = self.tmp / f"{stem}-default.json"
            run(Path(module.__file__).name, "--write-default-config", str(out))
            self.assertEqual(logolib.load_config(cls, out), cls(), stem)

    def test_the_committed_pngs_are_the_generators_output(self):
        need("resvg_py")
        for module, _, config_name, stem in LOGOS:
            png = self.tmp / f"{stem}.png"
            run(Path(module.__file__).name, "-c", config_name, "-o", str(self.tmp / f"{stem}.svg"),
                "--png", str(png), "--png-width", str(PNG_WIDTH))
            assert_same_pixels(self, HERE / f"{stem}.png", png)

    def test_the_preview_command_line_runs(self):
        out = self.tmp / "preview.png"
        result = run("preview_icon.py", "-c", "java-llama-logo-config.json", "-o", str(out))
        self.assertIn("wrote", result.stdout)
        self.assertTrue(out.is_file())


class AppIconTest(TempDirTest):
    def test_the_single_icon_is_the_committed_launcher_svg(self):
        config = logolib.load_config(jl.LogoConfig, HERE / "java-llama-logo-config.json")
        svg = app.build_icon_svg(config, 1024, config.orange, config.background, app.FULL_FRAC)
        self.assertEqual(svg, read(HERE / "app-icon" / "ic_launcher.svg"))
        out = self.tmp / "app-icon.svg"
        run("generate_app_icon.py", "-c", "java-llama-logo-config.json", "-o", str(out))
        self.assertEqual(read(out), svg)

    def test_the_android_set_is_the_committed_one(self):
        need("resvg_py")
        out = self.tmp / "app-icon"
        run("generate_app_icon.py", "-c", "java-llama-logo-config.json", "--android-set", str(out))
        committed = HERE / "app-icon"
        expected = sorted(p.relative_to(committed) for p in committed.rglob("*")
                          if p.is_file() and p.name != "README.md")
        written = sorted(p.relative_to(out) for p in out.rglob("*") if p.is_file())
        self.assertEqual(written, expected)
        for rel in written:
            if rel.suffix == ".png":
                assert_same_pixels(self, committed / rel, out / rel)
            else:
                self.assertEqual(read(out / rel), read(committed / rel), str(rel))

    def test_the_adaptive_foreground_stays_inside_the_safe_zone(self):
        # An adaptive icon's foreground is masked to a circle; only the central 66 dp of its
        # 108 dp canvas are always visible. SAFE_FRAC is chosen so the J's farthest ink stays
        # inside that circle.
        need("resvg_py")
        from PIL import Image

        config = logolib.load_config(jl.LogoConfig, HERE / "java-llama-logo-config.json")
        svg = self.tmp / "foreground.svg"
        svg.write_text(app.build_icon_svg(config, 1024, config.orange, "none", app.SAFE_FRAC),
                       encoding="utf-8")
        size = 432
        png = self.tmp / "foreground.png"
        logolib.render_png(svg, png, size)
        with Image.open(png) as image:
            alpha = image.convert("RGBA").getchannel("A")
            centre = (size - 1) / 2
            radius = size * 66 / 108 / 2
            inked = [(x, y) for y in range(size) for x in range(size) if alpha.getpixel((x, y)) > 0]
        self.assertTrue(inked, "the foreground draws the J")
        farthest = max(((x - centre) ** 2 + (y - centre) ** 2) ** 0.5 for x, y in inked)
        self.assertLess(farthest, radius)


if __name__ == "__main__":
    unittest.main()
