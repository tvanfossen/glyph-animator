---
type: proof
algorithm: BezierEvaluator
class_path: glyph_animator.algorithms.curves.BezierEvaluator
related_classes:
  - curves.BezierDerivative
  - conversion.QuadToCubic
  - conversion.LineToCubic
parameters: null
complexity: "O(1) per evaluation"
error_bound: "Machine epsilon (float64)"
gate_validation: "Gate 2 — max deviation < 10^-10 across all digits"
---

# Proof 1: Cubic Bezier Evaluation, Derivative, and Conversion Identities

## 1. Definition

A cubic Bezier curve with control points C_0, C_1, C_2, C_3 in R^2 is defined for
parameter t in [0, 1] as:

    B(t) = (1-t)^3 C_0 + 3(1-t)^2 t C_1 + 3(1-t) t^2 C_2 + t^3 C_3

Equivalently, expanding in powers of t:

    B(t) = C_0
         + t [-3C_0 + 3C_1]
         + t^2 [3C_0 - 6C_1 + 3C_2]
         + t^3 [-C_0 + 3C_1 - 3C_2 + C_3]

This is a polynomial of degree 3 in t with coefficients that are linear combinations
of the control points. Evaluation requires O(1) arithmetic operations.

## 2. Derivative Formula

**Theorem.** The first derivative of B(t) is:

    B'(t) = 3(1-t)^2 (C_1 - C_0) + 6(1-t)t (C_2 - C_1) + 3t^2 (C_3 - C_2)

**Proof.** Differentiate B(t) term by term.

Let u = 1 - t, so du/dt = -1. The Bernstein basis functions are:

    b_0(t) = u^3
    b_1(t) = 3u^2 t
    b_2(t) = 3u t^2
    b_3(t) = t^3

Their derivatives:

    b_0'(t) = 3u^2 (-1) = -3u^2
    b_1'(t) = 3[2u(-1)t + u^2] = 3u^2 - 6ut
    b_2'(t) = 3[-t^2 + 2ut] = 6ut - 3t^2
    b_3'(t) = 3t^2

Therefore:

    B'(t) = -3u^2 C_0 + (3u^2 - 6ut) C_1 + (6ut - 3t^2) C_2 + 3t^2 C_3

Collecting terms:

    B'(t) = 3u^2 (C_1 - C_0) + 6ut (C_2 - C_1) + 3t^2 (C_3 - C_2)

This is exactly a quadratic Bezier scaled by 3, with control points (C_1 - C_0),
(C_2 - C_1), (C_3 - C_2). These are the forward differences of the original
control points, and the factor of 3 = degree.

This matches the implementation in `eval_cubic_derivative`. QED.

## 3. Quadratic-to-Cubic Conversion Identity

**Theorem.** Given a quadratic Bezier Q(t) = (1-t)^2 P_0 + 2(1-t)t P_1 + t^2 P_2,
the cubic Bezier with control points:

    C_0 = P_0
    C_1 = P_0 + (2/3)(P_1 - P_0)
    C_2 = P_2 + (2/3)(P_1 - P_2)
    C_3 = P_2

evaluates identically to Q(t) for all t in [0, 1].

**Proof.** We show that the cubic polynomial B(t) with the stated control points
equals the quadratic polynomial Q(t) by expanding both in the monomial basis and
comparing coefficients.

**Quadratic expansion:**

    Q(t) = (1 - 2t + t^2) P_0 + (2t - 2t^2) P_1 + t^2 P_2
         = P_0 + t(-2P_0 + 2P_1) + t^2(P_0 - 2P_1 + P_2)

This is degree 2, so the t^3 coefficient is 0.

**Cubic expansion** with the given control points:

Substituting C_1 = P_0 + (2/3)(P_1 - P_0) = (1/3)P_0 + (2/3)P_1 and
C_2 = P_2 + (2/3)(P_1 - P_2) = (2/3)P_1 + (1/3)P_2 into the monomial form:

Constant term:
    C_0 = P_0

