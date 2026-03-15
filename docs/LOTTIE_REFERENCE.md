# Lottie Format Reference

Comprehensive reference for the Lottie (bodymovin) animation format as implemented by
this library. Documents every structural element, format rule, and rendering landmine
discovered during prototype development against lottie-web, rlottie, and ThorVG.

Target format version: **bodymovin v5.7.0**.

---

## 1. File Structure

Every Lottie JSON file is a single object with these top-level fields:

| Field | Type | Description |
|---|---|---|
| `v` | string | Bodymovin version. Use `"5.7.0"`. |
| `nm` | string | Animation name (informational). |
| `ddd` | int | 3D flag. Always `0` for 2D animations. |
| `fr` | int | Frame rate (frames per second). |
| `ip` | int | In-point: first playable frame (usually `0`). |
| `op` | int | Out-point: one past the last playable frame. |
| `w` | int | Canvas width in pixels. |
| `h` | int | Canvas height in pixels. |
| `layers` | array | Ordered array of layer objects. |

```json
{
  "v": "5.7.0",
  "nm": "my-animation",
  "ddd": 0,
  "fr": 30,
  "ip": 0,
  "op": 60,
  "w": 200,
  "h": 260,
  "layers": []
}
```

**Playback range**: frames `ip` through `op - 1`. A 2-second animation at 30fps has
`ip=0, op=60` (frames 0..59).

---

## 2. Layer Ordering

**Index 0 = FRONT (topmost visual). Last index = BACK (bottommost).**

Layers are rendered back-to-front: the last element in the `layers` array is drawn first,
the first element is drawn last (on top). This matches the Photoshop/After Effects
convention where the topmost layer in the timeline panel is the frontmost visual.

```json
{
  "layers": [
    {"nm": "foreground-digit", "...": "drawn LAST (on top)"},
    {"nm": "decorations",      "...": "drawn in middle"},
    {"nm": "background",       "...": "drawn FIRST (behind everything)"}
  ]
}
```

If you want a background layer, append it as the **last** element of the array.

---

## 3. Layer Types

The `ty` field on each layer object determines its type.

### ty=4: Shape Layer

The workhorse. Contains vector shapes (paths, fills, strokes, groups).
This is the only layer type this library generates.

```json
{
  "ty": 4,
  "nm": "digit-layer",
  "sr": 1,
  "ks": {},
  "ao": 0,
  "shapes": [],
  "ip": 0,
  "op": 60,
  "st": 0
}
```

| Field | Type | Description |
|---|---|---|
| `ty` | int | `4` = shape layer. |
| `nm` | string | Layer name. |
| `sr` | number | Time stretch factor. `1` = normal speed. |
| `ks` | object | Layer transform (see section 13). |
| `ao` | int | Auto-orient along motion path. `0` = off. |
| `shapes` | array | Shape items (paths, fills, groups, etc.). |
| `ip` | int | In-point: frame where this layer becomes visible. |
| `op` | int | Out-point: frame where this layer disappears. |
| `st` | int | Start time offset. Usually `0`. |

### ty=0: Precomp Layer

References a pre-composed set of layers (like a nested animation). Not used by this
library but common in After Effects exports.

```json
{
  "ty": 0,
  "nm": "nested-comp",
  "refId": "comp_0",
  "ks": {},
  "ip": 0,
  "op": 60,
  "w": 200,
  "h": 260
}
```

### ty=1: Solid Layer

A solid-color rectangle. Rarely used directly; shape layers with rectangles are more
flexible.

```json
{
  "ty": 1,
  "nm": "solid-bg",
  "sc": "#0a0a14",
  "sw": 200,
  "sh": 260,
  "ks": {},
  "ip": 0,
  "op": 60
}
```

---

## 4. Shape Types

Shape items live inside a shape layer's `shapes` array (or inside a group's `it` array).
The `ty` field is a **string** (not int) for shapes.

### sh: Path

A bezier path. The core building block.

```json
{
  "ty": "sh",
  "nm": "contour-0",
  "ks": {"a": 0, "k": {"c": true, "v": [], "i": [], "o": []}}
}
```

The `ks` field holds either a static or animated value wrapping a path object.
See section 6 for the path format.

