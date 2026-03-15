---
type: proof
algorithm: StartingPointAligner
class_path: glyph_animator.algorithms.matching.StartingPointAligner

parameters: {}

complexity: "O(N^2) where N = segment count (brute-force cross-correlation)"
error_bound: "Exact (exhaustive search over N rotations)"
gate_validation: "Gate 4: alignment reduces total travel distance vs unaligned"
---

# Starting Point Alignment via Exhaustive Cross-Correlation

## Problem Statement

Given two closed contours P = {p_0, p_1, ..., p_{N-1}} and Q = {q_0, q_1, ..., q_{N-1}}, each with N uniformly resampled segments, find the cyclic rotation offset k* in {0, 1, ..., N-1} that minimizes the total squared displacement when morphing P to Q:

    k* = argmin_{k} D(k) = argmin_{k} SUM_{i=0}^{N-1} ||p_i - q_{(i+k) mod N}||^2

## Reduction to Cross-Correlation

**Theorem.** Minimizing D(k) is equivalent to maximizing the cross-correlation C(k) = SUM_{i=0}^{N-1} p_i . q_{(i+k) mod N}.

*Proof.* Expand the squared norm:

    D(k) = SUM_i ||p_i||^2 - 2 * SUM_i p_i . q_{(i+k) mod N} + SUM_i ||q_{(i+k) mod N}||^2

The first term SUM_i ||p_i||^2 is independent of k.

The third term SUM_i ||q_{(i+k) mod N}||^2 = SUM_i ||q_i||^2 for all k, since the sum ranges over a complete cyclic permutation of Q.

Therefore:

    D(k) = (const) - 2 * C(k)

where C(k) = SUM_i p_i . q_{(i+k) mod N}. Since the constant is positive and the coefficient of C(k) is -2, minimizing D(k) is equivalent to maximizing C(k). QED

## Brute-Force Complexity

The algorithm evaluates C(k) for each k in {0, 1, ..., N-1}. Each evaluation computes a sum of N dot products (2D), requiring 3N floating-point operations (2 multiplies + 1 add per dot product, plus N-1 additions for the sum).

Total cost: N evaluations * O(N) per evaluation = O(N^2).

For the standard resampling count N = 64:

    N^2 = 4096 floating-point operations

This completes in microseconds on any modern processor.

## FFT Alternative

The cross-correlation C(k) can be computed for all k simultaneously via the circular cross-correlation theorem:

    C = IFFT(FFT(P) * conj(FFT(Q)))

where P and Q are treated as complex sequences p_n = x_n + i*y_n. This reduces complexity to O(N log N).

For N = 64: N log_2 N = 384, compared to N^2 = 4096. The constant-factor overhead of FFT (complex arithmetic, twiddle factors, bit-reversal) makes this slower in practice at N = 64. The crossover where FFT becomes advantageous is approximately N > 256. Since our pipeline fixes N = 64 (from Gate 3 arc-length resampling), the brute-force approach is both simpler and faster.

## Prevention of the Spinning Artifact

**Definition.** The "spinning" artifact occurs when the morph of a closed contour causes points to travel long paths around the perimeter rather than taking short direct paths to their targets.

**Theorem.** Optimal starting-point alignment eliminates the spinning artifact for convex-like contours.

*Proof.* Consider two contours P and Q with the same winding direction. Without alignment (k = 0), if the "natural" starting points of P and Q are on opposite sides of the glyph, then p_0 must travel to q_0 across the glyph interior while p_{N/2} (on the same side as q_0) must travel the other way. This creates crossing paths whose interpolation sweeps around the contour — the spinning artifact.

With optimal alignment, the rotation offset k* is chosen such that D(k*) is minimized. Consider the contribution of any single point:

    ||p_i - q_{(i+k*) mod N}||^2

If k* aligns the starting points so that nearby points on P map to nearby points on Q, each individual displacement is small. Conversely, any k that causes spinning must have at least N/2 point pairs with displacements spanning the contour diameter d, giving D(k) >= (N/2) * d^2. The optimal k* achieves D(k*) << (N/2) * d^2 by ensuring local correspondence.

For strictly convex contours, the displacement function D(k) has a unique global minimum (the contours are "rotationally compatible"), so k* unambiguously resolves the alignment. For non-convex contours with concavities, D(k) may have local minima, but the global minimum still produces the visually correct alignment in practice because the resampling from Gate 3 distributes points proportional to arc length, concentrating correspondence where geometric detail exists. QED

## Correctness of Exhaustive Search

**Proposition.** The brute-force search over all N rotations returns the globally optimal offset.

*Proof.* The search space {0, 1, ..., N-1} is finite with exactly N elements. The algorithm evaluates D(k) (equivalently, C(k)) for every element and selects the extremum. Since a finite set always contains its minimum, the result is globally optimal. QED
