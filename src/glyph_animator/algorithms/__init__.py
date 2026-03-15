"""Pure math algorithms, each backed by a proof document."""

from glyph_animator.algorithms.alignment import StartingPointAligner, align_starting_points
from glyph_animator.algorithms.lsystem import LSystemGrower
from glyph_animator.algorithms.morphing import PathMorpher, morph_contours
from glyph_animator.algorithms.vogel import VogelSpiralPlacer, vogel_positions

__all__ = [
    "LSystemGrower",
    "PathMorpher",
    "StartingPointAligner",
    "VogelSpiralPlacer",
    "align_starting_points",
    "morph_contours",
    "vogel_positions",
]
