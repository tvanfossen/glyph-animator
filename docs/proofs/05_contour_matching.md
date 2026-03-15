---
type: proof
algorithm: HungarianMatcher
class_path: glyph_animator.algorithms.matching.HungarianMatcher

parameters:
  centroid_weight:
    value: 1.0
    type: float
    range: [0.0, 10.0]
    description: "Weight of centroid distance in cost function"
  area_weight:
    value: 1.0
    type: float
    range: [0.0, 10.0]
    description: "Weight of area difference in cost function"
  winding_penalty:
    value: 2.0
    type: float
    range: [0.0, 10.0]
    description: "Penalty for matching contours with opposite winding direction"

complexity: "O(k!) where k <= 5 (brute-force permutation)"
error_bound: "Exact (optimal assignment for given cost function)"
gate_validation: "Gate 4: all contours paired, degenerates correctly placed"
---

# Contour Matching via Optimal Assignment

## Problem Statement

Given a source glyph with contours S = {S_1, S_2, ..., S_k} and a target glyph with contours T = {T_1, T_2, ..., T_k}, find a bijection sigma: {1,...,k} -> {1,...,k} that minimizes the total matching cost. When contour counts differ, degenerate (zero-area) contours are synthesized to equalize the sets.

## Cost Function

The cost of matching source contour S_i to target contour T_j is defined as:

    cost(i, j) = alpha * ||c_i - c_j||^2 + beta * (A_i - A_j)^2 + gamma * W(i, j)

where:
- alpha = centroid_weight (default 1.0)
- beta = area_weight (default 1.0)
- gamma = winding_penalty (default 2.0)
- c_i, c_j are contour centroids
- A_i, A_j are signed contour areas
- W(i,j) = 1 if winding directions differ, 0 otherwise

### Centroid Definition

The centroid of a contour with N cubic Bezier segments is the average of all segment start points:

    c = (1/N) * SUM_{n=0}^{N-1} p_n^{(0)}

where p_n^{(0)} is the first control point (on-curve start) of segment n. This approximation is exact for uniformly resampled contours (which Gate 3 guarantees) and avoids the complexity of integrating along cubic arcs.

### Signed Area via Shoelace Formula

The signed area of a contour approximated by its N segment start points {(x_0, y_0), ..., (x_{N-1}, y_{N-1})} is:

    A = (1/2) * SUM_{n=0}^{N-1} (x_n * y_{n+1 mod N} - x_{n+1 mod N} * y_n)

**Proposition.** The sign of A encodes winding direction: A > 0 for counter-clockwise, A < 0 for clockwise.

*Proof.* The shoelace formula computes the signed area of a simple polygon. By Green's theorem, the line integral (1/2) * OINT (x dy - y dx) over a positively oriented (CCW) closed curve equals the enclosed area with positive sign. For CW orientation, the integral negates. Since the discrete shoelace formula is the trapezoidal approximation of this integral, the sign convention is preserved. QED

### Winding Penalty

The penalty term W(i,j) equals 1 when sign(A_i) != sign(A_j), and 0 otherwise. This discourages matching outer contours (CCW, positive area) to inner contours (CW, negative area, representing holes), since such pairings produce visually incorrect morphs where fills and holes swap roles.

## Optimality of Brute-Force Search

**Theorem.** For k contours with k <= 5, exhaustive enumeration of all k! permutations finds the globally optimal assignment.

*Proof.* The assignment problem seeks sigma* = argmin_{sigma in S_k} SUM_{i=1}^{k} cost(i, sigma(i)), where S_k is the symmetric group on k elements. Exhaustive search evaluates every element of S_k and selects the minimum. Since S_k is finite, the minimum exists and is found exactly.

The computational cost is O(k! * k): for each of k! permutations, summing k cost terms. The maximum case:

| k | k! | Operations |
|---|-----|------------|
| 1 | 1   | 1          |
| 2 | 2   | 4          |
| 3 | 6   | 18         |
| 4 | 24  | 96         |
| 5 | 120 | 600        |

At k = 5, 600 floating-point operations complete in microseconds. The general Hungarian algorithm (Kuhn 1955) solves this in O(k^3), which is asymptotically superior but unnecessary when k <= 5. The brute-force approach has the advantage of implementation simplicity and zero risk of algorithmic error in the augmenting-path logic.

**Justification for k <= 5.** Typographic glyphs in standard Latin fonts contain at most 5 contours. The most complex common case is the digit "8" with 3 contours (outer boundary plus two counter holes). Even decorative glyphs rarely exceed 5. QED

## Degenerate Contour Handling

When |S| != |T|, the deficit is filled with degenerate contours: zero-area contours collapsed to a single point at the centroid of the opposing glyph.

**Definition.** A degenerate contour D_c is a contour of N segments where all control points equal c (the target glyph centroid). Formally, for all segments n and all control points j in {0,1,2,3}: p_n^{(j)} = c.

**Properties of degenerate contours:**
1. Centroid: c_D = c (trivially)
2. Signed area: A_D = 0 (all cross products vanish)
3. Winding: undefined (area is zero); winding penalty is not applied

**Morphing behavior.** When a real contour S_i is matched to a degenerate D_c, the morph interpolation (1-alpha)*S_i + alpha*D_c causes the contour to smoothly collapse to point c as alpha -> 1. Conversely, matching D_c to a real target T_j causes the contour to grow from point c. This produces the visual effect of contours appearing or disappearing during the transition.

## References

- Kuhn, H. W. (1955). "The Hungarian method for the assignment problem." *Naval Research Logistics Quarterly*, 2(1-2), 83-97.
- Munkres, J. (1957). "Algorithms for the assignment and transportation problems." *Journal of the Society for Industrial and Applied Mathematics*, 5(1), 32-38.
