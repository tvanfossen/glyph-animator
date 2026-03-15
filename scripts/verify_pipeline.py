#!/usr/bin/env python3
"""Visual verification: render pipeline output as overlay PNGs.

Generates:
- Per-digit: original contours (red) vs resampled (green) with equidistant points (yellow)
- Per-pair: morph at α=0, 0.25, 0.5, 0.75, 1.0
"""

from pathlib import Path

from PIL import Image, ImageDraw

from glyph_animator.algorithms.curves import eval_cubic
from glyph_animator.algorithms.matching import morph_contours
from glyph_animator.font.extractor import FontExtractor
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline, _contour_to_tuples

FONT_PATH = Path.home() / "Projects/greenwood-clock/components/fonts/fonts/Nunito-ExtraBold.ttf"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "verify"
SIZE = 400
PAD = 40


def _transform(bounds, x, y):
    available = SIZE - 2 * PAD
    scale = min(available / bounds.width, available / bounds.height)
    px = PAD + (x - bounds.x_min) * scale
    py = PAD + (bounds.y_max - y) * scale
    return (px, py)


def _draw_contour(draw, contour_segs, bounds, color, width=2):
    for seg in contour_segs:
        pts = [_transform(bounds, *eval_cubic(*seg, t / 30)) for t in range(31)]
        draw.line(pts, fill=color, width=width)


def render_digit(char, pipeline, extractor, out_dir=None):
    """Render original vs resampled for one digit."""
    out_dir = out_dir or OUTPUT_DIR
    raw = extractor.extract_glyph(char)
    resampled = pipeline.process_glyph(char)

    img = Image.new("RGBA", (SIZE, SIZE), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 5), f"'{char}' original(red) resampled(green)", fill=(200, 200, 200))

    for contour in raw.contours:
        _draw_contour(
            draw, [s.as_tuples() for s in contour.segments], raw.bounds, (255, 60, 60), 3
        )

    for contour in resampled.contours:
        segs = [s.as_tuples() for s in contour.segments]
        _draw_contour(draw, segs, raw.bounds, (60, 255, 60), 2)
        for seg in segs:
            px, py = _transform(raw.bounds, *seg[0])
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 0))

    path = out_dir / f"digit_{char}.png"
    img.save(str(path))
    return path


def render_morph_strip(char_a, char_b, pipeline, out_dir=None):
    """Render morph at 5 alpha values as a horizontal strip."""
    out_dir = out_dir or OUTPUT_DIR
    pairs = pipeline.process_pair(char_a, char_b)
    glyph_a = pipeline.process_glyph(char_a)

    alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
    strip = Image.new("RGBA", (SIZE * len(alphas), SIZE), (30, 30, 30, 255))

    for ai, alpha in enumerate(alphas):
        img = Image.new("RGBA", (SIZE, SIZE), (30, 30, 30, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 5), f"'{char_a}'→'{char_b}' α={alpha:.2f}", fill=(200, 200, 200))

        for pair in pairs:
            ca = _contour_to_tuples(pair.contour_a)
            cb = _contour_to_tuples(pair.contour_b)
            morphed = morph_contours(ca, cb, alpha)
            _draw_contour(draw, morphed, glyph_a.bounds, (100, 200, 255), 2)

        strip.paste(img, (ai * SIZE, 0))

    path = out_dir / f"morph_{char_a}_{char_b}.png"
    strip.save(str(path))
    return path


FONTS = {
    "nunito": FONT_PATH,
    "montserrat": Path.home() / ".local/share/fonts/Montserrat-Bold.ttf",
}


def run_font(name, font_path):
    """Run full verification for one font."""
    font_dir = OUTPUT_DIR / name
    font_dir.mkdir(parents=True, exist_ok=True)

    extractor = FontExtractor(font_path)
    pipeline = GlyphPipeline(font_path, segment_count=64)

    print(f"\n=== {name} ({font_path.name}) ===")
    print("Digit overlays...")
    for char in "0123456789":
        path = render_digit(char, pipeline, extractor, font_dir)
        print(f"  {path.name}")

    print("Morph strips...")
    test_pairs = [("3", "8"), ("0", "8"), ("1", "7"), ("4", "9")]
    for a, b in test_pairs:
        path = render_morph_strip(a, b, pipeline, font_dir)
        print(f"  {path.name}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, font_path in FONTS.items():
        if not font_path.exists():
            print(f"Skipping {name}: {font_path} not found")
            continue
        run_font(name, font_path)

    print(f"\nOutput: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