Coefficient of t:
    -3C_0 + 3C_1 = -3P_0 + 3[(1/3)P_0 + (2/3)P_1]
                  = -3P_0 + P_0 + 2P_1
                  = -2P_0 + 2P_1

Coefficient of t^2:
    3C_0 - 6C_1 + 3C_2 = 3P_0 - 6[(1/3)P_0 + (2/3)P_1] + 3[(2/3)P_1 + (1/3)P_2]
                        = 3P_0 - 2P_0 - 4P_1 + 2P_1 + P_2
                        = P_0 - 2P_1 + P_2

Coefficient of t^3:
    -C_0 + 3C_1 - 3C_2 + C_3 = -P_0 + 3[(1/3)P_0 + (2/3)P_1] - 3[(2/3)P_1 + (1/3)P_2] + P_2
                                = -P_0 + P_0 + 2P_1 - 2P_1 - P_2 + P_2
                                = 0

All four coefficients match exactly. The conversion introduces zero approximation
error; the only error source is floating-point representation of 2/3 and 1/3,
which is bounded by machine epsilon. QED.

## 4. Line-to-Cubic Conversion Identity

**Theorem.** Given a line segment L(t) = (1-t) P_0 + t P_1, the cubic Bezier with
control points:

    C_0 = P_0
    C_1 = P_0 + (1/3)(P_1 - P_0)
    C_2 = P_0 + (2/3)(P_1 - P_0)
    C_3 = P_1

evaluates identically to L(t) for all t in [0, 1].

**Proof.** We expand the cubic in the monomial basis.

C_1 = (2/3)P_0 + (1/3)P_1 and C_2 = (1/3)P_0 + (2/3)P_1.

Constant term:
    C_0 = P_0

Coefficient of t:
    -3C_0 + 3C_1 = -3P_0 + 3[(2/3)P_0 + (1/3)P_1]
                  = -3P_0 + 2P_0 + P_1
                  = -P_0 + P_1

Coefficient of t^2:
    3C_0 - 6C_1 + 3C_2 = 3P_0 - 6[(2/3)P_0 + (1/3)P_1] + 3[(1/3)P_0 + (2/3)P_1]
                        = 3P_0 - 4P_0 - 2P_1 + P_0 + 2P_1
                        = 0

Coefficient of t^3:
    -C_0 + 3C_1 - 3C_2 + C_3 = -P_0 + 3[(2/3)P_0 + (1/3)P_1] - 3[(1/3)P_0 + (2/3)P_1] + P_1
                                = -P_0 + 2P_0 + P_1 - P_0 - 2P_1 + P_1
                                = 0

Thus B(t) = P_0 + t(P_1 - P_0) = L(t). The cubic degenerates to a line with
control points equally spaced along the segment. QED.

## 5. Error Analysis

All three evaluations (cubic, derivative, conversions) are computed using direct
polynomial arithmetic in float64. The operations involve:

- Multiplications and additions of float64 values
- No transcendental functions, no divisions (except the fixed constants 1/3 and 2/3)
- No iterative procedures

By the standard model of floating-point arithmetic (IEEE 754), each elementary
operation introduces relative error at most epsilon = 2^{-52} ~ 2.22 x 10^{-16}.
For the cubic evaluation (approximately 15 floating-point operations), the accumulated
relative error is bounded by approximately 15 epsilon ~ 3.3 x 10^{-15}.

For font-scale coordinates (0-1000 units), this gives absolute error < 10^{-12},
which is well below the Gate 2 threshold of 10^{-10}.

The conversions (quad-to-cubic and line-to-cubic) are algebraically exact. The only
error source is representation of 1/3 and 2/3, each rounded to the nearest float64.
These constants have relative error < epsilon, propagating to absolute error
< epsilon * max(|P_i|) on the converted control points.

## 6. Gate Validation

Gate 2 tests extract all 10 digit glyphs from the font, convert all segments
(lines and quadratics) to cubics, and verify round-trip evaluation accuracy. The
measured maximum deviation across all converted glyphs is < 10^{-10} font units,
confirming that both conversion formulas and the evaluation formula are implemented
correctly.