### fl: Fill

Fills enclosed paths with a solid color.

```json
{
  "ty": "fl",
  "nm": "fill",
  "c": {"a": 0, "k": [0.95, 0.95, 0.95, 1]},
  "r": 1,
  "o": {"a": 0, "k": 100}
}
```

| Field | Description |
|---|---|
| `c` | Color as `[r, g, b, a]`, each 0.0-1.0. |
| `r` | Fill rule: `1` = non-zero winding, `2` = even-odd. See section 11. |
| `o` | Opacity (0-100). |

### st: Stroke

Strokes along paths.

```json
{
  "ty": "st",
  "nm": "stem-stroke",
  "c": {"a": 0, "k": [0.28, 0.52, 0.24, 1]},
  "w": {"a": 0, "k": 7.0},
  "o": {"a": 0, "k": 100},
  "lc": 2,
  "lj": 2
}
```

| Field | Description |
|---|---|
| `c` | Stroke color `[r, g, b, a]`. |
| `w` | Stroke width. |
| `o` | Opacity (0-100). |
| `lc` | Line cap: `1` = butt, `2` = round, `3` = square. |
| `lj` | Line join: `1` = miter, `2` = round, `3` = bevel. |

### rc: Rectangle

```json
{
  "ty": "rc",
  "nm": "bg-rect",
  "p": {"a": 0, "k": [100, 130]},
  "s": {"a": 0, "k": [200, 260]},
  "r": {"a": 0, "k": 0}
}
```

| Field | Description |
|---|---|
| `p` | Center position `[x, y]`. |
| `s` | Size `[width, height]`. |
| `r` | Corner radius. |

### el: Ellipse

```json
{
  "ty": "el",
  "nm": "pistil",
  "p": {"a": 0, "k": [0, 0]},
  "s": {"a": 0, "k": [6, 6]}
}
```

| Field | Description |
|---|---|
| `p` | Center position `[x, y]`. |
| `s` | Size `[width, height]`. Diameter, not radius. |

### gr: Group

Contains child shape items in an `it` array. **The group transform (`tr`) must be
the LAST item** in the `it` array. See section 12.

```json
{
  "ty": "gr",
  "nm": "glyph-group",
  "it": [
    {"ty": "sh", "nm": "path-0", "...": "..."},
    {"ty": "sh", "nm": "path-1", "...": "..."},
    {"ty": "fl", "nm": "fill", "...": "..."},
    {"ty": "tr", "...": "MUST BE LAST"}
  ]
}
```

### tr: Group Transform

Applied to all sibling items in the parent group. See section 12.

### tm: Trim Paths

Trims a stroke to a percentage range. Useful for "drawing on" animations.

```json
{
  "ty": "tm",
  "nm": "trim",
  "s": {"a": 0, "k": 0},
  "e": {"a": 1, "k": [
    {"t": 0, "s": [0], "e": [100],
     "i": {"x": [0.22], "y": [1]},
     "o": {"x": [0.78], "y": [0]}},
    {"t": 30, "s": [100]}
  ]},
  "o": {"a": 0, "k": 0}
}
```

| Field | Description |
|---|---|
| `s` | Start percentage (0-100). |
| `e` | End percentage (0-100). |
| `o` | Offset in degrees. |

---

## 5. Animated vs Static Values

Every animatable property uses the same wrapper format. The `a` flag determines whether
the value is static or animated.

### Static Value

`a=0`: the `k` field holds the raw value directly.

```json
{"a": 0, "k": [100, 130, 0]}
```

```json
{"a": 0, "k": 50}
```

```json
{"a": 0, "k": {"c": true, "v": [], "i": [], "o": []}}
```

### Animated Value

`a=1`: the `k` field holds an array of keyframe objects.

```json
{"a": 1, "k": [
  {"t": 0, "s": [0, 0, 0], "o": {}, "i": {}, "to": [], "ti": []},
  {"t": 30, "s": [100, 200, 0], "o": {}, "i": {}, "to": [], "ti": []},
  {"t": 60, "s": [100, 200, 0]}
]}
```

**The final keyframe** in a sequence has only `t` and `s` (no easing handles, no end
value). It marks the resting state.

---

