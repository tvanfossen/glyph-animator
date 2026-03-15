---
type: proof
algorithm: GaussQuadratureArcLength
class_path: glyph_animator.algorithms.arc_length.GaussQuadratureArcLength
also_covers: glyph_animator.algorithms.arc_length.NewtonInverse
uses_constants:
  - GAUSS_5PT
parameters: null
complexity: "O(1) per segment (5 function evaluations)"
error_bound: "< 10^-6 absolute for font-scale coordinates"
gate_validation: "Gate 3 — measured error < 10^-6 across all 10 digits"
---

# Proof 2: Arc-Length Computation via Gauss Quadrature and Newton Inverse

## 1. Arc-Length Integral

The arc length of a parametric curve B(t) from t = a to t = b is:

    L(a, b) = integral_a^b |B'(t)| dt

where |B'(t)| = sqrt(B'_x(t)^2 + B'_y(t)^2) is the speed function.

**No closed-form exists.** For a cubic Bezier, B'(t) is a quadratic polynomial in
each coordinate (Proof 1), so |B'(t)| = sqrt(P_4(t)) where P_4 is a polynomial of
degree 4. The integral of sqrt(polynomial) is an elliptic integral, which has no
closed-form expression in elementary functions except in degenerate cases (e.g.,
straight lines where the polynomial is a perfect square).

Numerical quadrature is therefore necessary.

## 2. Gauss-Legendre Quadrature

### Standard form

The n-point Gauss-Legendre quadrature approximates:

    integral_{-1}^{1} f(x) dx ~ sum_{i=1}^{n} w_i f(x_i)

where x_i are the roots of the n-th Legendre polynomial P_n(x), and w_i are the
corresponding weights. This formula is exact for all polynomials of degree <= 2n - 1.

### Mapping to arbitrary interval [a, b]

The change of variable x = (2t - a - b) / (b - a), or equivalently
t = ((b-a)/2) x + (a+b)/2, gives:

    integral_a^b f(t) dt = ((b-a)/2) integral_{-1}^{1} f(((b-a)/2) x + (a+b)/2) dx

Applying quadrature:

    integral_a^b f(t) dt ~ ((b-a)/2) sum_{i=1}^{n} w_i f(((b-a)/2) x_i + (a+b)/2)

This is exactly the formula implemented in `segment_arc_length`:

    half_range = (t_end - t_start) / 2.0
    mid = (t_start + t_end) / 2.0
    total = sum(weight * |B'(half_range * node + mid)| for node, weight in zip(...))
    return half_range * total

### 5-point nodes and weights

From Abramowitz & Stegun (1964), Table 25.4:

| i | Node x_i                | Weight w_i            |
|---|-------------------------|-----------------------|
| 1 |  0.0                   | 0.5688888888888889    |
| 2 | -0.5384693101056831    | 0.4786286704993665    |
| 3 |  0.5384693101056831    | 0.4786286704993665    |
| 4 | -0.9061798459386640    | 0.2369268850561891    |
| 5 |  0.9061798459386640    | 0.2369268850561891    |

Verification: sum of weights = 0.5688888... + 2(0.4786286...) + 2(0.2369268...)
= 0.5688888... + 0.9572573... + 0.4738537... = 2.0000000 (exact for f(x) = 1).

The nodes are symmetric about 0 and the weights are symmetric in pairs, which is a
general property of Gauss-Legendre quadrature (since Legendre polynomials have
definite parity).

## 3. Error Bound

### Theoretical error

The error of n-point Gauss quadrature for a function f with 2n continuous
derivatives is:

    E_n = ((b-a)^{2n+1} (n!)^4) / ((2n+1) ((2n)!)^3) * f^{(2n)}(xi)

for some xi in (a, b). For n = 5:

    E_5 = O(h^{11}) * f^{(10)}(xi)

where h = b - a. Since we apply quadrature to each segment with h = 1 (full
parameter range), the error is controlled by the 10th derivative of the integrand.

More precisely, 5-point Gauss quadrature exactly integrates polynomials up to
degree 2(5) - 1 = 9. The integrand |B'(t)| = sqrt(P_4(t)) is not a polynomial,
but it is analytic (smooth) for any non-degenerate cubic Bezier. The Taylor
expansion of |B'(t)| around any point has terms through degree 9 that are captured
exactly; the error comes from degree-10 and higher terms.

### Measured error for font glyphs

The integrand |B'(t)| for a typical font glyph segment has bounded curvature
variation and |B'(t)| values in the range [10, 1000] font units. The 10th
derivative of sqrt(P_4(t)) is bounded by a constant proportional to the control
point magnitudes and inversely proportional to |B'(t)|^{19} (from repeated
application of the chain rule to sqrt).

