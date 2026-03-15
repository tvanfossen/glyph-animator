---
type: proof
algorithm: PathMorpher
class_path: glyph_animator.algorithms.matching.PathMorpher

parameters: {}

complexity: "O(N) where N = segment count"
error_bound: "Exact (linear interpolation of control points)"
gate_validation: "Gate 5: smooth intermediates at alpha=0, 0.25, 0.5, 0.75, 1.0"
---

# Path Interpolation via Linear Control Point Morphing

## Problem Statement

Given two compatible paths P_source and P_target — each consisting of K contours with N cubic Bezier segments per contour, with aligned starting points — produce an interpolated path P(alpha) for alpha in [0, 1] such that:
1. P(0) = P_source exactly
2. P(1) = P_target exactly
3. P(alpha) is a valid collection of cubic Bezier curves for all alpha in [0, 1]

## Compatibility Preconditions

The PathMorpher requires that its inputs have been processed by the preceding pipeline stages:

1. **Equal contour count** (Gate 4, HungarianMatcher): degenerate contours synthesized if needed
2. **Equal segment count per contour** (Gate 3, arc-length resampling): both paths resampled to N segments
3. **Aligned starting points** (Gate 4, StartingPointAligner): cyclic rotation optimized
4. **Matched contour pairing** (Gate 4, HungarianMatcher): bijection sigma mapping source contours to target contours

## Interpolation Formula

For each contour pair (S_m, T_{sigma(m)}) and each segment n in {0, ..., N-1}, the source segment has control points (s_0, s_1, s_2, s_3) and the target segment has control points (t_0, t_1, t_2, t_3). The interpolated segment at parameter alpha is:

    P_morph(alpha)_n^{(j)} = (1 - alpha) * s_j + alpha * t_j,  for j in {0, 1, 2, 3}

where each s_j, t_j in R^2, and the arithmetic is component-wise:

    x_j(alpha) = (1 - alpha) * s_j.x + alpha * t_j.x
    y_j(alpha) = (1 - alpha) * s_j.y + alpha * t_j.y

## Proof of Boundary Conditions

**Theorem 1.** P(0) = P_source and P(1) = P_target.

*Proof.* At alpha = 0:

    P_morph(0)_n^{(j)} = (1 - 0) * s_j + 0 * t_j = s_j

for all segments n and control points j. This is identically P_source.

At alpha = 1:

    P_morph(1)_n^{(j)} = (1 - 1) * s_j + 1 * t_j = t_j

for all segments n and control points j. This is identically P_target. QED

## Proof of Valid Cubic Bezier Output

**Theorem 2.** For all alpha in [0, 1], the interpolated control points define valid cubic Bezier curves.

*Proof.* A cubic Bezier curve is defined by any four points (P_0, P_1, P_2, P_3) in R^2. The Bernstein basis evaluation:

    B(t) = (1-t)^3 * P_0 + 3(1-t)^2 * t * P_1 + 3(1-t) * t^2 * P_2 + t^3 * P_3

is well-defined for any four points in R^2, with no constraints on their relative positions. There is no configuration of four points that produces an "invalid" cubic Bezier — the curve always exists and is a continuous polynomial map [0,1] -> R^2.

Since P_morph(alpha)_n^{(j)} is a linear combination of points in R^2 with coefficients (1-alpha) and alpha that sum to 1, the result is a point in R^2 (convex combination). Four such points define a valid cubic Bezier segment. QED

## Proof of Continuity in Alpha

**Theorem 3.** The interpolated path P(alpha) varies continuously with alpha.

*Proof.* Each control point coordinate is an affine function of alpha:

    x_j(alpha) = s_j.x + alpha * (t_j.x - s_j.x)

This is a polynomial of degree 1 in alpha, hence continuous (and in fact smooth to all orders). Since each segment's shape B(t; alpha) is a polynomial in both t and alpha (via the Bernstein basis applied to affine functions of alpha), the entire path is jointly continuous in (t, alpha). QED

## Complexity

The interpolation visits each of the K contours, each with N segments, each with 4 control points, each with 2 coordinates. Total operations:

    K * N * 4 * 2 * 2 = 16KN

floating-point operations (one multiply and one add per coordinate per control point). Since K is bounded by a small constant (at most 5 for typographic glyphs), the complexity is O(N).

For typical values K = 3, N = 64: 16 * 3 * 64 = 3072 operations per frame.

## Non-Constant Speed

**Remark.** Linear interpolation in control-point space does not produce constant-speed morphing in the perceptual sense. Consider two contours where the source is a small circle and the target is a large circle: at alpha = 0.5, the interpolated contour is the midpoint circle (average radius), but the visual "distance traveled" in the first half (small to medium) appears less dramatic than the second half (medium to large) due to area scaling quadratically with radius.

This non-uniformity is by design. The Lottie animation format provides its own easing system (cubic Bezier easing curves on keyframe timing) that controls the temporal progression of alpha. The path interpolation provides geometrically correct intermediates; the Lottie easing handles perceptual tempo. Separating these concerns allows the same morph data to be played with different timing profiles (ease-in, ease-out, linear, spring) without recomputing geometry.

## Waypoint Extension for Topologically Dissimilar Glyphs

For glyphs with significantly different topology (e.g., "1" with 1 contour morphing to "8" with 3 contours), direct interpolation via degenerate contours can produce unsatisfying collapse/expansion artifacts. The waypoint extension decomposes the morph into two stages:

    P_source -> P_waypoint -> P_target

where P_waypoint is an intermediate design (e.g., a neutral circular form) compatible with both endpoints. Each half-morph uses the same linear interpolation proven above, with alpha remapped to [0, 0.5] and [0.5, 1] respectively. The boundary conditions and continuity proofs apply independently to each half, and continuity at the join (alpha = 0.5) is guaranteed since both halves evaluate to P_waypoint at that point.
