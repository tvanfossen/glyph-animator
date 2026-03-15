---
type: constants
description: "Universal mathematical constants from nature — foundational values used across all algorithms"

constants:
  PHI:
    value: 1.6180339887498949
    description: "The golden ratio — (1+√5)/2"
    derivation: "Positive root of x² - x - 1 = 0"
    unit: dimensionless

  GOLDEN_ANGLE:
    value: 2.3999632297286533
    unit: radians
    description: "The angle that produces maximum angular dispersion in phyllotaxis"
    derivation: "2π(2 - φ) where φ is the golden ratio"
    equivalent_degrees: 137.508

  LENGTH_DECAY:
    value: 0.6180339887498949
    description: "Golden ratio reciprocal — each L-system generation shrinks by this factor"
    derivation: "1/φ = φ - 1"
    unit: dimensionless

  GAUSS_5PT:
    description: "5-point Legendre-Gauss quadrature nodes and weights"
    source: "Abramowitz & Stegun Table 25.4"
    nodes: [0.0, -0.5384693101056831, 0.5384693101056831, -0.9061798459386640, 0.9061798459386640]
    weights: [0.5688888888888889, 0.4786286704993665, 0.4786286704993665, 0.2369268850561891, 0.2369268850561891]
    error_order: 10
    description_detailed: "Approximates ∫f(x)dx over [-1,1]. Error is O(h^10) for smooth integrands. 5 points chosen to exactly integrate polynomials up to degree 9."

defaults:
  segment_count:
    value: 64
    description: "Default number of cubic bezier segments per resampled contour"
    range: [16, 256]

  newton_tolerance:
    value: 1.0e-12
    description: "Convergence threshold for Newton's method arc-length inverse"
    range: [1.0e-15, 1.0e-6]

  newton_max_iterations:
    value: 50
    description: "Maximum Newton iterations before returning best estimate"
    range: [5, 200]

  speed_epsilon:
    value: 1.0e-15
    description: "Minimum derivative magnitude before fallback to bisection"

  arc_length_epsilon:
    value: 1.0e-10
    description: "Threshold below which a contour is considered degenerate"
---

# Mathematical Constants

This document defines all fixed mathematical constants and algorithm defaults used by
the glyph-animator library. Values are loaded at runtime by the `ConfigManager` and
injected into algorithm constructors.

## Golden Ratio (φ)

The golden ratio φ = (1+√5)/2 ≈ 1.618 is the positive root of x² − x − 1 = 0.

It appears throughout the library:
- **Golden angle** (2π(2−φ) ≈ 137.508°): optimal angular dispersion in phyllotaxis
- **Length decay** (1/φ = φ−1 ≈ 0.618): L-system branch shortening per generation
- **Fibonacci spirals**: petal and flower placement patterns

The golden ratio's continued fraction [1; 1, 1, 1, ...] makes it the "most irrational"
number — successive placements at golden-angle intervals never align into visible rows.
This is proven by the three-distance theorem (Steinhaus 1957).

## Gauss Quadrature

5-point Legendre-Gauss quadrature approximates definite integrals:

$$\int_{-1}^{1} f(x)\,dx \approx \sum_{i=1}^{5} w_i f(x_i)$$

Mapped to arbitrary interval [a, b]:

$$\int_a^b f(t)\,dt = \frac{b-a}{2} \sum_{i=1}^{5} w_i f\!\left(\frac{b-a}{2}x_i + \frac{a+b}{2}\right)$$

The nodes and weights are tabulated in Abramowitz & Stegun (1964), Table 25.4.
Error is O(h¹⁰) — the quadrature exactly integrates polynomials up to degree 9.

For cubic bezier arc length (integrand is √(polynomial)), measured error is < 10⁻⁶
font units across all test glyphs at 1000 units/em.

## Newton's Method Defaults

Arc-length inverse uses Newton's method: t_{n+1} = tₙ − (L(tₙ) − s) / |B'(tₙ)|

- Tolerance 10⁻¹² ensures sub-pixel accuracy at any practical render resolution
- Typically converges in 3-5 iterations (quadratic convergence)
- Fallback to bisection when |B'(t)| < speed_epsilon (degenerate segment)
- Max iterations is a safety bound, rarely reached
