#!/usr/bin/env python3
"""Stop Point 2: Generate morph Lottie JSON files and HTML viewer.

Produces:
- morph_3_8.json — digit 3 morphs into digit 8
- morph_0_8.json
- morph_4_9.json
- viewer.html — drag-drop or auto-loads the Lottie files
"""

from pathlib import Path

from glyph_animator.lottie.builder import (
    LottieBuilder,
    _fill,
    animated_shape,
    shape_group,
)
from glyph_animator.lottie.easing import ORGANIC
from glyph_animator.lottie.keyframes import shape_keyframe
from glyph_animator.lottie.paths import contour_to_lottie_path, offset_contour
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline, _contour_to_tuples

FONT_PATH = Path.home() / "Projects/greenwood-clock/components/fonts/fonts/Nunito-ExtraBold.ttf"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "lottie"


def generate_morph(pipeline, char_a, char_b):
    """Generate a morph Lottie animation for one digit pair."""
    pairs = pipeline.process_pair(char_a, char_b)
    glyph_a = pipeline.process_glyph(char_a)
    glyph_b = pipeline.process_glyph(char_b)

    ba, bb = glyph_a.bounds, glyph_b.bounds
    x_min = min(ba.x_min, bb.x_min)
    y_min = min(ba.y_min, bb.y_min)
    x_max = max(ba.x_max, bb.x_max)
    y_max = max(ba.y_max, bb.y_max)

    margin = 50
    w = int(x_max - x_min + 2 * margin)
    h = int(y_max - y_min + 2 * margin)
    ox = margin - x_min
    oy = margin - y_min

    hold_before = 15
    morph_duration = 60
    hold_after = 30
    total = hold_before + morph_duration + hold_after

    builder = LottieBuilder(f"morph-{char_a}-{char_b}", w, h, fps=30, frames=total)

    shape_items = []
    for pi, pair in enumerate(pairs):
        ca = _contour_to_tuples(pair.contour_a)
        cb = _contour_to_tuples(pair.contour_b)
        ca_canvas = offset_contour(ca, ox, oy, h)
        cb_canvas = offset_contour(cb, ox, oy, h)

        path_a = contour_to_lottie_path(ca_canvas)
        path_b = contour_to_lottie_path(cb_canvas)

        kfs = [
            shape_keyframe(0, path_a, path_a),
            shape_keyframe(hold_before, path_a, path_b, easing=ORGANIC),
            shape_keyframe(hold_before + morph_duration, path_b),
        ]
        shape_items.append(animated_shape(f"path-{pi}", kfs))

    shape_items.append(_fill([0.95, 0.95, 0.95, 1], rule=1))
    group = shape_group("glyph", shape_items)
    builder.add_shape_layer("morph", [group])
    builder.add_background()
    return builder


def generate_viewer_html(json_files):
    """Generate an HTML viewer that loads generated Lottie files."""
    buttons = "\n".join(
        f"        <button onclick=\"load('{f.name}')\">{f.stem}</button>" for f in json_files
    )
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Glyph Animator — Lottie Viewer</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<style>
body {{ background: #1a1a2e; color: #eee; font-family: sans-serif; text-align: center; }}
#player {{ width: 400px; height: 400px; margin: 20px auto;
  background: #16213e; border-radius: 8px; }}
button {{ margin: 4px; padding: 8px 16px; background: #0f3460; color: #e94560;
         border: 1px solid #e94560; border-radius: 4px; cursor: pointer; }}
button:hover {{ background: #e94560; color: #1a1a2e; }}
h1 {{ color: #e94560; }}
</style>
</head>
<body>
<h1>Glyph Animator — Morph Preview</h1>
<div>
{buttons}
</div>
<div id="player"></div>
<script>
let anim = null;
function load(file) {{
    if (anim) anim.destroy();
    anim = lottie.loadAnimation({{
        container: document.getElementById('player'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: file
    }});
}}
// Auto-load first
load('{json_files[0].name if json_files else ""}');
</script>
</body>
</html>"""


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pipeline = GlyphPipeline(FONT_PATH, segment_count=64)

    test_pairs = [("3", "8"), ("0", "8"), ("4", "9"), ("2", "5")]
    json_files = []

    for char_a, char_b in test_pairs:
        print(f"Generating morph: '{char_a}' → '{char_b}'...", end="")
        builder = generate_morph(pipeline, char_a, char_b)
        out_path = OUTPUT_DIR / f"morph_{char_a}_{char_b}.json"
        builder.save(out_path)
        size = out_path.stat().st_size
        print(f" {size:,}B")
        json_files.append(out_path)

    viewer_path = OUTPUT_DIR / "viewer.html"
    viewer_path.write_text(generate_viewer_html(json_files))
    print(f"\nViewer: {viewer_path}")
    print(f"Serve with: cd {OUTPUT_DIR} && python3 -m http.server 8080")


if __name__ == "__main__":
    main()
