---
type: proof
algorithm: ContourResampler
class_path: glyph_animator.algorithms.resampling.ContourResampler
uses_constants:
  - GAUSS_5PT
parameters:
  target_n:
    value: 64
    type: int
    range: [16, 256]
    description: "Segments per resampled contour"
complexity: "O(N*S) where N=target segments, S=original segments"
error_bound: "< 5.0 font units (0.5% em)"
gate_validation: "Gate 3 — Hausdorff < 5.0 across all digits at N=64"
---

# Proof 4: Contour Resampling via Arc-Length Parameterization

## 1. Problem Statement

Given a closed contour consisting of S cubic Bezier segments (with varying arc
lengths), produce a new contour of exactly N cubic Bezier segments where each
segment has equal arc length delta_s = L / N, and the new contour approximates
the original to within a bounded Hausdorff distance.

This normalization is a prerequisite for path morphing (Proof 7): two contours
can only be linearly interpolated if they have the same number of segments, and
the visual quality of morphing improves when corresponding segments cover similar
arc-length spans.

## 2. Algorithm

The resampling algorithm proceeds in three phases:

### Phase 1: Compute Total Arc Length

Using 5-point Gauss quadrature (Proof 2), compute the arc length of each original
segment and the cumulative arc lengths:

    L_i = integral_0^1 |B'_i(t)| dt     for i = 1, ..., S
    L = sum_{i=1}^{S} L_i
    delta_s = L / N

Complexity: O(S) with 5 quadrature evaluations per segment.

### Phase 2: Split at Arc-Length Boundaries

Walk the original segments, placing boundary points at cumulative arc lengths
k * delta_s for k = 1, ..., N-1. At each boundary:

1. **Locate the segment**: Find the original segment containing the boundary
   point by comparing cumulative arc lengths.

2. **Find the local parameter**: Given segment i and target local arc length
   s_local, use Newton's method (Proof 2) to find t* such that
   L_i(0, t*) = s_local.

3. **Subdivide**: Use De Casteljau (Proof 3) to split the segment at t*,
   producing a left sub-curve (before the boundary) and a right sub-curve
   (after, which continues to the next boundary).

This produces a list of sub-segments, partitioned into N groups by the
boundary indices.

Complexity: O(N * S) in the worst case, since each boundary point requires
locating its segment and performing Newton iteration. In practice, the walk is
sequential and each boundary is found in O(1) amortized time.

### Phase 3: Merge Sub-Segments

Each group of sub-segments between consecutive boundaries must be merged into a
single cubic Bezier. Three cases:

1. **Group has exactly 1 sub-segment**: Use it directly (no approximation).
2. **Group has 0 sub-segments**: Degenerate case (all control points at the
   previous endpoint).
3. **Group has >= 2 sub-segments**: Fit a single cubic via least-squares
   (Proof 4a).

Complexity: O(N * K) where K is the sample count per fitting (K = 20).

## 3. Error Analysis

The resampling introduces approximation error only in Phase 3, case 3, when
multiple sub-segments are merged into one cubic. The error sources are:

### Source 1: Arc-length computation (Proof 2)

The boundary placement has error < 10^{-6} font units in arc length, which
translates to parameter error < 10^{-9} (Section 5 of Proof 2). This is
negligible.

### Source 2: De Casteljau subdivision (Proof 3)

Exact — introduces no geometric error.

### Source 3: Least-squares cubic fitting (Proof 4a)

This is the dominant error source. When merging M sub-segments into one cubic,
the fitting error depends on the curvature variation within the merged span.

**Bound.** For a smooth curve with curvature kappa(t) and curvature derivative
kappa'(t) bounded by kappa_max and kappa'_max respectively, the Hausdorff distance
between the original curve segment of arc length delta_s and its best-fit cubic
approximation is bounded by:

    H <= (kappa'_max * delta_s^3) / 24

This is the standard cubic approximation error for a curve segment, derived from
the Taylor expansion of the curve about the midpoint. The cubic can match the
curve up to third-order contact (position, tangent, curvature), leaving a residual
that scales with the cube of the segment length.

### Numerical estimate for fonts

For typical font glyphs (Nunito ExtraBold) at 1000 units/em:

- Total arc length per contour: L ~ 2000-5000 font units
- Number of segments: N = 64
- Segment arc length: delta_s ~ 30-80 font units
- Maximum curvature derivative: kappa'_max ~ 0.01 (measured across digit glyphs)

Plugging in:
    H <= 0.01 * 80^3 / 24 = 0.01 * 512000 / 24 ~ 213

This naive bound is loose because it assumes worst-case curvature variation across
the entire segment. In practice, the least-squares fitting (Proof 4a) with K = 20
sample points adapts the control points to minimize the actual deviation, yielding
much better results than the worst-case Taylor bound.

### Empirical measurement

Gate 3 measures the Hausdorff distance between original and resampled contours by
sampling 1000 points on each and computing the maximum nearest-point distance.
Across all 10 digit glyphs at N = 64:

    max Hausdorff distance < 5.0 font units

This is 0.5% of the em width, corresponding to < 1 pixel at any practical render
size (font sizes up to ~200pt at 96 DPI give ~0.1px error).

## 4. Correctness of Boundary Placement

**Theorem.** The resampling algorithm places exactly N-1 interior boundaries,
producing exactly N groups, each with arc length delta_s (up to quadrature
precision).

**Proof.** The algorithm maintains a running cumulative arc length `cum_arc` and a
boundary counter `boundaries_placed`. At each step:

- If `local_target = next_boundary - cum_arc > current_len + epsilon`: the current
  segment does not contain the next boundary. Append it as a sub-segment and
  advance to the next original segment.

- If `local_target < epsilon`: the boundary falls exactly at the current segment
  start. Place a group boundary without splitting.

- Otherwise: split the current segment at the boundary via Newton + De Casteljau.
  Append the left piece, place the group boundary, and continue with the right piece.

The loop terminates when `boundaries_placed = N - 1` (all interior boundaries
placed) or all original segments are consumed. After the loop, a final boundary
at `len(sub_segments)` closes the last group.

Since the boundaries are placed at cumulative arc lengths k * delta_s for
k = 1, ..., N-1, and the total arc length of all sub-segments equals L (because
De Casteljau subdivision is exact), each group spans arc length delta_s, up to
the quadrature precision of < 10^{-6}. QED.

## 5. Closure Preservation

The original contour is closed: the last segment's endpoint C_3 equals the first
segment's startpoint C_0. The resampling algorithm preserves this:

- Phase 2 does not modify endpoints; it only splits interior points.
- Phase 3 fitting fixes C_0 and C_3 of each merged cubic to the boundary points.
- The first group starts at the original contour start, and the last group ends
  at the original contour end (which is the same point).

Therefore the resampled contour is also closed.

## 6. Gate Validation

Gate 3 validates the resampling pipeline with the following checks:

1. **Segment count**: Output has exactly N = 64 segments per contour.
2. **Arc-length uniformity**: Standard deviation of per-segment arc lengths is
   < 1% of delta_s.
3. **Hausdorff distance**: < 5.0 font units from original contour.
4. **Closure**: |first_point - last_point| < 10^{-6}.

All checks pass across the full set of 10 digit glyphs (0-9) extracted from
Nunito ExtraBold.
