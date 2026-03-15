"""Base class and data model for digit rendering."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from glyph_animator.models.geometry import Contour, GlyphData, Point

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class OutlineLayer(BaseModel):
    """A single outline edge at a specific offset from the glyph boundary."""

    contour: Contour
    offset: float
    stroke_width: float


class RenderedDigit(BaseModel):
    """Structural rendering of a digit — consumed by styles.

    The renderer produces these structural elements. Styles layer
    visual content (fills, decorations, animations) on top.
    Adding a new style never touches the renderer.
    """

    glyph: GlyphData
    fitted_contours: list[Contour]
    outline_layers: list[OutlineLayer]
    matte_contour: Contour | None = None
    arc_samples: list[list[Point]] = []


class DigitRendererBase(ABC):
    """Base class for digit renderers.

    Subclasses implement _render() to produce a RenderedDigit from
    processed GlyphData. The base class provides common utilities.
    """

    @abstractmethod
    def render(self, glyph: GlyphData) -> RenderedDigit:
        """Produce structural rendering of a glyph."""
