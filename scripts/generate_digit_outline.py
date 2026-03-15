#!/usr/bin/env python3
"""Stop Point 3: Generate digit with outline layers as Lottie JSON."""

from pathlib import Path

from glyph_animator.lottie.builder import (
    LottieBuilder,
    _fill,
    _stroke,
    shape_group,
    static_shape,
)
from glyph_animator.lottie.paths import contour_to_lottie_path, offset_contour
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.glyph_renderer import GlyphRenderer

FONT_PATH = Path.home() / "Projects/greenwood-clock/components/fonts/fonts/Nunito-ExtraBold.ttf"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "lottie"


def generate_digit_outline(char, pipeline, renderer):
    """Generate a static digit with filled shape and outline strokes."""
    glyph = pipeline.process_glyph(char)
    rendered = renderer.render(glyph)

    b = glyph.bounds
    margin = 50
    w = int(b.width + 2 * margin)
    h = int(b.height + 2 * margin)
    ox = margin - b.x_min
    oy = margin - b.y_min

    builder = LottieBuilder(f"digit-{char}", w, h, fps=30, frames=90)

    # Outline layers (back to front: thickest first)
    outline_colors = [
        [0.2, 0.5, 0.9, 1],
        [0.3, 0.7, 0.9, 1],
        [0.5, 0.9, 1.0, 1],
    ]
    for i, ol in enumerate(rendered.outline_layers):
        segs = ol.contour.to_tuples()
        canvas_segs = offset_contour(segs, ox, oy, h)
        path = contour_to_lottie_path(canvas_segs)
        color = outline_colors[i % len(outline_colors)]
        items = [static_shape(f"outline-{i}", path), _stroke(color, ol.stroke_width)]
        builder.add_shape_layer(f"outline-{i}", [shape_group(f"ol-{i}", items)])

    # Filled shape (front)
    fill_items = []
    for ci, contour in enumerate(rendered.fitted_contours):
        segs = contour.to_tuples()
        canvas_segs = offset_contour(segs, ox, oy, h)
        path = contour_to_lottie_path(canvas_segs)
        fill_items.append(static_shape(f"fill-{ci}", path))
    fill_items.append(_fill([0.95, 0.95, 0.95, 1], rule=1))
    builder.add_shape_layer("fill", [shape_group("fill-grp", fill_items)], ip=0)

    builder.add_background()
    return builder


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pipeline = GlyphPipeline(FONT_PATH, segment_count=64)
    renderer = GlyphRenderer(n_outline_layers=3, n_arc_samples=100)

    for char in "3805":
        print(f"Generating digit '{char}' with outlines...", end="")
        builder = generate_digit_outline(char, pipeline, renderer)
        out_path = OUTPUT_DIR / f"digit_{char}_outline.json"
        builder.save(out_path)
        print(f" {out_path.stat().st_size:,}B")

    print(f"\nServe with: cd {OUTPUT_DIR} && python3 -m http.server 8080")


if __name__ == "__main__":
    main()