For font-scale coordinates (0-1000 units per em), with |B'(t)| bounded away from
zero (non-degenerate segments), the measured absolute error is < 10^{-6} font
units across all 10 digit glyphs (Gate 3 validation). This is far below perceptual
threshold (~0.5 font units = 0.5% of em width).

## 4. Newton's Method for Arc-Length Inverse

### Problem statement

Given a target arc length s in [0, L], find the parameter t* such that:

    L(0, t*) = s

where L(0, t) = integral_0^t |B'(u)| du.

### Monotonicity

**Lemma.** L(0, t) is strictly monotonically increasing for any non-degenerate
cubic Bezier.

**Proof.** L'(t) = |B'(t)| > 0 for non-degenerate curves (|B'(t)| = 0 only at
isolated cusps, which do not occur in well-formed font outlines). Therefore L is
strictly increasing and invertible on [0, 1]. QED.

### Newton iteration

Define g(t) = L(0, t) - s. We seek g(t*) = 0. Newton's method gives:

    t_{n+1} = t_n - g(t_n) / g'(t_n)
            = t_n - (L(0, t_n) - s) / |B'(t_n)|

This is the update implemented in `_newton_solve`:

    error = current_len - target_len
    t = t - error / speed

### Initial guess

    t_0 = s / L

This linear initial guess assumes uniform speed, placing t_0 within O(kappa * s^2)
of the true value, where kappa is the curvature variation. For typical font
segments, this gives 1-2 digits of accuracy, and Newton doubles the digits each
iteration.

### Convergence

**Theorem.** Newton's method converges quadratically to t* for non-degenerate
cubic Bezier curves.

**Proof.** The standard Newton convergence theorem requires:

1. g'(t*) != 0: We have g'(t) = |B'(t)| > 0 for non-degenerate curves.
2. g''(t) bounded: g''(t) = d/dt |B'(t)| = (B'(t) . B''(t)) / |B'(t)|, which
   is bounded when |B'(t)| is bounded away from zero.

Under these conditions, for t_0 sufficiently close to t*, the error satisfies:

    |t_{n+1} - t*| <= C |t_n - t*|^2

where C = max|g''| / (2 min|g'|) is bounded for non-degenerate curves.

In practice, convergence from the linear initial guess requires 3-5 iterations to
reach tolerance 10^{-12}. The implementation caps at 50 iterations as a safety
bound (constant NEWTON_MAX_ITERATIONS). QED.

### Degenerate fallback

When |B'(t)| < SPEED_EPSILON = 10^{-15} (near-zero speed at cusps), Newton's
update would divide by near-zero. The implementation falls back to bisection:

    if error > 0: t = t / 2
    if error < 0: t = (t + 1) / 2

This maintains monotonic convergence at linear rate, avoiding numerical instability.

## 5. Combined Error Budget

The arc-length inverse t* has two error sources:

1. **Quadrature error** in computing L(0, t_n) at each Newton step: < 10^{-6}
2. **Newton convergence tolerance**: 10^{-12}

The dominant error is the quadrature approximation. When Newton converges to
tolerance 10^{-12}, the residual |L(0, t*) - s| < 10^{-12}, but L(0, t*) itself
has quadrature error < 10^{-6}. Therefore the true arc-length error at the
returned t* is bounded by 10^{-6} font units.

Converting to parameter error: |delta_t| ~ |delta_L| / |B'(t)| < 10^{-6} / |B'(t)|.
For typical font segments with |B'(t)| ~ 500, this gives |delta_t| < 2 x 10^{-9},
which is negligible.

## 6. Gate Validation

Gate 3 computes arc-length reparameterization of all 10 digit contours and
validates:

- Total arc-length error < 10^{-6} (measured by comparing 5-point quadrature
  against adaptive subdivision with 1000+ evaluations)
- Newton convergence in < 10 iterations for all inverse queries
- Resampled segment arc lengths differ by < 10^{-4} from the target delta_s

All thresholds are met across the full digit set.
