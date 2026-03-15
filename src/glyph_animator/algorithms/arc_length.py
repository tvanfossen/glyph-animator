"""Arc-length computation and inverse via Gauss quadrature and Newton's method."""

from __future__ import annotations

from glyph_animator.algorithms.base import Algorithm
from glyph_animator.algorithms.curves import derivative_magnitude, eval_cubic_derivative
from glyph_animator.constants import (
    ARC_LENGTH_EPSILON,
    GAUSS_5PT_NODES,
    GAUSS_5PT_WEIGHTS,
    NEWTON_MAX_ITERATIONS,
    NEWTON_TOLERANCE,
    SPEED_EPSILON,
)

# Type alias for a cubic segment as 4 tuples
Seg = tuple[
    tuple[float, float],
    tuple[float, float],
    tuple[float, float],
    tuple[float, float],
]


class GaussQuadratureArcLength(Algorithm[tuple, float]):
    """Compute arc length of a cubic bezier segment using 5-point Gauss quadrature.

    Maps ∫[a,b] |B'(t)| dt to [-1,1] via:
        ((b-a)/2) Σᵢ wᵢ |B'((b-a)/2·xᵢ + (a+b)/2)|
    """

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/02_arc_length_quadrature.md"

    @property
    def complexity(self) -> str:
        return "O(1) per segment (5 function evaluations)"

    @property
    def error_bound(self) -> str:
        return "< 10⁻⁶ absolute for font-scale coordinates (0-1000 units)"

    def execute(self, input_data: tuple) -> float:
        c0, c1, c2, c3 = input_data[:4]
        t_start = input_data[4] if len(input_data) > 4 else 0.0
        t_end = input_data[5] if len(input_data) > 5 else 1.0
        return segment_arc_length(c0, c1, c2, c3, t_start, t_end)


class NewtonInverse(Algorithm[tuple, tuple[float, int]]):
    """Find parameter t such that arc_length(0, t) = target via Newton's method."""

    def __init__(
        self,
        tolerance: float = NEWTON_TOLERANCE,
        max_iterations: int = NEWTON_MAX_ITERATIONS,
    ):
        self.tolerance = tolerance
        self.max_iterations = max_iterations

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/02_arc_length_quadrature.md"

    @property
    def complexity(self) -> str:
        return "O(1) per query (~4 iterations, quadratic convergence)"

    @property
    def error_bound(self) -> str:
        return f"< {self.tolerance} (convergence tolerance)"

    def execute(self, input_data: tuple) -> tuple[float, int]:
        c0, c1, c2, c3, target_len, total_len = input_data
        return arc_length_inverse(c0, c1, c2, c3, target_len, total_len)


# --- Free functions ---


def segment_arc_length(
    c0: tuple[float, float],
    c1: tuple[float, float],
    c2: tuple[float, float],
    c3: tuple[float, float],
    t_start: float = 0.0,
    t_end: float = 1.0,
) -> float:
    """Compute arc length of a cubic bezier from t_start to t_end."""
    half_range = (t_end - t_start) / 2.0
    mid = (t_start + t_end) / 2.0
    total = 0.0
    for node, weight in zip(GAUSS_5PT_NODES, GAUSS_5PT_WEIGHTS, strict=False):
        t = half_range * node + mid
        speed = derivative_magnitude(c0, c1, c2, c3, t)
        total += weight * speed
    return half_range * total


def contour_arc_lengths(
    contour: list[Seg],
) -> tuple[list[float], list[float]]:
    """Compute per-segment and cumulative arc lengths.

    Returns (segment_lengths, cumulative_lengths).
    """
    seg_lens = []
    cum_lens = []
    running = 0.0
    for seg in contour:
        length = segment_arc_length(*seg)
        seg_lens.append(length)
        running += length
        cum_lens.append(running)
    return seg_lens, cum_lens


def arc_length_inverse(
    c0: tuple[float, float],
    c1: tuple[float, float],
    c2: tuple[float, float],
    c3: tuple[float, float],
    target_len: float,
    total_len: float,
) -> tuple[float, int]:
    """Find t such that arc_length(0, t) = target_len via Newton's method.

    Returns (t, iterations_used). Guard clauses handle degenerate/boundary cases.
    """
    # Boundary cases: degenerate, at start, or at end
    if total_len < ARC_LENGTH_EPSILON or target_len <= 0 or target_len >= total_len:
        t_boundary = 0.0 if (total_len < ARC_LENGTH_EPSILON or target_len <= 0) else 1.0
        return t_boundary, 0

    t = target_len / total_len  # Linear initial guess

    for iteration in range(NEWTON_MAX_ITERATIONS):
        current_len = segment_arc_length(c0, c1, c2, c3, 0.0, t)
        error = current_len - target_len

        if abs(error) < NEWTON_TOLERANCE:
            return t, iteration + 1

        dx, dy = eval_cubic_derivative(c0, c1, c2, c3, t)
        speed = (dx * dx + dy * dy) ** 0.5

        if speed < SPEED_EPSILON:
            t = t / 2.0 if error > 0 else (t + 1.0) / 2.0
            continue

        t = max(0.0, min(1.0, t - error / speed))

    return t, NEWTON_MAX_ITERATIONS
