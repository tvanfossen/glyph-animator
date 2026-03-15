"""Spatial algorithms: ray casting, interior sampling."""

from __future__ import annotations

from glyph_animator.algorithms.base import Algorithm

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class RayCastingTest(Algorithm[tuple[Pt, list[list[Pt]]], bool]):
    """Test if a point is inside a contour using ray casting.

    Cast a horizontal ray from the point to +∞. Count crossings
    with the polygon edges. Odd count = inside, even = outside.
    """

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/16_ray_casting.md"

    @property
    def complexity(self) -> str:
        return "O(N) where N = polygon edges"

    @property
    def error_bound(self) -> str:
        return "Exact for polygon boundaries"

    def execute(self, input_data: tuple[Pt, list[list[Pt]]]) -> bool:
        point, polygons = input_data
        return point_in_contours(point, polygons)


class InteriorSampler(Algorithm[tuple, list[Pt]]):
    """Sample random interior points within a glyph outline."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/16_ray_casting.md"

    @property
    def complexity(self) -> str:
        return "O(N·M) where N=candidates, M=polygon edges"

    @property
    def error_bound(self) -> str:
        return "Exact (ray casting boundary test)"

    def execute(self, input_data: tuple) -> list[Pt]:
        polygons, bounds, n_points = input_data
        return sample_interior_points(polygons, bounds, n_points, self.seed)


# --- Free functions ---


def point_in_polygon(pt: Pt, polygon: list[Pt]) -> bool:
    """Ray casting: is point inside polygon? Odd crossings = inside."""
    x, y = pt
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_contours(pt: Pt, polygons: list[list[Pt]]) -> bool:
    """Test if point is inside the glyph (inside outer, outside holes).

    Uses non-zero winding: point must be inside an odd number of contours.
    """
    count = sum(1 for poly in polygons if point_in_polygon(pt, poly))
    return count % 2 == 1


def sample_interior_points(
    polygons: list[list[Pt]],
    bounds: tuple[float, float, float, float],
    n_points: int,
    seed: int = 42,
) -> list[Pt]:
    """Sample n_points inside the glyph via rejection sampling."""
    x_min, y_min, x_max, y_max = bounds
    points: list[Pt] = []

    # Simple LCG for deterministic sampling without importing random
    state = seed
    max_attempts = n_points * 20

    for _ in range(max_attempts):
        if len(points) >= n_points:
            break
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        fx = state / 0x7FFFFFFF
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        fy = state / 0x7FFFFFFF
        x = x_min + fx * (x_max - x_min)
        y = y_min + fy * (y_max - y_min)
        if point_in_contours((x, y), polygons):
            points.append((x, y))

    return points
