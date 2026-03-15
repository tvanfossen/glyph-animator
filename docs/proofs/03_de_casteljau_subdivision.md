---
type: proof
algorithm: DeCasteljau
class_path: glyph_animator.algorithms.curves.DeCasteljau
parameters: null
complexity: "O(1) per split"
error_bound: "Exact (algebraic identity)"
gate_validation: "Gate 3 — subdivision used in resampling, verified by Hausdorff < 5.0"
---

# Proof 3: De Casteljau Subdivision is Algebraically Exact

## 1. Algorithm Definition

Given a cubic Bezier curve with control points (C_0, C_1, C_2, C_3) and a
parameter t in [0, 1], the De Casteljau algorithm computes two sub-curves by
three levels of linear interpolation:

**Level 1** (lerp between adjacent control points):

    Q_0 = (1-t) C_0 + t C_1
    Q_1 = (1-t) C_1 + t C_2
    Q_2 = (1-t) C_2 + t C_3

**Level 2** (lerp between level-1 points):

    R_0 = (1-t) Q_0 + t Q_1
    R_1 = (1-t) Q_1 + t Q_2

**Level 3** (lerp between level-2 points):

    S = (1-t) R_0 + t R_1

The algorithm outputs two curves:

    Left:  (C_0, Q_0, R_0, S)     representing B restricted to [0, t]
    Right: (S, R_1, Q_2, C_3)     representing B restricted to [t, 1]

This matches the implementation in `subdivide_cubic`.

## 2. The Split Point S Equals B(t)

**Theorem.** S = B(t).

**Proof.** Expand S by substituting all intermediate points:

    S = (1-t) R_0 + t R_1
      = (1-t)[(1-t) Q_0 + t Q_1] + t[(1-t) Q_1 + t Q_2]
      = (1-t)^2 Q_0 + 2(1-t)t Q_1 + t^2 Q_2

Now substitute the level-1 points:

    S = (1-t)^2 [(1-t) C_0 + t C_1]
      + 2(1-t)t [(1-t) C_1 + t C_2]
      + t^2 [(1-t) C_2 + t C_3]

    = (1-t)^3 C_0 + (1-t)^2 t C_1
      + 2(1-t)^2 t C_1 + 2(1-t) t^2 C_2
      + (1-t) t^2 C_2 + t^3 C_3

    = (1-t)^3 C_0 + 3(1-t)^2 t C_1 + 3(1-t) t^2 C_2 + t^3 C_3

    = B(t)

QED.

## 3. Left Curve Traces B on [0, t]

**Theorem.** Define L(s) as the cubic Bezier with control points (C_0, Q_0, R_0, S)
evaluated at parameter s in [0, 1]. Then L(s) = B(st) for all s in [0, 1].

**Proof.** We must show that the control points (C_0, Q_0, R_0, S) define a curve
that, when evaluated at s, gives the same point as the original curve at parameter
st.

Consider the original curve B(u) for u in [0, t]. Define the reparameterization
u = st, so s in [0, 1] maps to u in [0, t]. We need to express B(st) as a cubic
Bezier in s.

    B(st) = (1 - st)^3 C_0 + 3(1 - st)^2 (st) C_1 + 3(1 - st)(st)^2 C_2 + (st)^3 C_3

This is a cubic polynomial in s. We will verify that L(s) = (1-s)^3 C_0 +
3(1-s)^2 s Q_0 + 3(1-s) s^2 R_0 + s^3 S matches B(st) by comparing monomial
coefficients.

**Coefficient of s^0:**

    B(st)|_{s=0} = B(0) = C_0
    L(0) = C_0

**Coefficient of s^1:** (first derivative at s = 0, divided by 1)

    d/ds B(st)|_{s=0} = t B'(0) = t [3(C_1 - C_0)] = 3t(C_1 - C_0)
    L'(0) = 3(Q_0 - C_0) = 3[(1-t)C_0 + tC_1 - C_0] = 3t(C_1 - C_0)

**Coefficient of s^2:** (second derivative at s = 0, divided by 2)

    d^2/ds^2 B(st)|_{s=0} = t^2 B''(0) = t^2 [6(C_0 - 2C_1 + C_2)]
    L''(0) = 6(C_0 - 2Q_0 + R_0)

Expanding:
    C_0 - 2Q_0 + R_0
    = C_0 - 2[(1-t)C_0 + tC_1] + [(1-t)^2 C_0 + 2(1-t)t C_1 + t^2 C_2]

Collecting by control point:
    C_0 coefficient: 1 - 2(1-t) + (1-t)^2 = 1 - 2 + 2t + 1 - 2t + t^2 = t^2
    C_1 coefficient: -2t + 2(1-t)t = -2t + 2t - 2t^2 = -2t^2
    C_2 coefficient: t^2

    = t^2 (C_0 - 2C_1 + C_2)

So L''(0) = 6t^2(C_0 - 2C_1 + C_2) = t^2 B''(0). Matches.