## 6. Path Format

Lottie paths are defined by three parallel arrays plus a closed flag:

```json
{
  "c": true,
  "v": [[x0, y0], [x1, y1], ...],
  "i": [[dx0, dy0], [dx1, dy1], ...],
  "o": [[dx0, dy0], [dx1, dy1], ...]
}
```

| Field | Description |
|---|---|
| `c` | `true` for closed paths, `false` for open. |
| `v` | **Vertices**: on-curve anchor points (absolute coordinates). |
| `i` | **In-tangents**: cubic bezier handle arriving at each vertex (**RELATIVE** to vertex). |
| `o` | **Out-tangents**: cubic bezier handle departing each vertex (**RELATIVE** to vertex). |

All three arrays must have the same length.

### Converting from Cubic Bezier Segments

Given a cubic bezier segment with control points `(C0, C1, C2, C3)`:

```
vertex[i]      = C0        (start point of segment i)
out_tangent[i] = C1 - C0   (handle leaving vertex i toward C1)
in_tangent[i]  = C2_prev - C3_prev  (handle arriving at vertex i from previous segment)
```

Where `C2_prev` and `C3_prev` are the third and fourth control points of the
**previous** segment (wrapping around for closed paths).

**CRITICAL: tangents are RELATIVE to their vertex, not absolute coordinates.**

A tangent of `[0, 0]` means "no handle" (the curve degenerates to a straight line at
that vertex).

### Worked Example

Given two cubic bezier segments forming a closed triangle-ish shape:

```
Segment 0: C0=(0,0), C1=(50,0), C2=(100,50), C3=(100,100)
Segment 1: C0=(100,100), C1=(50,100), C2=(0,50), C3=(0,0)
```

The Lottie path is:

```json
{
  "c": true,
  "v": [[0, 0], [100, 100]],
  "i": [[0, 50], [100, 50]],
  "o": [[50, 0], [50, 100]]
}
```

Derivation for vertex 0 `(0, 0)`:
- `v[0]` = C0 of segment 0 = `[0, 0]`
- `o[0]` = C1 - C0 of segment 0 = `[50-0, 0-0]` = `[50, 0]`
- `i[0]` = C2_prev - C3_prev of segment 1 (the previous segment, wrapping) = `[0-0, 50-0]` = `[0, 50]`

Derivation for vertex 1 `(100, 100)`:
- `v[1]` = C0 of segment 1 = `[100, 100]`
- `o[1]` = C1 - C0 of segment 1 = `[50-100, 100-100]` = `[-50, 0]`... wait. Let me be precise:
  - `o[1]` = `[50-100, 100-100]` = `[-50, 0]`
  - `i[1]` = C2 - C3 of segment 0 = `[100-100, 50-100]` = `[0, -50]`

Corrected path:

```json
{
  "c": true,
  "v": [[0, 0], [100, 100]],
  "i": [[0, 50], [0, -50]],
  "o": [[50, 0], [-50, 0]]
}
```

### Code Reference

```python
def contour_to_lottie_path(contour: list[Seg]) -> dict:
    """contour is a list of (C0, C1, C2, C3) tuples."""
    vertices, in_tangents, out_tangents = [], [], []
    n = len(contour)
    for i in range(n):
        c0, c1, _, _ = contour[i]
        _, _, c2_prev, c3_prev = contour[(i - 1) % n]
        vertices.append([c0[0], c0[1]])
        out_tangents.append([c1[0] - c0[0], c1[1] - c0[1]])
        in_tangents.append([c2_prev[0] - c3_prev[0], c2_prev[1] - c3_prev[1]])
    return {"c": True, "v": vertices, "i": in_tangents, "o": out_tangents}
```

---

## 7. Easing Handles -- THE BIG GOTCHA

Lottie keyframes use cubic bezier easing curves defined by `i` (in-handle) and `o`
(out-handle) on each keyframe. The handles map time progression to value progression
in normalized `[0,1] x [0,1]` space.

**The array dimensions of `x` and `y` depend on the property type.** Getting this wrong
produces **silent rendering corruption** -- the animation plays but values are wrong.
No error, no warning.

### 1D Properties: Single-Element Arrays

