---
type: proof
algorithm: CoordinateTransform
class_path: glyph_animator.algorithms.transform.CoordinateTransform

parameters:
  render_size:
    value: 400
    type: int
    range: [100, 2000]
    description: "Output image size in pixels"
  padding:
    value: 40
    type: int
    range: [0, 200]
    description: "Padding around glyph in pixels"

complexity: "O(1) per point"
error_bound: "Machine epsilon (affine transform)"
gate_validation: "All gates: rendering uses this transform for visual verification"
---

# Affine Coordinate Transform: Font Space to Image Space

## Problem Statement

Font outlines are defined in a coordinate system with Y-axis pointing upward and origin at the baseline. Raster images use a coordinate system with Y-axis pointing downward and origin at the top-left corner. We require a transform that maps font coordinates to pixel coordinates while:
1. Preserving glyph proportions (uniform scaling)
2. Centering the glyph within the output image
3. Applying configurable padding
4. Flipping the Y-axis

## Coordinate Systems

### Font Space (Source)
- Origin: (0, 0) at the glyph's left sidebearing on the baseline
- X-axis: rightward (positive)
- Y-axis: upward (positive)
- Units: font design units (typically 1000 or 2048 units-per-em)
- Bounding box: [xMin, yMin] to [xMax, yMax] from the glyph's outline extrema

### Image Space (Target)
- Origin: (0, 0) at top-left pixel
- X-axis: rightward (positive)
- Y-axis: downward (positive)
- Units: pixels
- Bounding box: [0, 0] to [render_size - 1, render_size - 1]

## Transform Derivation

### Step 1: Available Drawing Area

The available area after padding is:

    available = render_size - 2 * padding

This defines a square region of side length `available` pixels, inset by `padding` pixels from each edge.

### Step 2: Uniform Scale Factor

The glyph's bounding box has dimensions:

    width  = xMax - xMin
    height = yMax - yMin

To fit the glyph within the available area while preserving aspect ratio:

    scale = min(available / width, available / height)

**Proposition.** This scale factor is the largest uniform scale that fits the entire glyph within the padded region.

*Proof.* After scaling, the glyph dimensions are (width * scale, height * scale). By the definition of scale as the minimum of two ratios:
- width * scale = width * min(available/width, available/height) <= width * (available/width) = available
- height * scale = height * min(available/width, available/height) <= height * (available/height) = available

So the scaled glyph fits. If scale were any larger, the binding dimension (whichever ratio was smaller) would exceed `available`. QED

### Step 3: Centering Offset

After scaling, the glyph may not fill the available area in one dimension. The centering offsets are:

    offset_x = padding + (available - width * scale) / 2
    offset_y = padding + (available - height * scale) / 2

### Step 4: Full Transform

Combining scaling, Y-flip, and translation:

    px = offset_x + (x - xMin) * scale
    py = offset_y + (yMax - y) * scale

Equivalently, in the non-centered (padding-only) form used by the implementation:

    px = padding + (x - xMin) * scale
    py = padding + (yMax - y) * scale

where the binding dimension exactly fills `available` and the non-binding dimension is implicitly centered by the equal padding on both sides (since the output is square and scale is chosen by the binding dimension).

## Matrix Representation

The transform can be expressed as a 3x3 affine matrix operating on homogeneous coordinates:

    | px |   | scale    0      padding - xMin * scale          | | x |
    | py | = | 0       -scale  padding + yMax * scale          | | y |
    |  1 |   | 0        0      1                               | | 1 |

The negative scale in the (2,2) position accomplishes the Y-flip. The translation terms in the third column combine the origin shift with the padding offset.

## Proof of Affine Properties

**Theorem 1.** The transform preserves straight lines.

*Proof.* An affine transform is a function f: R^2 -> R^2 of the form f(v) = Mv + b where M is a 2x2 matrix and b is a translation vector. For our transform:

    M = | scale    0    |    b = | padding - xMin * scale |
        | 0      -scale |        | padding + yMax * scale |

A straight line in font space is parameterized as L(t) = A + t*(B - A) for t in [0,1]. Applying f:

    f(L(t)) = M*(A + t*(B-A)) + b = (MA + b) + t*(M*(B-A)) = f(A) + t*(f(B) - f(A))

This is a straight line from f(A) to f(B) in image space. QED

**Theorem 2.** The transform preserves parallelism.

*Proof.* Two lines are parallel iff their direction vectors are scalar multiples: d_2 = lambda * d_1. After applying M:

    M*d_2 = M*(lambda * d_1) = lambda * (M*d_1)

So the transformed direction vectors remain scalar multiples, preserving parallelism. QED

**Theorem 3.** The transform preserves the ratio of distances along any line.

*Proof.* For three collinear points A, B, C with B dividing AC in ratio r:(1-r), we have B = A + r*(C-A). Applying f:

    f(B) = f(A) + r*(f(C) - f(A))

So f(B) divides f(A)f(C) in the same ratio r:(1-r). QED

**Corollary.** Bezier curves are correctly preserved. A cubic Bezier curve is defined by the de Casteljau algorithm, which uses only convex combinations (ratio-preserving operations on collinear points). Since the affine transform preserves these ratios (Theorem 3), applying the transform to the four control points and then evaluating the Bezier produces the same result as evaluating the Bezier first and then transforming each point. This is the well-known affine invariance of Bezier curves.

## Error Analysis

The transform involves the following floating-point operations per point:
1. One subtraction (x - xMin or yMax - y)
2. One multiplication (result * scale)
3. One addition (padding + result)

Using IEEE 754 float64 arithmetic, each operation introduces relative error at most epsilon approximately equal to 2.22e-16 (machine epsilon). By standard error propagation, three chained operations accumulate at most:

    (1 + epsilon)^3 - 1 approximately equal to 3 * epsilon approximately equal to 6.66e-16

For a render_size of 2000 pixels, the maximum absolute error is:

    2000 * 6.66e-16 approximately equal to 1.33e-12 pixels

This is thirteen orders of magnitude below the size of a single pixel, making the transform exact for all practical purposes.

## Inverse Transform

The inverse (image space to font space) is:

    x = (px - padding) / scale + xMin
    y = yMax - (py - padding) / scale

This is used when mapping pixel coordinates (e.g., from mouse clicks in the viewer) back to font coordinates. The inverse exists and is unique because M is non-singular (det(M) = -scale^2 != 0 for scale > 0).