**Coefficient of s^3:** (third derivative, divided by 6)

    d^3/ds^3 B(st) = t^3 B'''(0) = t^3 [-6C_0 + 18C_1 - 18C_2 + 6C_3]
                   = 6t^3(-C_0 + 3C_1 - 3C_2 + C_3)
    L'''(0) = 6(-C_0 + 3Q_0 - 3R_0 + S)

We compute -C_0 + 3Q_0 - 3R_0 + S:

    S = (1-t)^3 C_0 + 3(1-t)^2 t C_1 + 3(1-t)t^2 C_2 + t^3 C_3   (from Section 2)

    R_0 = (1-t)^2 C_0 + 2(1-t)t C_1 + t^2 C_2

    Q_0 = (1-t) C_0 + t C_1

Collecting coefficients of each C_i:

    C_0: -1 + 3(1-t) - 3(1-t)^2 + (1-t)^3

Let u = 1-t:
    = -1 + 3u - 3u^2 + u^3 = -(1 - 3u + 3u^2 - u^3) = -(1-u)^3 = -t^3

    C_1: 3t - 6(1-t)t + 3(1-t)^2 t = 3t[1 - 2(1-t) + (1-t)^2] = 3t[1-1+t]^2...

Let us compute more carefully:
    3t - 3[2(1-t)t] + 3(1-t)^2 t = 3t[1 - 2(1-t) + (1-t)^2] = 3t(1 - (1-t))^2 = 3t^3

    C_2: -3t^2 + 3(1-t)t^2 = 3t^2(-1 + 1 - t) = -3t^3

    C_3: t^3

So: -C_0 + 3Q_0 - 3R_0 + S = t^3(-C_0 + 3C_1 - 3C_2 + C_3)

Therefore L'''(0) = 6t^3(-C_0 + 3C_1 - 3C_2 + C_3) = t^3 B'''(0). Matches.

Since both B(st) and L(s) are cubic polynomials in s with identical coefficients
at s^0, s^1, s^2, s^3, they are the same polynomial. Therefore L(s) = B(st) for
all s in [0, 1]. QED.

## 4. Right Curve Traces B on [t, 1]

**Theorem.** Define R(s) as the cubic Bezier with control points (S, R_1, Q_2, C_3)
evaluated at parameter s in [0, 1]. Then R(s) = B(t + s(1-t)) for all s in [0, 1].

**Proof.** By the same argument structure as Section 3. The reparameterization
u = t + s(1-t) maps s in [0, 1] to u in [t, 1]. We verify that R(s) = B(t + s(1-t))
by comparing monomial coefficients.

At s = 0: R(0) = S = B(t). Correct.

At s = 1: R(1) = C_3 = B(1). Correct.

The derivative check follows identically by symmetry of the De Casteljau
construction. The right sub-curve control points are obtained by reading the
"right edge" of the De Casteljau triangle, and the same algebraic expansion
confirms all four monomial coefficients match.

(The full expansion is symmetric to Section 3 with t replaced by 1-t and the
parameter direction reversed. We omit the repetition.) QED.

## 5. Exactness: No Approximation

The De Casteljau algorithm consists entirely of linear interpolations (weighted
averages). Each lerp:

    lerp(A, B, t) = (1 - t) A + t B

is a single multiply-add operation. The three levels of lerp are composed, but the
composition of exact operations is exact. There is no truncation, no series
expansion, no iterative convergence.

The only error source is finite-precision floating-point arithmetic. Each lerp
introduces relative error bounded by machine epsilon. After three levels, the
accumulated relative error is at most 3 * epsilon ~ 6.7 x 10^{-16} per coordinate,
which is negligible for any practical application.

Algebraically, the De Casteljau subdivision is an **identity**: it produces control
points for sub-curves that trace the same geometric path as the original. No
information is lost or approximated.

## 6. Properties Preserved by Subdivision

The following properties hold for both sub-curves and are important for the
resampling pipeline:

1. **Continuity**: The left curve ends at S and the right curve starts at S,
   ensuring C^0 continuity at the split point.

2. **Tangent continuity**: The tangent of the left curve at s = 1 is
   proportional to R_0 -> S, and the tangent of the right curve at s = 0 is
   proportional to S -> R_1. Since R_0, S, R_1 are produced by the same lerp
   chain, these tangent directions agree (they are parallel), giving G^1
   continuity.

3. **Convex hull**: Each sub-curve lies within the convex hull of its four
   control points, which is a subset of the convex hull of the original four
   control points. This is the convex hull subdivision property.

## 7. Gate Validation

Gate 3 uses De Casteljau subdivision within the resampling pipeline to split
original contour segments at arc-length boundary points. The resampled contours
are validated by computing the Hausdorff distance to the original contours,
which must be < 5.0 font units. Since subdivision is exact, any Hausdorff error
arises solely from the least-squares cubic fitting step (Proof 4a), not from
the subdivision itself.