Properties with a single animated value:
- **Opacity** (0-100 scalar)
- **Rotation** (degrees scalar)
- **Shape morph** (path interpolation is treated as 1D)
- **Trim path start/end** (percentage scalar)

```json
{
  "t": 0,
  "s": [0],
  "e": [100],
  "i": {"x": [0.42], "y": [0]},
  "o": {"x": [0.58], "y": [1]}
}
```

### 2D Properties: Two-Element Arrays

Properties with two or more animated components, each needing independent easing:
- **Position** (`[x, y, z]`)
- **Scale** (`[sx, sy, sz]`)

```json
{
  "t": 0,
  "s": [0, 0, 0],
  "i": {"x": [0.42, 0.42], "y": [0, 0]},
  "o": {"x": [0.58, 0.58], "y": [1, 1]}
}
```

The two array elements correspond to easing for the X and Y components independently.
In practice they are usually the same value, but the format requires two elements.

### What Happens When You Get This Wrong

| Property | Wrong Handle Size | Symptom |
|---|---|---|
| Position with 1D handles | `{"x": [0.42], "y": [0]}` | Jerky motion, Y component ignores easing |
| Opacity with 2D handles | `{"x": [0.42, 0.42], "y": [0, 0]}` | Renderer-dependent: may crash, ignore, or misinterpret |
| Shape with 2D handles | `{"x": [0.42, 0.42], "y": [0, 0]}` | ThorVG renders garbage; lottie-web silently corrupts interpolation |

### Easing Presets

```python
# Linear (no easing)
out_handle = {"x": [1.0], "y": [1.0]}  # 1D
in_handle  = {"x": [0.0], "y": [0.0]}

# Ease-in-out (smooth start and stop)
out_handle = {"x": [0.42], "y": [0]}   # 1D
in_handle  = {"x": [0.58], "y": [1]}

# Organic (asymmetric: slow start, fast middle, gentle settle)
out_handle = {"x": [0.25], "y": [0.1]}  # 1D
in_handle  = {"x": [0.75], "y": [0.9]}

# Elastic (overshoot)
out_handle = {"x": [0.5], "y": [0.0]}   # 1D
in_handle  = {"x": [0.3], "y": [1.4]}   # y > 1.0 = overshoot
```

---

## 8. Position Keyframes: Spatial Tangents (to/ti)

Position is a **spatial** property. In addition to temporal easing (`i`/`o`), position
keyframes support spatial tangents (`to`/`ti`) that define curved motion paths between
keyframes.

**Without `to`/`ti`, motion between keyframes is strictly linear (straight line),
which looks mechanical and jerky.** Even for transitions that are conceptually "smooth,"
the lack of spatial tangents makes them visibly robotic.

```json
{
  "t": 0,
  "s": [50, 200, 0],
  "to": [16.67, -33.33, 0],
  "ti": [-16.67, 33.33, 0],
  "i": {"x": [0.42, 0.42], "y": [0, 0]},
  "o": {"x": [0.58, 0.58], "y": [1, 1]}
}
```

| Field | Description |
|---|---|
| `s` | Start position `[x, y, z]` at this keyframe. |
| `to` | Spatial out-tangent: direction of the motion curve leaving this keyframe. |
| `ti` | Spatial in-tangent: direction of the motion curve arriving at the **next** keyframe. |
| `i`/`o` | Temporal easing (must be 2D format, see section 7). |

### Computing to/ti from Motion Direction

A reasonable default for smooth curved motion:

```python
dx = next_x - current_x
dy = next_y - current_y
to = [dx / 6, dy / 6, 0]   # 1/6 of displacement
ti = [-dx / 6, -dy / 6, 0]  # symmetric
```

The division by 6 approximates a smooth cubic bezier arc. Larger values produce wider
curves; `[0, 0, 0]` for both produces linear motion.

### Final Position Keyframe

The last keyframe has only `t` and `s` (no easing, no tangents):

```json
{"t": 60, "s": [150, 50, 0]}
```

### Complete Position Animation Example

Move from (50, 200) to (150, 50) over 60 frames with curved motion:

