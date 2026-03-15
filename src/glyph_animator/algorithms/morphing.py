"""Path morphing via linear interpolation of cubic Bézier control points."""

from __future__ import annotations

from glyph_animator.algorithms.base import Algorithm

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class PathMorpher(Algorithm[tuple, list[Seg]]):
    """Linearly interpolate between two compatible contours at parameter α."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/07_path_interpolation.md"

    @property
    def complexity(self) -> str:
        return "O(N) where N = segment count"

    @property
    def error_bound(self) -> str:
        return "Exact (linear interpolation of control points)"

    def execute(self, input_data: tuple) -> list[Seg]:
        contour_a, contour_b, alpha = input_data
        return morph_contours(contour_a, contour_b, alpha)


def morph_contours(contour_a: list[Seg], contour_b: list[Seg], alpha: float) -> list[Seg]:
    """Linear interpolation of all control points at parameter α ∈ [0, 1]."""
    result = []
    for sa, sb in zip(contour_a, contour_b, strict=False):
        seg = tuple(
            (sa[i][0] + alpha * (sb[i][0] - sa[i][0]), sa[i][1] + alpha * (sb[i][1] - sa[i][1]))
            for i in range(4)
        )
        result.append(seg)
    return result
