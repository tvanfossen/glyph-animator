"""Base class for animation styles.

Each style implements three distinct animation types:
- Creation: glyph appears from nothing
- Destruction: glyph disappears (NOT reversed creation)
- Transition: glyph A morphs into glyph B

Styles receive RenderedDigit(s) and produce Lottie layer dicts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from glyph_animator.models.geometry import MatchedPair
from glyph_animator.renderer.base import RenderedDigit


class StyleBase(ABC):
    """Abstract base class for all animation styles.

    The base class provides the public API (build_creation, build_destruction,
    build_transition) which delegates to abstract methods that concrete
    styles must implement.
    """

    def __init__(self, name: str, duration_frames: int = 60, fps: int = 30):
        self.name = name
        self.duration_frames = duration_frames
        self.fps = fps

    def build_creation(self, rendered: RenderedDigit) -> list[dict]:
        """Build Lottie layers for glyph appearing from nothing."""
        return self._build_creation(rendered)

    def build_destruction(self, rendered: RenderedDigit) -> list[dict]:
        """Build Lottie layers for glyph disappearing."""
        return self._build_destruction(rendered)

    def build_transition(
        self,
        rendered_a: RenderedDigit,
        rendered_b: RenderedDigit,
        pairs: list[MatchedPair],
    ) -> list[dict]:
        """Build Lottie layers for glyph A → glyph B."""
        return self._build_transition(rendered_a, rendered_b, pairs)

    @abstractmethod
    def _build_creation(self, rendered: RenderedDigit) -> list[dict]:
        """Glyph appears from nothing."""

    @abstractmethod
    def _build_destruction(self, rendered: RenderedDigit) -> list[dict]:
        """Glyph disappears. Distinct from reversed creation."""

    @abstractmethod
    def _build_transition(
        self,
        rendered_a: RenderedDigit,
        rendered_b: RenderedDigit,
        pairs: list[MatchedPair],
    ) -> list[dict]:
        """Glyph A transforms into glyph B."""
