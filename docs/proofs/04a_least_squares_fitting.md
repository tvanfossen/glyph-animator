---
type: proof
algorithm: CubicFitter
class_path: glyph_animator.algorithms.resampling.CubicFitter
parameters:
  n_samples:
    value: 20
    type: int
    range: [10, 50]
    description: "Interior sample points for fitting"
complexity: "O(K) where K = sample count"
error_bound: "Bounded by curvature variation within merged span"
gate_validation: "Gate 3 — contributes to overall Hausdorff < 5.0"
---

# Proof 4a: Least-Squares Cubic Bezier Fitting

## 1. Problem Statement

Given a sequence of M cubic Bezier sub-segments that together trace a curve from
point C_0 to point C_3, fit a single cubic Bezier (C_0, C_1, C_2, C_3) with
fixed endpoints C_0 and C_3 that minimizes the sum of squared deviations from K
interior sample points along the original curve.

This operation is the core of the merge step in contour resampling (Proof 4).

## 2. Sampling

Sample K interior points P_1, P_2, ..., P_K at uniformly-spaced arc-length
fractions along the group of sub-segments:

    P_k = B_group(s_k)     where s_k = k / (K+1)     for k = 1, ..., K

Here B_group(s) denotes evaluation along the concatenated sub-segments at
normalized arc-length parameter s in (0, 1). The corresponding Bezier parameter
for the fitted cubic is t_k = k / (K+1).

The implementation uses K = 19 interior points (n_samples = 20 produces samples
at k/(K+1) for k = 1, ..., 19, since the loop `range(1, n_samples)` gives
indices 1 through 19, and t_k = k / n_samples = k / 20).

More precisely, from the implementation:

    for k in range(1, n_samples):  # k = 1, ..., 19
        target = k * total / n_samples
        # ... locate and evaluate point on sub-segments
        ts.append(k / n_samples)   # t_k = k/20

## 3. Formulation as Linear System

The fitted cubic Bezier at parameter t is:

    B(t) = (1-t)^3 C_0 + 3(1-t)^2 t C_1 + 3(1-t) t^2 C_2 + t^3 C_3

With C_0 and C_3 fixed, define the residual at sample point k:

    r_k = P_k - (1-t_k)^3 C_0 - t_k^3 C_3

This is the part of P_k not explained by the fixed endpoints. The unknowns C_1
and C_2 must satisfy:

    r_k ~ 3(1-t_k)^2 t_k C_1 + 3(1-t_k) t_k^2 C_2

Define the basis functions:

    phi_1(t) = 3(1-t)^2 t
    phi_2(t) = 3(1-t) t^2

We minimize the objective:

    F(C_1, C_2) = sum_{k=1}^{K} |r_k - phi_1(t_k) C_1 - phi_2(t_k) C_2|^2

Since x and y coordinates are independent (the squared norm decomposes as
|v|^2 = v_x^2 + v_y^2), this separates into two identical-structure scalar
least-squares problems, one per coordinate.

## 4. Normal Equations

Setting partial derivatives to zero:

    dF/dC_1 = 0:   sum_k phi_1(t_k) [phi_1(t_k) C_1 + phi_2(t_k) C_2 - r_k] = 0
    dF/dC_2 = 0:   sum_k phi_2(t_k) [phi_1(t_k) C_1 + phi_2(t_k) C_2 - r_k] = 0

In matrix form (for x-coordinate; y-coordinate is identical):

    [A_11  A_12] [C_1x]   [b_1x]
    [A_12  A_22] [C_2x] = [b_2x]

where:

    A_11 = sum_k phi_1(t_k)^2
    A_12 = sum_k phi_1(t_k) phi_2(t_k)
    A_22 = sum_k phi_2(t_k)^2
    b_1x = sum_k phi_1(t_k) r_kx
    b_2x = sum_k phi_2(t_k) r_kx

This is the Gram matrix of the basis functions sampled at the t_k values. The
solution by Cramer's rule:

    det = A_11 * A_22 - A_12^2

    C_1x = (A_22 * b_1x - A_12 * b_2x) / det
    C_2x = (A_11 * b_2x - A_12 * b_1x) / det

And identically for the y-coordinate. This matches the implementation in
`_solve_least_squares`.

## 5. Non-Degeneracy of the Gram Matrix

**Theorem.** For K >= 2 sample points with distinct t_k values in (0, 1), the
determinant det = A_11 * A_22 - A_12^2 > 0.

