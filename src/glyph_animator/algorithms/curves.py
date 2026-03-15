"""Bezier curve evaluation and subdivision algorithms."""

from __future__ import annotations

import math

from glyph_animator.algorithms.base import Algorithm


class BezierEvaluator(Algorithm[tuple, tuple[float, float]]):
    """Evaluate cubic bezier B(t) = (1-t)³C₀ + 3(1-t)²tC₁ + 3(1-t)t²C₂ + t³C₃."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/01_bezier_evaluation.md"

    @property
    def complexity(self) -> str:
        return "O(1) per evaluation"

    @property
    def error_bound(self) -> str:
        return "Machine epsilon (float64)"

    def execute(self, input_data: tuple) -> tuple[float, float]:
        c0, c1, c2, c3, t = input_data
        return eval_cubic(c0, c1, c2, c3, t)


class BezierDerivative(Algorithm[tuple, tuple[float, float]]):
    """First derivative B'(t) = 3(1-t)²(C₁-C₀) + 6(1-t)t(C₂-C₁) + 3t²(C₃-C₂)."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/01_bezier_evaluation.md"

    @property
    def complexity(self) -> str:
        return "O(1) per evaluation"

    @property
    def error_bound(self) -> str:
        return "Machine epsilon (float64)"

    def execute(self, input_data: tuple) -> tuple[float, float]:
        c0, c1, c2, c3, t = input_data
        return eval_cubic_derivative(c0, c1, c2, c3, t)


class DeCasteljau(Algorithm[tuple, tuple]):
    """Split cubic bezier at parameter t into two exact sub-curves."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/03_de_casteljau_subdivision.md"

    @property
    def complexity(self) -> str:
        return "O(1) per split"

    @property
    def error_bound(self) -> str:
        return "Exact (algebraic identity)"

    def execute(self, input_data: tuple) -> tuple:
        c0, c1, c2, c3, t = input_data
        return subdivide_cubic(c0, c1, c2, c3, t)


# --- Free functions used by algorithms and directly by the pipeline ---


def eval_cubic(
    c0: tuple[float, float],
    c1: tuple[float, float],
    c2: tuple[float, float],
    c3: tuple[float, float],
    t: float,
) -> tuple[float, float]:
    """Evaluate cubic bezier at parameter t. Returns (x, y)."""
    mt = 1 - t
    mt2 = mt * mt
    mt3 = mt2 * mt
    t2 = t * t
    t3 = t2 * t
    x = mt3 * c0[0] + 3 * mt2 * t * c1[0] + 3 * mt * t2 * c2[0] + t3 * c3[0]
    y = mt3 * c0[1] + 3 * mt2 * t * c1[1] + 3 * mt * t2 * c2[1] + t3 * c3[1]
    return (x, y)


def eval_cubic_derivative(
    c0: tuple[float, float],
    c1: tuple[float, float],
    c2: tuple[float, float],
    c3: tuple[float, float],
    t: float,
) -> tuple[float, float]:
    """First derivative of cubic bezier at parameter t. Returns (dx, dy)."""
    mt = 1 - t
    mt2 = mt * mt
    t2 = t * t
    dx = 3 * mt2 * (c1[0] - c0[0]) + 6 * mt * t * (c2[0] - c1[0]) + 3 * t2 * (c3[0] - c2[0])
    dy = 3 * mt2 * (c1[1] - c0[1]) + 6 * mt * t * (c2[1] - c1[1]) + 3 * t2 * (c3[1] - c2[1])
    return (dx, dy)


def derivative_magnitude(
    c0: tuple[float, float],
    c1: tuple[float, float],
    c2: tuple[float, float],
    c3: tuple[float, float],
    t: float,
) -> float:
    """Speed |B'(t)| at parameter t."""
    dx, dy = eval_cubic_derivative(c0, c1, c2, c3, t)
    return math.sqrt(dx * dx + dy * dy)


def lerp_point(
    a: tuple[float, float],
    b: tuple[float, float],
    t: float,
) -> tuple[float, float]:
    """Linear interpolation between two 2D points."""
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def subdivide_cubic(
    c0: tuple[float, float],
    c1: tuple[float, float],
    c2: tuple[float, float],
    c3: tuple[float, float],
    t: float,
) -> tuple[tuple, tuple]:
    """Split cubic bezier at t via De Casteljau. Returns (left, right).

    Left = (P₀, Q₀, R₀, S) for [0, t]
    Right = (S, R₁, Q₂, P₃) for [t, 1]
    """
    q0 = lerp_point(c0, c1, t)
    q1 = lerp_point(c1, c2, t)
    q2 = lerp_point(c2, c3, t)
    r0 = lerp_point(q0, q1, t)
    r1 = lerp_point(q1, q2, t)
    s = lerp_point(r0, r1, t)
    return (c0, q0, r0, s), (s, r1, q2, c3)
