"""Concrete digit renderer: produces outline stack, matte, and arc samples."""

from __future__ import annotations

from glyph_animator.models.geometry import GlyphData
from glyph_animator.renderer.base import GlyphRendererBase, OutlineLayer


class GlyphRenderer(GlyphRendererBase):
    """Render a glyph into structural layers.

    Thin subclass — only implements _build_outlines() to define
    the concentric outline construction strategy. All other logic
    (render template, matte detection, arc sampling) lives in the base.
    """

    def __init__(self, n_outline_layers: int = 3, n_arc_samples: int = 100):
        super().__init__(n_arc_samples=n_arc_samples)
        self._n_outline_layers = n_outline_layers

    def _build_outlines(self, glyph: GlyphData) -> list[OutlineLayer]:
        """Build concentric outline layers with decreasing stroke width."""
        layers = []
        for i in range(self._n_outline_layers):
            offset = (i + 1) * 2.0
            width = max(1.0, 4.0 - i * 1.0)
            for contour in glyph.contours:
                layers.append(OutlineLayer(contour=contour, offset=offset, stroke_width=width))
        return layers
