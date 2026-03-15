#!/usr/bin/env python3
"""Render sample shapes (daisy, leaf, tendril) to PNG for visual verification."""

from pathlib import Path

from PIL import Image, ImageDraw

from glyph_animator.algorithms.shapes import DaisyGenerator, LeafGenerator, TendrilGenerator

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "shapes"
SIZE = 200
CX, CY = SIZE // 2, SIZE // 2


def _draw_ellipse(draw, item, cx, cy):
    """Draw a Lottie ellipse shape item."""
    px, py = item["p"]["k"]
    sx, sy = item["s"]["k"]
    x0 = cx + px - sx / 2
    y0 = cy + py - sy / 2
    draw.ellipse([x0, y0, x0 + sx, y0 + sy], fill=(200, 100, 150, 200))


def render_generator(gen, name, count=6):
    """Render several instances from a generator into a strip."""
    strip = Image.new("RGBA", (SIZE * count, SIZE), (30, 30, 30, 255))

    for idx in range(count):
        img = Image.new("RGBA", (SIZE, SIZE), (30, 30, 30, 255))
        draw = ImageDraw.Draw(img)
        draw.text((5, 5), f"{name} #{idx}", fill=(200, 200, 200))

        items = gen.generate(idx)
        for item in items:
            if item.get("ty") == "el":
                _draw_ellipse(draw, item, CX, CY)

        strip.paste(img, (idx * SIZE, 0))

    path = OUTPUT_DIR / f"{name}.png"
    strip.save(str(path))
    return path


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for gen, name in [
        (DaisyGenerator(), "daisy"),
        (LeafGenerator(), "leaf"),
        (TendrilGenerator(), "tendril"),
    ]:
        path = render_generator(gen, name)
        print(f"  {path.name}")

    print(f"\nOutput: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