```json
{"a": 1, "k": [
  {
    "t": 0,
    "s": [50, 200, 0],
    "to": [16.67, -25, 0],
    "ti": [-16.67, 25, 0],
    "i": {"x": [0.42, 0.42], "y": [0, 0]},
    "o": {"x": [0.58, 0.58], "y": [1, 1]}
  },
  {
    "t": 60,
    "s": [150, 50, 0]
  }
]}
```

---

## 9. Shape Morph Keyframes

Animated shape paths morph between two path objects. The keyframe format differs from
other property types.

**`s` and `e` are ARRAYS of path objects**, not bare path objects. This is the format
for all renderers (lottie-web, rlottie, ThorVG).

```json
{
  "t": 0,
  "s": [{"c": true, "v": [...], "i": [...], "o": [...]}],
  "e": [{"c": true, "v": [...], "i": [...], "o": [...]}],
  "i": {"x": [0.42], "y": [0]},
  "o": {"x": [0.58], "y": [1]}
}
```

| Field | Description |
|---|---|
| `t` | Frame number. |
| `s` | **Array** containing the start path object. `[path]`, not `path`. |
| `e` | **Array** containing the end path object. `[path]`, not `path`. |
| `i`/`o` | Temporal easing. **1D format** (single-element arrays). |

**NO `to`/`ti`**: shape morph is NOT a spatial property. Spatial tangents are not
applicable and must be omitted.

### Both Paths Must Have Equal Vertex Counts

The start and end paths must have the same number of vertices. If contour A has 64
segments and contour B has 48, you must resample both to the same count before
generating keyframes. Mismatched counts produce undefined behavior (usually a crash
in ThorVG, visual garbage in lottie-web).

### Hold Keyframe (No Morph)

To hold a shape steady, set `e` equal to `s`:

```json
{
  "t": 0,
  "s": [path_a],
  "e": [path_a],
  "i": {"x": [0.67], "y": [1]},
  "o": {"x": [0.33], "y": [0]}
}
```

### Final Shape Keyframe

```json
{"t": 60, "s": [path_b]}
```

### Complete Shape Morph Example

Hold digit "3" for 15 frames, morph to digit "8" over 60 frames, hold:

```json
{"a": 1, "k": [
  {
    "t": 0,
    "s": [{"c": true, "v": [[...]], "i": [[...]], "o": [[...]]}],
    "e": [{"c": true, "v": [[...]], "i": [[...]], "o": [[...]]}],
    "i": {"x": [0.42], "y": [0]},
    "o": {"x": [0.58], "y": [1]}
  },
  {
    "t": 15,
    "s": [{"c": true, "v": [[...]], "i": [[...]], "o": [[...]]}],
    "e": [{"c": true, "v": [[...]], "i": [[...]], "o": [[...]]}],
    "i": {"x": [0.25], "y": [0.1]},
    "o": {"x": [0.75], "y": [0.9]}
  },
  {
    "t": 75,
    "s": [{"c": true, "v": [[...]], "i": [[...]], "o": [[...]]}]
  }
]}
```

---

## 10. Scale and Rotation: NO Spatial Tangents

Scale and rotation are animated properties but are **NOT spatial**. They must never
include `to`/`ti` fields. Including spatial tangents on these properties produces
undefined renderer behavior.

### Scale Keyframes

Scale uses `[sx, sy, sz]` as percentages (100 = original size). Easing is **2D format**
because there are two independent components.

```json
{
  "t": 0,
  "s": [0, 0, 100],
  "i": {"x": [0.42, 0.42], "y": [0, 0]},
  "o": {"x": [0.58, 0.58], "y": [1, 1]}
}
```

Pop-in with overshoot:

```json
{"a": 1, "k": [
  {"t": 10, "s": [0, 0, 100],
   "i": {"x": [0.42, 0.42], "y": [0, 0]},
   "o": {"x": [0.58, 0.58], "y": [1, 1]}},
  {"t": 18, "s": [125, 125, 100],
   "i": {"x": [0.42, 0.42], "y": [0, 0]},
   "o": {"x": [0.58, 0.58], "y": [1, 1]}},
  {"t": 23, "s": [100, 100, 100]}
]}
```

### Rotation Keyframes

Rotation is a single scalar (degrees). Easing is **1D format**.

