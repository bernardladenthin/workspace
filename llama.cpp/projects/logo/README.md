# Logo generators — llama.cpp-style brand family

Two parameterised generators sharing one visual language (dark `#111`, Martian
Mono wordmark, orange accent). The wordmark ships two ways: as **real `<text>`
with the font embedded** (default — editable, selectable) or, with
`--outline-text`, as **`<path>` outlines** (font-independent, ~5× smaller — see
[Outlined wordmarks](#outlined-wordmarks---outline-text)):

- **java-llama.cpp** — a 3-shard **"J"** icon (small hook top, stem, hook
  bottom, flush right edge) in the style of the
  [llama.cpp](https://github.com/ggml-org/llama.cpp) mark.
- **srcmorph** — no separate icon; the wordmark itself is the logo, and the
  **"m" in "morph"** is blurred/smeared (it "morphs").

## Files

| File | Purpose |
|---|---|
| `logolib.py` | Shared base: `BaseConfig` (canvas/font fields), font embedding, text→path outlining (`text_to_path_d`), config load/write, PNG export, Martian Mono metrics, `fmt`. |
| `generate_java_llama_logo.py` | java-llama.cpp generator (shard-J geometry + wordmark). |
| `java-llama-logo-config.json` | Config for the java-llama.cpp logo. |
| `generate_srcmorph_logo.py` | srcmorph generator (wordmark + blurred m-in-"morph"). |
| `srcmorph-logo-config.json` | Config for the srcmorph logo. |
| `preview_icon.py` | Fast **shard-icon** preview (PIL, no font) — for J-shape iteration. |
| `generate_app_icon.py` | Square **Android app icon** from the shard-J (full set via `--android-set`); see [`app-icon/`](app-icon/README.md). |
| `MartianMono-Regular.ttf` | Wordmark font (OFL-1.1), embedded into the SVG as base64. |
| `*-generated.svg` / `*.png` | Generated output (embedded-font wordmark). |
| `*-outlined.svg` | Generated output with the wordmark as `<path>` outlines (`--outline-text`) — no embedded font, no `<text>`. |

**Font:** [Martian Mono](https://github.com/evilmartians/mono) by the Martian
Mono Project Authors (Evil Martians), licensed under the SIL Open Font License
1.1 (see `LICENSES/OFL-1.1.txt` at the repo root). Only the Regular weight is
bundled; download the family from the link for other weights.

> PNG export uses [`resvg-py`](https://pypi.org/project/resvg-py/) (`pip install
> resvg-py`) — a self-contained renderer that honours the embedded font. The SVG
> is the master; PNG is a convenience export.
>
> **Structure:** both generators share `logolib.py` (identical infrastructure +
> the `BaseConfig` dataclass). Each generator keeps its own config subclass and
> icon geometry, so the two logos stay fully independent. Each config JSON's keys
> match its dataclass fields (base fields included via inheritance).

## Usage

```bash
# SVG only
python generate_java_llama_logo.py -c java-llama-logo-config.json -o java-llama-cpp-generated.svg

# SVG + PNG in one go (needs: pip install resvg-py)
python generate_java_llama_logo.py -c java-llama-logo-config.json \
    -o java-llama-cpp-generated.svg --png java-llama-cpp.png --png-width 2250

# Write a fresh default config to edit
python generate_java_llama_logo.py --write-default-config myconfig.json

# Font-independent wordmark: <path> outlines instead of embedded font + <text>
python generate_java_llama_logo.py -c java-llama-logo-config.json \
    --outline-text -o java-llama-cpp-outlined.svg

# Construction anchors overlay
python generate_java_llama_logo.py -c java-llama-logo-config.json -o debug.svg --debug

# Fast icon-shape preview while tuning geometry (no font needed)
python preview_icon.py -c java-llama-logo-config.json -o preview_icon.png

# Square Android app icon (full drop-in res/ set) from the shard-J
python generate_app_icon.py -c java-llama-logo-config.json --android-set app-icon

# srcmorph — same flags (including --outline-text)
python generate_srcmorph_logo.py -c srcmorph-logo-config.json \
    -o srcmorph-generated.svg --png srcmorph.png
python generate_srcmorph_logo.py -c srcmorph-logo-config.json \
    --outline-text -o srcmorph-outlined.svg
python generate_srcmorph_logo.py --write-default-config srcmorph-logo-config.json
```

## Outlined wordmarks (`--outline-text`)

By default the wordmark is real `<text>` with `MartianMono-Regular.ttf`
base64-embedded via `@font-face`. That blob is ~64 KB — about 98% of each
generated SVG — because it ships the *whole* font. `--outline-text` instead
converts only the glyphs actually used into `<path>` outlines (via fontTools'
`text_to_path_d` in `logolib.py`), so the file drops to ~13–16 KB and needs no
font at all. The `srcmorph` blur is preserved: the `feGaussianBlur` filters move
from the `<text>` onto the outlined groups (filters work on any element).

| | Embedded font (default) | `--outline-text` |
|---|---|---|
| Wordmark markup | `<text>` + `@font-face` | `<path>` only |
| Self-contained / portable | ✅ | ✅ |
| Text selectable / restyleable / editable | ✅ | ❌ (frozen geometry) |
| Font binary redistributed in the file | yes (OFL-1.1, permitted) | no |
| Survives renderers that strip `<style>`/`@font-face` | ❌ | ✅ |
| File size | ~65–71 KB | ~13–16 KB |

Use the **default** when the SVG is a working master you may re-letter or when
selectable text matters; use **`--outline-text`** for distribution — smaller,
font-independent, and robust in sanitizing renderers. Outlining needs
[`fonttools`](https://pypi.org/project/fonttools/) (`pip install fonttools`); the
default text mode does not.

## How the java-llama.cpp icon is built

The **J** is three slanted shards sharing one italic `shear`. Their right edges
all sit on the stem's slanted "spine" line, so when the icon is italic the cap
and hook are offset **along the angle** (offset = `shear` × height) instead of
being right-flush — which keeps the slant consistent:

- `j-cap`  — upper stem slab (rounded top-left)
- `j-stem` — the diagonal stem
- `j-hook` — the bottom part. `foot_style: "parallel"` (default) makes it a
  shorter **parallel copy of the stem** (same angle, `foot_height_frac` tall,
  `foot_gap` to the left, centred on the stem's bottom). `foot_style: "hook"`
  makes it the classic horizontal foot instead (via `hook_h` / `hook_extend_left`).

Set `cap_enabled: false` for a **2-shard** J (single stem + hook), which is
closest to the original llama.cpp two-shard mark.

Set `mirror_jl: true` to also draw a mirrored copy of the J (an "L") to its
right — the pair reads as **"JL"** for java-llama (`jl_gap` controls the space
between them). Off by default (single J).

### Key parameters

| Param | Meaning |
|---|---|
| `shear` | Italic slant (dx per dy). 0.16 ≈ upright, 0.30 ≈ strong llama.cpp lean. |
| `stem_w`, `stem_h` | Thickness / height of a stem slab. Bigger `stem_w` = bolder. |
| `cap_h`, `hook_h` | Heights of the top / bottom slabs. |
| `hook_extend_left` | How far the bottom hook reaches left (the J foot). |
| `gap_top`, `gap_bottom` | The two horizontal seam gaps. |
| `cap_corner_radius`, `hook_corner_radius` | Rounded outer corners (llama.cpp feel). |
| `icon_scale` | Overall icon size relative to the wordmark. |

### Layout

With `auto_layout: true` the icon and wordmark are **centred automatically** on
the canvas, `gap` between them. With `fit_cap: true` (default) the icon is scaled
so its height equals a **capital letter** (`fit_cap_em` × font size, 0.8 = cap
height) and it sits on the text **baseline** — so it reads like an uppercase "J"
in the wordmark's font. Set `fit_cap: false` to size via `icon_scale` and centre
on the optical midline instead, or `auto_layout: false` to place everything
manually.

### Wordmark

`java-` is drawn in `orange`, `llama.cpp` in `white`. By default it is **real
`<text>`** with the font embedded (`embed_font: true`); pass `--outline-text` to
emit `<path>` outlines instead (see [Outlined wordmarks](#outlined-wordmarks---outline-text)).

## How the srcmorph "m" is built

There is no icon. The wordmark is drawn as `src` (white) + the leading `m` of
`morph` + `orph` (orange). `morph` is written cleanly; only its `m` **comes in
blurred from the left and sharpens toward the right**, where it joins the sharp
`orph`. A slightly bigger gap sits between `src` and `morph` to hold the m's
left-hand blur trail. Built from N glyph copies whose blur ramps down left→right,
each faded in over a soft, overlapping gradient band (smooth, no slice seams).

### Key parameters

| Param | Meaning |
|---|---|
| `font_size` | Wordmark size (the m scales with it). |
| `max_blur_em` | Blur at the m's **left** edge (fraction of `font_size`). |
| `blur_power` | `>1` keeps more of the m sharp on the right. |
| `fade_to` | Left-edge opacity (`0` = the m emerges from nothing). |
| `directional` | `true` = horizontal smear, `false` = round defocus. |
| `m_layers` | More layers = smoother blur ramp. |
| `space_before_em` | Gap between `src` and `morph` (room for the left trail). |
| `space_after_em` | Gap between the m and `orph` (`0` = clean word). |
| `src_color`, `morph_color` | Wordmark colours (white / orange). |

`auto_layout: true` centres the whole wordmark on the canvas.

## TODO / open

- Optional: light-background variants and square/app-icon crops for both logos.
- Optional: unify the two scripts behind one CLI (`--icon shard-j | morph-m`).
