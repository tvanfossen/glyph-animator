"""Contour matching: Hungarian assignment, cost matrix, contour geometry."""

from __future__ import annotations

from itertools import permutations

from glyph_animator.algorithms.base import Algorithm

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class HungarianMatcher(Algorithm[list[list[float]], list[tuple[int, int]]]):
    """Solve linear assignment via brute-force permutation search.

    For k ≤ 5 contours, k! ≤ 120 — simpler and equally fast as full Hungarian.
    """

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/05_contour_matching.md"

    @property
    def complexity(self) -> str:
        return "O(k!) where k ≤ 5"

    @property
    def error_bound(self) -> str:
        return "Exact (optimal assignment)"

    def execute(self, input_data: list[list[float]]) -> list[tuple[int, int]]:
        return hungarian_match(input_data)


# --- Free functions ---


def hungarian_match(cost_matrix: list[list[float]]) -> list[tuple[int, int]]:
    """Optimal assignment via brute-force permutation (k ≤ 5)."""
    n = len(cost_matrix)
    if n == 0:
        return []
    if n == 1:
        return [(0, 0)]

    best_cost = float("inf")
    best_perm: tuple[int, ...] | None = None

    for perm in permutations(range(n)):
        cost = sum(cost_matrix[i][perm[i]] for i in range(n))
        if cost < best_cost:
            best_cost = cost
            best_perm = perm

    assert best_perm is not None
    return [(i, best_perm[i]) for i in range(n)]


def contour_centroid(contour: list[Seg]) -> Pt:
    """Average of all segment start points."""
    if not contour:
        return (0.0, 0.0)
    pts = [seg[0] for seg in contour]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return (cx, cy)


def contour_signed_area(contour: list[Seg]) -> float:
    """Signed area via shoelace formula. Positive = CCW."""
    pts = [seg[0] for seg in contour]
    n = len(pts)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
    return area / 2.0


def make_degenerate_contour(center: Pt, n_segments: int) -> list[Seg]:
    """All control points at center — grows from / shrinks to a point."""
    return [(center, center, center, center)] * n_segments


class ContourSet:
    """Bundle of contours + their computed centroids and areas."""

    __slots__ = ("contours", "centroids", "areas", "n_real")

    def __init__(self, contours: list[list[Seg]]):
        self.contours = list(contours)
        self.centroids = [contour_centroid(c) for c in contours]
        self.areas = [contour_signed_area(c) for c in contours]
        self.n_real = len(contours)

    def pad_to(self, k: int, other_centroids: list[Pt], target_n: int) -> None:
        """Add degenerate contours to reach k total."""
        if self.n_real >= k:
            return
        cx = sum(c[0] for c in other_centroids) / len(other_centroids) if other_centroids else 0
        cy = sum(c[1] for c in other_centroids) / len(other_centroids) if other_centroids else 0
        for _ in range(k - self.n_real):
            self.contours.append(make_degenerate_contour((cx, cy), target_n))
            self.centroids.append((cx, cy))
            self.areas.append(0.0)


def match_contours(
    contours_a: list[list[Seg]],
    contours_b: list[list[Seg]],
    target_n: int,
) -> list[tuple[list[Seg], list[Seg]]]:
    """Match contours between two glyphs, padding with degenerates if needed."""
    set_a = ContourSet(contours_a)
    set_b = ContourSet(contours_b)
    k = max(set_a.n_real, set_b.n_real)

    set_a.pad_to(k, set_b.centroids, target_n)
    set_b.pad_to(k, set_a.centroids, target_n)

    cost_matrix = _build_cost_matrix(set_a, set_b, k)
    assignment = hungarian_match(cost_matrix)
    return _finalize_pairs(assignment, set_a, set_b, target_n)


def _build_cost_matrix(set_a: ContourSet, set_b: ContourSet, k: int):
    """Build assignment cost matrix from centroids and areas."""
    all_c = set_a.centroids + set_b.centroids
    max_dist_sq = max(
        ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 for c1 in all_c for c2 in all_c),
        default=1.0,
    )
    max_dist_sq = max(max_dist_sq, 1e-10)

    all_areas = [abs(a) for a in set_a.areas + set_b.areas]
    max_area = max(max(all_areas), 1e-10) if all_areas else 1.0

    cost = []
    for i in range(k):
        row = []
        for j in range(k):
            dx = set_a.centroids[i][0] - set_b.centroids[j][0]
            dy = set_a.centroids[i][1] - set_b.centroids[j][1]
            cent_cost = (dx * dx + dy * dy) / max_dist_sq
            area_cost = ((abs(set_a.areas[i]) - abs(set_b.areas[j])) / max_area) ** 2
            winding = _winding_penalty(set_a.areas[i], set_b.areas[j])
            row.append(cent_cost + area_cost + winding)
        cost.append(row)
    return cost


def _winding_penalty(area_a: float, area_b: float) -> float:
    """Penalize matching contours with opposite winding direction."""
    if (area_a > 0) != (area_b > 0) and abs(area_a) > 1e-5 and abs(area_b) > 1e-5:
        return 2.0
    return 0.0


def _finalize_pairs(assignment, set_a: ContourSet, set_b: ContourSet, target_n):
    """Build final pairs, relocating degenerates to partner centroids."""
    pairs = []
    for i, j in assignment:
        ca = set_a.contours[i]
        cb = set_b.contours[j]
        if i >= set_a.n_real:
            ca = make_degenerate_contour(set_b.centroids[j], target_n)
        if j >= set_b.n_real:
            cb = make_degenerate_contour(set_a.centroids[i], target_n)
        pairs.append((ca, cb))
    return pairs