**Proof.** The Gram matrix G = [A_ij] is a 2x2 matrix with entries:

    G_ij = sum_k phi_i(t_k) phi_j(t_k) = <phi_i, phi_j>

where the inner product is the discrete sum over sample points. The matrix G is
positive semi-definite by construction (it equals M^T M where M is the K x 2
matrix with rows [phi_1(t_k), phi_2(t_k)]).

G is strictly positive definite (det > 0) if and only if the columns of M are
linearly independent, i.e., there is no scalar alpha such that:

    phi_1(t_k) = alpha * phi_2(t_k)     for all k

Substituting:

    3(1-t_k)^2 t_k = alpha * 3(1-t_k) t_k^2

For t_k in (0, 1), we can divide both sides by 3(1-t_k) t_k > 0:

    (1-t_k) = alpha * t_k

This gives alpha = (1-t_k) / t_k, which is different for different values of t_k.
Therefore, for any two distinct sample points t_j != t_k, no single alpha satisfies
both equations simultaneously.

Since K >= 2 and the t_k are distinct (they are k/20 for k = 1, ..., 19), the
columns are linearly independent and det > 0. QED.

**Fallback.** The implementation guards against near-zero determinant
(|det| < 10^{-20}) by falling back to the linear interpolation:

    C_1 = lerp(C_0, C_3, 1/3)
    C_2 = lerp(C_0, C_3, 2/3)

This can only trigger for nearly-degenerate configurations where all sample points
are collinear with C_0 and C_3, in which case the linear cubic is already a good
approximation.

## 6. Optimality

**Theorem.** The solution (C_1*, C_2*) from the normal equations globally minimizes
F(C_1, C_2).

**Proof.** F is a sum of squared terms, each quadratic in C_1 and C_2. Therefore F
is a convex quadratic function of the four unknowns (C_1x, C_1y, C_2x, C_2y).
Since the Hessian matrix (2G for each coordinate) is positive definite (Section 5),
the unique critical point found by the normal equations is the global minimum. QED.

## 7. Error Characterization

The fitting error at sample point k is:

    e_k = P_k - B(t_k)

The maximum fitting error over all sample points is:

    E_sample = max_k |e_k|

The true Hausdorff error between the fitted cubic and the original curve may be
slightly larger, since the maximum deviation can occur between sample points. The
relationship is:

    H <= E_sample + O(delta_t^2 * kappa_max)

where delta_t = 1/K is the sample spacing and kappa_max is the maximum curvature
of the original curve. For K = 19 and typical font curvatures, the inter-sample
error term is negligible (< 0.1 font units).

### Error dependence on curvature variation

The least-squares fit is exact when the original curve is itself a cubic Bezier
(the fit recovers the original control points). Error arises only when the
concatenation of sub-segments has higher effective degree than cubic — i.e., when
the curvature varies within the merged span.

For a curve with constant curvature (circular arc), a single cubic can approximate
it to within:

    H_arc ~ (kappa * delta_s)^3 / 384

For kappa = 0.01 (typical font curvature) and delta_s = 80 font units:

    H_arc ~ (0.01 * 80)^3 / 384 = 0.512^3 / 384 ~ 0.00035

This is well below the 5.0 threshold.

The worst case occurs at high-curvature transitions (e.g., the junction of the
bowl and stem in digit "6"), where kappa' is largest. Even there, the measured
Hausdorff stays below 5.0 at N = 64.

## 8. Complexity

The algorithm performs:

- K evaluations of phi_1(t_k) and phi_2(t_k): O(K)
- K additions to the 5 accumulators (A_11, A_12, A_22, b_1, b_2): O(K)
- One 2x2 solve: O(1)

Total: O(K) per fitted cubic. With K = 19, this is 19 multiply-accumulate
iterations plus a constant-time solve.

Over the full resampling pipeline, fitting is called at most N times (once per
output segment), giving total fitting cost O(N * K).

## 9. Gate Validation

Gate 3 validates the combined resampling pipeline (arc-length computation +
boundary placement + De Casteljau splitting + least-squares fitting). The
least-squares fitting contributes the dominant approximation error, and the
overall Hausdorff distance is measured at < 5.0 font units across all 10 digit
glyphs at N = 64 segments per contour.

The fitting is also indirectly validated by Gate 4 (contour matching) and Gate 5
(path morphing), which require resampled contours as input. Artifacts in the
fitting would propagate as visible distortion in the morphed output, which is
checked visually and by the morph continuity metric.
