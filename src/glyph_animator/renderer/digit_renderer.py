"""Concrete digit renderer: produces outline stack, matte, and arc samples."""

from __future__ import annotations

from glyph_animator.algorithms.arc_length import contour_arc_lengths
from glyph_animator.algorithms.curves import eval_cubic
from glyph_animator.models.geometry import Contour, GlyphData, Point
from glyph_animator.renderer.base import DigitRendererBase, OutlineLayer, RenderedDigit

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class DigitRenderer(DigitRendererBase):
    """Render a glyph into structural layers.

    Produces:
    - fitted_contours: the resampled contours (passthrough from pipeline)
    - outline_layers: N concentric outlines at increasing offsets
    - matte_contour: outermost contour (for clipping/masking)
    - arc_samples: points sampled at equal arc-length intervals per contour
    """

    def __init__(self, n_outline_layers: int = 3, n_arc_samples: int = 100):
        self._n_outline_layers = n_outline_layers
        self._n_arc_samples = n_arc_samples

    def render(self, glyph: GlyphData) -> RenderedDigit:
        """Produce RenderedDigit from processed GlyphData."""
        outlines = self._build_outlines(glyph)
        arc_samples = self._sample_arcs(glyph)
        matte = self._find_matte(glyph)

        return RenderedDigit(
            glyph=glyph,
            fitted_contours=glyph.contours,
            outline_layers=outlines,
            matte_contour=matte,
            arc_samples=arc_samples,
        )

    def _build_outlines(self, glyph: GlyphData) -> list[OutlineLayer]:
        """Build concentric outline layers with decreasing stroke width."""
        layers = []
        for i in range(self._n_outline_layers):
            offset = (i + 1) * 2.0
            width = max(1.0, 4.0 - i * 1.0)
            for contour in glyph.contours:
                layers.append(OutlineLayer(contour=contour, offset=offset, stroke_width=width))
        return layers

    def _sample_arcs(self, glyph: GlyphData) -> list[list[Point]]:
        """Sample equidistant points along each contour."""
        all_samples = []
        for contour in glyph.contours:
            segs = [seg.as_tuples() for seg in contour.segments]
            samples = _sample_contour_points(segs, self._n_arc_samples)
            all_samples.append([Point(x=p[0], y=p[1]) for p in samples])
        return all_samples

    def _find_matte(self, glyph: GlyphData) -> Contour | None:
        """Find the outermost contour (largest absolute area)."""
        if not glyph.contours:
            return None
        best = glyph.contours[0]
        best_area = _contour_area(best)
        for contour in glyph.contours[1:]:
            area = _contour_area(contour)
            if area > best_area:
                best_area = area
                best = contour
        return best


def _sample_contour_points(segs: list[Seg], n: int) -> list[Pt]:
    """Sample n points along a contour at equal arc-length intervals."""
    seg_lens, cum_lens = contour_arc_lengths(segs)
    total = cum_lens[-1] if cum_lens else 0.0
    if total < 1e-10:
        return [(segs[0][0][0], segs[0][0][1])] * n if segs else []

    points = []
    for k in range(n):
        target = k * total / n
        seg_idx, local_t = _find_segment_at_length(target, segs, seg_lens, cum_lens)
        pt = eval_cubic(*segs[seg_idx], local_t)
        points.append(pt)
    return points


def _find_segment_at_length(target, segs, seg_lens, cum_lens):
    """Find which segment contains the target arc length."""
    from glyph_animator.algorithms.arc_length import arc_length_inverse

    for i, cum in enumerate(cum_lens):
        if cum >= target - 1e-10:
            prev_cum = cum_lens[i - 1] if i > 0 else 0.0
            local_target = target - prev_cum
            t, _ = arc_length_inverse(*segs[i], local_target, seg_lens[i])
            return i, t
    return len(segs) - 1, 1.0


def _contour_area(contour: Contour) -> float:
    """Absolute area via shoelace on segment start points."""
    pts = [(seg.p0.x, seg.p0.y) for seg in contour.segments]
    n = len(pts)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
    return abs(area) / 2.0
