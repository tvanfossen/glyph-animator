#!/usr/bin/env python3
"""Regenerate viewer.html to include all Lottie JSON files in output/lottie/."""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "lottie"


def main():
    json_files = sorted(OUTPUT_DIR.glob("*.json"))
    if not json_files:
        print("No JSON files found in output/lottie/")
        return

    file_list = json.dumps([f.name for f in json_files])

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Glyph Animator — Lottie Viewer</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<style>
body {{ background: #1a1a2e; color: #eee; font-family: sans-serif;
  text-align: center; padding: 20px; }}
#player {{ width: 500px; height: 500px; margin: 20px auto;
  background: #16213e; border-radius: 8px; }}
#buttons {{ max-width: 800px; margin: 0 auto; }}
button {{ margin: 4px; padding: 8px 14px; background: #0f3460;
  color: #e94560; border: 1px solid #e94560;
  border-radius: 4px; cursor: pointer; font-size: 13px; }}
button:hover {{ background: #e94560; color: #1a1a2e; }}
button.active {{ background: #e94560; color: #1a1a2e; }}
h1 {{ color: #e94560; margin-bottom: 5px; }}
p {{ color: #666; margin-top: 0; }}
</style>
</head>
<body>
<h1>Glyph Animator</h1>
<p>{len(json_files)} animations</p>
<div id="buttons"></div>
<div id="player"></div>
<script>
const files = {file_list};
let anim = null;
function load(file) {{
    document.querySelectorAll('button').forEach(
      b => b.classList.remove('active'));
    event.target.classList.add('active');
    if (anim) anim.destroy();
    anim = lottie.loadAnimation({{
        container: document.getElementById('player'),
        renderer: 'svg', loop: true, autoplay: true, path: file
    }});
}}
const container = document.getElementById('buttons');
files.forEach(f => {{
    const btn = document.createElement('button');
    btn.textContent = f.replace('.json', '');
    btn.onclick = () => load(f);
    container.appendChild(btn);
}});
if (files.length > 0) {{
    const first = container.querySelector('button');
    first.classList.add('active');
    load(files[0]);
}}
</script>
</body>
</html>"""

    viewer_path = OUTPUT_DIR / "viewer.html"
    viewer_path.write_text(html)
    print(f"Viewer: {viewer_path}")
    print(f"Files: {', '.join(f.name for f in json_files)}")
    print(f"\ncd {OUTPUT_DIR} && python3 -m http.server 8080")


if __name__ == "__main__":
    main()
