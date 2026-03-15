"""Starting point alignment for matched contour pairs."""

from __future__ import annotations

import math

from glyph_animator.algorithms.base import Algorithm

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class StartingPointAligner(Algorithm[tuple, tuple]):
    """Find rotation offset k minimizing total squared distance between contours."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/06_starting_point_alignment.md"

    @property
    def complexity(self) -> str:
        return "O(N²) where N = segment count"

    @property
    def error_bound(self) -> str:
        return "Exact (exhaustive search over N rotations)"

    def execute(self, input_data: tuple) -> tuple:
        contour_a, contour_b = input_data
        return align_starting_points(contour_a, contour_b)


def align_starting_points(
    contour_a: list[Seg], contour_b: list[Seg]
) -> tuple[int, float, float, list[Seg]]:
    """Find rotation k for B minimizing total squared distance to A.

    Returns (best_k, unaligned_cost, aligned_cost, rotated_B).
    """
    pts_a = [seg[0] for seg in contour_a]
    pts_b = [seg[0] for seg in contour_b]
    n = len(pts_a)

    if n != len(pts_b) or n == 0:
        return 0, 0.0, 0.0, contour_b

    best_k = 0
    best_corr = -math.inf

    for k in range(n):
        corr = sum(
            pts_a[i][0] * pts_b[(i + k) % n][0] + pts_a[i][1] * pts_b[(i + k) % n][1]
            for i in range(n)
        )
        if corr > best_corr:
            best_corr = corr
            best_k = k

    unaligned = sum(
        (pts_a[i][0] - pts_b[i][0]) ** 2 + (pts_a[i][1] - pts_b[i][1]) ** 2 for i in range(n)
    )
    aligned = sum(
        (pts_a[i][0] - pts_b[(i + best_k) % n][0]) ** 2
        + (pts_a[i][1] - pts_b[(i + best_k) % n][1]) ** 2
        for i in range(n)
    )

    rotated = contour_b[best_k:] + contour_b[:best_k]
    return best_k, unaligned, aligned, rotated
