"""Quadratic-to-cubic and line-to-cubic bezier conversion (algebraically exact)."""

from __future__ import annotations

from glyph_animator.algorithms.base import Algorithm

Pt = tuple[float, float]


class QuadToCubic(Algorithm[tuple[Pt, Pt, Pt], tuple[Pt, Pt, Pt, Pt]]):
    """Convert a quadratic bezier to an equivalent cubic.

    C₀ = P₀
    C₁ = P₀ + (2/3)(P₁ - P₀)
    C₂ = P₂ + (2/3)(P₁ - P₂)
    C₃ = P₂

    Algebraically exact — zero approximation error.
    """

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/01_bezier_evaluation.md"

    @property
    def complexity(self) -> str:
        return "O(1) per segment"

    @property
    def error_bound(self) -> str:
        return "Exact (algebraic identity)"

    def execute(self, input_data: tuple[Pt, Pt, Pt]) -> tuple[Pt, Pt, Pt, Pt]:
        p0, p1, p2 = input_data
        return quad_to_cubic(p0, p1, p2)


class LineToCubic(Algorithm[tuple[Pt, Pt], tuple[Pt, Pt, Pt, Pt]]):
    """Convert a line segment to a degenerate cubic bezier.

    C₀ = P₀
    C₁ = P₀ + (1/3)(P₁ - P₀)
    C₂ = P₀ + (2/3)(P₁ - P₀)
    C₃ = P₁

    Exact — evaluating the cubic at any t equals lerp(P₀, P₁, t).
    """

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/01_bezier_evaluation.md"

    @property
    def complexity(self) -> str:
        return "O(1) per segment"

    @property
    def error_bound(self) -> str:
        return "Exact (degenerate cubic)"

    def execute(self, input_data: tuple[Pt, Pt]) -> tuple[Pt, Pt, Pt, Pt]:
        p0, p1 = input_data
        return line_to_cubic(p0, p1)


# --- Free functions ---


def quad_to_cubic(p0: Pt, p1: Pt, p2: Pt) -> tuple[Pt, Pt, Pt, Pt]:
    """Convert quadratic (P₀, P₁, P₂) to cubic (C₀, C₁, C₂, C₃)."""
    c0 = p0
    c1 = (
        p0[0] + (2 / 3) * (p1[0] - p0[0]),
        p0[1] + (2 / 3) * (p1[1] - p0[1]),
    )
    c2 = (
        p2[0] + (2 / 3) * (p1[0] - p2[0]),
        p2[1] + (2 / 3) * (p1[1] - p2[1]),
    )
    c3 = p2
    return (c0, c1, c2, c3)


def line_to_cubic(p0: Pt, p1: Pt) -> tuple[Pt, Pt, Pt, Pt]:
    """Convert line (P₀, P₁) to degenerate cubic."""
    c0 = p0
    c1 = (
        p0[0] + (1 / 3) * (p1[0] - p0[0]),
        p0[1] + (1 / 3) * (p1[1] - p0[1]),
    )
    c2 = (
        p0[0] + (2 / 3) * (p1[0] - p0[0]),
        p0[1] + (2 / 3) * (p1[1] - p0[1]),
    )
    c3 = p1
    return (c0, c1, c2, c3)