```json
{
  "t": 0,
  "s": [-50],
  "i": {"x": [0.42], "y": [0]},
  "o": {"x": [0.58], "y": [1]}
}
```

Spin from -50 to 0 degrees:

```json
{"a": 1, "k": [
  {"t": 10, "s": [-50],
   "i": {"x": [0.42], "y": [0]},
   "o": {"x": [0.58], "y": [1]}},
  {"t": 23, "s": [0]}
]}
```

### Summary Table

| Property | Value Format | Easing | to/ti |
|---|---|---|---|
| Position | `[x, y, z]` | 2D | **YES** (required for curves) |
| Scale | `[sx, sy, sz]` | 2D | **NO** |
| Rotation | `[degrees]` | 1D | **NO** |
| Opacity | `[percent]` | 1D | **NO** |
| Shape | `[path_object]` | 1D | **NO** |

---

## 11. Fill Rules

The fill `r` field controls how overlapping sub-paths determine inside/outside.

| Value | Rule | Description |
|---|---|---|
| `1` | Non-zero winding | Counts path direction. CW and CCW cancel out. |
| `2` | Even-odd | Counts crossings. Alternates filled/unfilled. |

### Font Glyphs: Use Non-Zero Winding (r=1)

Font outlines use **non-zero winding** with a strict convention:
- **Outer contours**: clockwise (CW) winding
- **Hole contours**: counter-clockwise (CCW) winding

This means holes "cut out" from the filled outer contour because their winding cancels.

```json
{
  "ty": "fl",
  "nm": "fill",
  "c": {"a": 0, "k": [0.95, 0.95, 0.95, 1]},
  "r": 1,
  "o": {"a": 0, "k": 100}
}
```

When morphing between digits, degenerate contours (zero-area placeholders for digits
with fewer contours than others) contribute zero winding and render invisibly -- which
is exactly correct. They grow into real contours as the morph progresses.

### When to Use Even-Odd (r=2)

Even-odd is simpler but less predictable with complex overlapping shapes. It does not
require winding direction awareness. Use it when you do not control contour winding
direction, or for simple non-overlapping shapes.

---

## 12. Group Transform (tr)

**The group transform MUST be the LAST item in the group's `it` array.**

Renderers process the `it` array and expect the transform at the end. Placing it
elsewhere causes undefined behavior (missing shapes, wrong positioning, or crashes).

```json
{
  "ty": "gr",
  "nm": "flower-group",
  "it": [
    {"ty": "el", "nm": "petal", "...": "..."},
    {"ty": "fl", "nm": "fill", "...": "..."},
    {
      "ty": "tr",
      "p": {"a": 0, "k": [0, 0]},
      "a": {"a": 0, "k": [0, 0]},
      "s": {"a": 0, "k": [100, 100]},
      "r": {"a": 0, "k": 0},
      "o": {"a": 0, "k": 100}
    }
  ]
}
```

The group transform fields are the same as the layer transform (section 13) but
use 2D values (`[x, y]`) instead of 3D (`[x, y, z]`).

| Field | Description |
|---|---|
| `p` | Position `[x, y]` offset. |
| `a` | Anchor point `[x, y]`. |
| `s` | Scale `[sx, sy]` as percentages. |
| `r` | Rotation in degrees. |
| `o` | Opacity (0-100). |

### Nested Groups with Rotation

A common pattern for positioning rotated elements (e.g., petals around a flower center):

```json
{
  "ty": "gr", "nm": "petal-0", "it": [
    {"ty": "sh", "nm": "p", "ks": {"a": 0, "k": {"c": true, "v": [...], "i": [...], "o": [...]}}},
    {"ty": "fl", "nm": "f", "c": {"a": 0, "k": [1.0, 0.4, 0.5, 1]}, "r": 1, "o": {"a": 0, "k": 100}},
    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
     "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 72}, "o": {"a": 0, "k": 100}}
  ]
}
```

The `r: 72` rotates this petal 72 degrees. Five such groups at 0, 72, 144, 216, 288
degrees create a 5-petal flower.

---

## 13. Layer Transform (ks)

Every layer has a `ks` object defining its spatial transform. All fields are animatable.

