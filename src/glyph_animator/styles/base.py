"""Base class for animation styles.

Each style implements three distinct animation types:
- Creation: glyph appears from nothing
- Destruction: glyph disappears (NOT reversed creation)
- Transition: glyph A morphs into glyph B

Styles receive RenderedGlyph(s) and produce Lottie layer dicts.
The base class owns common layer construction utilities.
Concrete styles implement only thin hooks: _create_layers,
_destroy_layers, _transition_layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from glyph_animator.models.geometry import MatchedPair
from glyph_animator.renderer.base import RenderedGlyph


class StyleBase(ABC):
    """Base class for all animation styles.

    Provides:
    - Public API: build_creation, build_destruction, build_transition
    - Utilities: _extract_geometry, _contours_to_paths,
      _make_shape_layer, _make_animated_layer
    """

    def __init__(self, name: str, duration_frames: int = 60, fps: int = 30):
        self.name = name
        self.duration_frames = duration_frames
        self.fps = fps

    # --- Public API (template methods) ---

    def build_creation(self, rendered: RenderedGlyph) -> list[dict]:
        """Build Lottie layers for glyph appearing from nothing."""
        return self._create_layers(rendered)

    def build_destruction(self, rendered: RenderedGlyph) -> list[dict]:
        """Build Lottie layers for glyph disappearing."""
        return self._destroy_layers(rendered)

    def build_transition(
        self,
        rendered_a: RenderedGlyph,
        rendered_b: RenderedGlyph,
        pairs: list[MatchedPair],
    ) -> list[dict]:
        """Build Lottie layers for glyph A -> glyph B."""
        return self._transition_layers(rendered_a, rendered_b, pairs)

    # --- Abstract hooks (concrete styles implement these) ---

    @abstractmethod
    def _create_layers(self, rendered: RenderedGlyph) -> list[dict]:
        """Glyph appears from nothing."""

    @abstractmethod
    def _destroy_layers(self, rendered: RenderedGlyph) -> list[dict]:
        """Glyph disappears. Distinct from reversed creation."""

    @abstractmethod
    def _transition_layers(
        self,
        rendered_a: RenderedGlyph,
        rendered_b: RenderedGlyph,
        pairs: list[MatchedPair],
    ) -> list[dict]:
        """Glyph A transforms into glyph B."""

    # --- Shared utilities ---

    def _extract_geometry(self, rendered: RenderedGlyph):
        """Extract center and radius from RenderedGlyph bounds."""
        b = rendered.glyph.bounds
        center = ((b.x_min + b.x_max) / 2, (b.y_min + b.y_max) / 2)
        radius = max(b.width, b.height) * 0.6
        return center, radius

    def _contours_to_paths(self, rendered: RenderedGlyph) -> list[dict]:
        """Convert all fitted contours to Lottie path dicts."""
        from glyph_animator.lottie.paths import contour_to_lottie_path

        return [contour_to_lottie_path(c.to_tuples()) for c in rendered.fitted_contours]

    def _make_shape_layer(self, name, shapes, op=None):
        """Build a standard Lottie shape layer dict."""
        from glyph_animator.lottie.builder import static_val

        return {
            "ty": 4,
            "nm": name,
            "sr": 1,
            "ks": {
                "p": static_val([0, 0, 0]),
                "a": static_val([0, 0, 0]),
                "s": static_val([100, 100, 100]),
                "r": static_val(0),
                "o": static_val(100),
            },
            "ao": 0,
            "shapes": shapes,
            "ip": 0,
            "op": op or (self.duration_frames + 30),
            "st": 0,
        }

    def _make_animated_layer(self, name, shapes, animated_ks, op=None):
        """Shape layer with animated transform properties."""
        layer = self._make_shape_layer(name, shapes, op)
        layer["ks"].update(animated_ks)
        return layer
