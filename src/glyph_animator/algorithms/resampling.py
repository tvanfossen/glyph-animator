"""Contour resampling to N equidistant segments via arc-length parameterization."""

from __future__ import annotations

from glyph_animator.algorithms.arc_length import (
    arc_length_inverse,
    contour_arc_lengths,
    segment_arc_length,
)
from glyph_animator.algorithms.base import Algorithm
from glyph_animator.algorithms.curves import eval_cubic, lerp_point, subdivide_cubic
from glyph_animator.constants import ARC_LENGTH_EPSILON, DEFAULT_SEGMENT_COUNT

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class ContourResampler(Algorithm[tuple[list[Seg], int], list[Seg]]):
    """Resample a contour to exactly N equidistant-arc-length segments.

    Algorithm:
    1. Compute total arc length, target spacing Δs = L/N
    2. Walk original segments, split at each boundary via Newton + De Casteljau
    3. Merge sub-segments between boundaries into single cubics via least-squares
    """

    def __init__(self, target_n: int = DEFAULT_SEGMENT_COUNT):
        self.target_n = target_n

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/04_point_normalization.md"

    @property
    def complexity(self) -> str:
        return "O(N·S) where N=target segments, S=original segments"

    @property
    def error_bound(self) -> str:
        return "< 5.0 font units (0.5% of em, <1px at any practical render size)"

    def execute(self, input_data: tuple[list[Seg], int]) -> list[Seg]:
        contour, target_n = input_data
        return resample_contour(contour, target_n)


class CubicFitter(Algorithm[list[Seg], Seg]):
    """Fit a single cubic bezier to a group of sequential sub-segments."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/04a_least_squares_fitting.md"

    @property
    def complexity(self) -> str:
        return "O(K) where K=sample count"

    @property
    def error_bound(self) -> str:
        return "Bounded by curvature variation within merged span"

    def execute(self, input_data: list[Seg]) -> Seg:
        return fit_cubic_to_group(input_data)


# --- Free functions ---


def resample_contour(contour: list[Seg], target_n: int) -> list[Seg]:
    """Resample contour to target_n equidistant segments."""
    _, cum_lens = contour_arc_lengths(contour)
    total_len = cum_lens[-1] if cum_lens else 0.0

    if total_len < ARC_LENGTH_EPSILON or not contour:
        return list(contour)

    delta_s = total_len / target_n
    sub_segments, boundary_indices = _split_at_boundaries(contour, delta_s, target_n)
    return _merge_groups(sub_segments, boundary_indices, target_n)


def _split_at_boundaries(
    contour: list[Seg], delta_s: float, target_n: int
) -> tuple[list[Seg], list[int]]:
    """Split all original segments at arc-length boundary points."""
    sub_segments: list[Seg] = []
    boundary_indices = [0]
    cum_arc = 0.0
    next_boundary = delta_s
    boundaries_placed = 0

    for seg in contour:
        current = seg
        current_len = segment_arc_length(*current)

        while boundaries_placed < target_n - 1:
            local_target = next_boundary - cum_arc

            if local_target > current_len + 1e-8:
                break

            if local_target < 1e-8:
                boundary_indices.append(len(sub_segments))
                boundaries_placed += 1
                next_boundary = (boundaries_placed + 1) * delta_s
                continue

            t, _ = arc_length_inverse(*current, local_target, current_len)
            left, right = subdivide_cubic(*current, t)

            sub_segments.append(left)
            cum_arc += segment_arc_length(*left)
            boundaries_placed += 1
            boundary_indices.append(len(sub_segments))
            next_boundary = (boundaries_placed + 1) * delta_s

            current = right
            current_len = segment_arc_length(*current)

        sub_segments.append(current)
        cum_arc += segment_arc_length(*current)

    boundary_indices.append(len(sub_segments))
    return sub_segments, boundary_indices


def _merge_groups(
    sub_segments: list[Seg], boundary_indices: list[int], target_n: int
) -> list[Seg]:
    """Merge sub-segments between boundaries into single cubics."""
    result: list[Seg] = []
    for i in range(target_n):
        start_idx = boundary_indices[i]
        end_idx = boundary_indices[i + 1] if i + 1 < len(boundary_indices) else len(sub_segments)
        group = sub_segments[start_idx:end_idx]

        if not group:
            pt = result[-1][3] if result else (0.0, 0.0)
            result.append((pt, pt, pt, pt))
        elif len(group) == 1:
            result.append(group[0])
        else:
            result.append(fit_cubic_to_group(group))

    return result


def fit_cubic_to_group(group: list[Seg]) -> Seg:
    """Fit a single cubic to sequential sub-segments via least-squares."""
    c0 = group[0][0]
    c3 = group[-1][3]

    group_lens = [segment_arc_length(*seg) for seg in group]
    total = sum(group_lens)
    if total < 1e-15:
        return (c0, c0, c3, c3)

    sample_pts, sample_ts = _sample_group(group, group_lens, total, n_samples=20)

    if len(sample_pts) < 2:
        mid = eval_cubic(*group[len(group) // 2], 0.5)
        c1 = (c0[0] + (mid[0] - c0[0]) * 1.5, c0[1] + (mid[1] - c0[1]) * 1.5)
        c2 = (c3[0] + (mid[0] - c3[0]) * 1.5, c3[1] + (mid[1] - c3[1]) * 1.5)
        return (c0, c1, c2, c3)

    return _solve_least_squares(c0, c3, sample_pts, sample_ts)


def _sample_group(
    group: list[Seg], group_lens: list[float], total: float, n_samples: int
) -> tuple[list[Pt], list[float]]:
    """Sample n_samples-1 interior points along a group of segments."""
    pts: list[Pt] = []
    ts: list[float] = []
    for k in range(1, n_samples):
        target = k * total / n_samples
        cum = 0.0
        for si, seg in enumerate(group):
            seg_len = group_lens[si]
            if cum + seg_len >= target - 1e-10:
                local_target = target - cum
                t_local, _ = arc_length_inverse(*seg, local_target, seg_len)
                pts.append(eval_cubic(*seg, t_local))
                ts.append(k / n_samples)
                break
            cum += seg_len
    return pts, ts


def _solve_least_squares(c0: Pt, c3: Pt, sample_pts: list[Pt], sample_ts: list[float]) -> Seg:
    """Solve 2x2 normal equations for C₁, C₂ given fixed C₀, C₃."""
    a11 = a12 = a22 = 0.0
    bx1 = by1 = bx2 = by2 = 0.0

    for pt, t in zip(sample_pts, sample_ts, strict=False):
        mt = 1 - t
        basis1 = 3 * mt * mt * t
        basis2 = 3 * mt * t * t

        rx = pt[0] - mt**3 * c0[0] - t**3 * c3[0]
        ry = pt[1] - mt**3 * c0[1] - t**3 * c3[1]

        a11 += basis1 * basis1
        a12 += basis1 * basis2
        a22 += basis2 * basis2
        bx1 += basis1 * rx
        by1 += basis1 * ry
        bx2 += basis2 * rx
        by2 += basis2 * ry

    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-20:
        c1 = lerp_point(c0, c3, 1 / 3)
        c2 = lerp_point(c0, c3, 2 / 3)
        return (c0, c1, c2, c3)

    c1x = (a22 * bx1 - a12 * bx2) / det
    c1y = (a22 * by1 - a12 * by2) / det
    c2x = (a11 * bx2 - a12 * bx1) / det
    c2y = (a11 * by2 - a12 * by1) / det
    return (c0, (c1x, c1y), (c2x, c2y), c3)