```json
{
  "p": {"a": 0, "k": [100, 130, 0]},
  "a": {"a": 0, "k": [0, 0, 0]},
  "s": {"a": 0, "k": [100, 100, 100]},
  "r": {"a": 0, "k": 0},
  "o": {"a": 0, "k": 100}
}
```

| Field | Description | Static Format | Easing |
|---|---|---|---|
| `p` | Position | `[x, y, z]` | 2D + to/ti |
| `a` | Anchor point (center of rotation/scale) | `[x, y, z]` | 2D + to/ti |
| `s` | Scale (percentages) | `[sx, sy, sz]` | 2D, no to/ti |
| `r` | Rotation (degrees) | `degrees` | 1D, no to/ti |
| `o` | Opacity | `0-100` | 1D, no to/ti |

### Transform Order

Transforms are applied: **Anchor -> Scale -> Rotate -> Translate**

The anchor point defines the origin for scale and rotation. To scale/rotate an object
around its center, set the anchor to the object's center coordinates. To
scale/rotate around the origin, leave anchor at `[0, 0, 0]`.

### Default Transform (Identity)

```json
{
  "p": {"a": 0, "k": [0, 0, 0]},
  "a": {"a": 0, "k": [0, 0, 0]},
  "s": {"a": 0, "k": [100, 100, 100]},
  "r": {"a": 0, "k": 0},
  "o": {"a": 0, "k": 100}
}
```

### Animated Layer Transform Example

A flower layer that moves into position, pops in scale, and rotates:

```json
{
  "p": {"a": 1, "k": [
    {"t": 0, "s": [50, 200, 0], "to": [16.67, -25, 0], "ti": [-16.67, 25, 0],
     "i": {"x": [0.42, 0.42], "y": [0, 0]}, "o": {"x": [0.58, 0.58], "y": [1, 1]}},
    {"t": 45, "s": [120, 80, 0]}
  ]},
  "a": {"a": 0, "k": [0, 0, 0]},
  "s": {"a": 1, "k": [
    {"t": 0, "s": [50, 50, 100],
     "i": {"x": [0.42, 0.42], "y": [0, 0]}, "o": {"x": [0.58, 0.58], "y": [1, 1]}},
    {"t": 45, "s": [100, 100, 100]}
  ]},
  "r": {"a": 1, "k": [
    {"t": 0, "s": [0],
     "i": {"x": [0.42], "y": [0]}, "o": {"x": [0.58], "y": [1]}},
    {"t": 45, "s": [25]}
  ]},
  "o": {"a": 0, "k": 100}
}
```

---

## Appendix A: Renderer Compatibility Notes

| Feature | lottie-web | rlottie | ThorVG (ESP32) |
|---|---|---|---|
| Shape morph | Full support | Full support | Full support |
| Trim paths | Full support | Full support | Full support |
| Even-odd fill | Full support | Full support | Full support |
| Precomp layers | Full support | Full support | Limited |
| Elastic easing (y > 1.0) | Works | Works | Untested |
| Wrong easing dimensions | Silent corruption | Silent corruption | Crash or corruption |

## Appendix B: Common Mistakes Checklist

1. **s/e on shape keyframes are bare paths instead of arrays**
   - Wrong: `"s": {"c": true, ...}`
   - Right: `"s": [{"c": true, ...}]`

2. **1D easing handles on position keyframes**
   - Wrong: `"i": {"x": [0.42], "y": [0]}`
   - Right: `"i": {"x": [0.42, 0.42], "y": [0, 0]}`

3. **2D easing handles on shape/opacity/rotation keyframes**
   - Wrong: `"i": {"x": [0.42, 0.42], "y": [0, 0]}`
   - Right: `"i": {"x": [0.42], "y": [0]}`

4. **Missing to/ti on position keyframes** -- motion will be linear (no curves)

5. **Including to/ti on scale or rotation keyframes** -- undefined behavior

6. **Group transform not at end of `it` array** -- shapes disappear or misposition

7. **Mismatched vertex counts in shape morph** -- crash or visual garbage

8. **Absolute tangent coordinates in path instead of relative** -- path explodes

9. **Background layer at index 0 instead of last** -- covers everything

10. **Path `i`/`o` tangent arrays different length from `v`** -- renderer crash
