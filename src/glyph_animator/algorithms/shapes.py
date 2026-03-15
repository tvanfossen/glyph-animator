"""Vector shape generators for flowers, leaves, tendrils, and other decorations.

Each shape generator produces Lottie-compatible shape item dicts.
These are consumed by styles to build animation layers.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from glyph_animator.constants import PHI
from glyph_animator.lottie.builder import static_val


class ShapeGenerator(ABC):
    """Base class for decorative shape generators."""

    @abstractmethod
    def generate(self, index: int) -> list[dict]:
        """Generate Lottie shape items for one instance.

        index is used for deterministic variation (petal count, size, color).
        Returns list of Lottie shape item dicts (ellipses, paths, fills, etc).
        Must include a group transform ("ty": "tr") as the last item.
        """


class DaisyGenerator(ShapeGenerator):
    """Daisy flower: petals around a pistil center."""

    PETAL_COUNTS = (5, 6, 5, 8, 5, 6)
    DEFAULT_PALETTE = [
        [1.0, 0.51, 0.59],
        [1.0, 0.71, 0.39],
        [1.0, 0.39, 0.39],
        [0.71, 0.51, 1.0],
        [1.0, 0.86, 0.39],
        [1.0, 0.59, 0.78],
    ]

    def __init__(self, palette: list[list[float]] | None = None):
        self.palette = palette or self.DEFAULT_PALETTE

    def generate(self, index: int) -> list[dict]:
        n_petals = self.PETAL_COUNTS[index % len(self.PETAL_COUNTS)]
        color = self.palette[index % len(self.palette)]
        size_factor = 0.7 + 0.6 * ((index * PHI) % 1.0)
        return _build_daisy(n_petals, size_factor, color)


class LeafGenerator(ShapeGenerator):
    """Simple teardrop leaf shape."""

    def __init__(self, color: list[float] | None = None):
        self.color = color or [0.2, 0.6, 0.2]

    def generate(self, index: int) -> list[dict]:
        size = 8.0 + 4.0 * ((index * PHI) % 1.0)
        angle = index * 37.0  # degrees, deterministic spread
        return _build_leaf(size, angle, self.color)


class TendrilGenerator(ShapeGenerator):
    """Curling vine tendril as a stroked path."""

    def __init__(self, color: list[float] | None = None):
        self.color = color or [0.3, 0.5, 0.2]

    def generate(self, index: int) -> list[dict]:
        length = 15.0 + 10.0 * ((index * PHI) % 1.0)
        curl = 0.5 + 0.5 * ((index * PHI * 2) % 1.0)
        return _build_tendril(length, curl, self.color)


# --- Shape construction functions ---


def _build_daisy(n_petals: int, size_factor: float, color: list[float]) -> list[dict]:
    """Build petal ellipses + pistil for one daisy flower."""
    rx = 8.0 * size_factor
    ry = 5.0 * size_factor
    dist = 6.0 * size_factor
    items: list[dict] = []

    for i in range(n_petals):
        angle = i * (2 * math.pi / n_petals)
        pcx = dist * math.cos(angle)
        pcy = dist * math.sin(angle)
        items.append(
            {
                "ty": "el",
                "nm": f"petal-{i}",
                "p": static_val([pcx, pcy]),
                "s": static_val([rx * 2, ry * 2]),
            }
        )

    items.append(_fill(color + [1]))

    # Pistil
    pistil_r = 3.0 * size_factor
    items.append(
        {
            "ty": "el",
            "nm": "pistil",
            "p": static_val([0, 0]),
            "s": static_val([pistil_r * 2, pistil_r * 2]),
        }
    )
    items.append(_fill([color[0] * 0.6, color[1] * 0.6, color[2] * 0.3, 1]))

    items.append(_group_transform())
    return items


def _build_leaf(size: float, angle_deg: float, color: list[float]) -> list[dict]:
    """Build a teardrop leaf at given angle."""
    angle = math.radians(angle_deg)
    tip_x = size * math.cos(angle)
    tip_y = size * math.sin(angle)
    # Simple ellipse rotated to approximate a leaf
    items: list[dict] = [
        {
            "ty": "el",
            "nm": "leaf",
            "p": static_val([tip_x / 2, tip_y / 2]),
            "s": static_val([size, size * 0.4]),
        },
        _fill(color + [1]),
        _group_transform(),
    ]
    return items


def _build_tendril(length: float, curl: float, color: list[float]) -> list[dict]:
    """Build a curling tendril as a stroked bezier."""
    # Simple S-curve approximation
    cx = length * 0.3 * curl
    cy = length * 0.5
    items: list[dict] = [
        {
            "ty": "sh",
            "nm": "tendril",
            "ks": static_val(
                {
                    "c": False,
                    "v": [[0, 0], [cx, cy], [0, length]],
                    "i": [[0, 0], [-cx * 0.5, 0], [0, 0]],
                    "o": [[0, 0], [cx * 0.5, 0], [0, 0]],
                }
            ),
        },
        {
            "ty": "st",
            "nm": "stroke",
            "c": static_val(color + [1]),
            "w": static_val(2.0),
            "o": static_val(100),
            "lc": 2,
            "lj": 2,
        },
        _group_transform(),
    ]
    return items


def _fill(color: list[float]) -> dict:
    return {"ty": "fl", "nm": "fill", "c": static_val(color), "r": 1, "o": static_val(100)}


def _group_transform() -> dict:
    return {
        "ty": "tr",
        "p": static_val([0, 0]),
        "a": static_val([0, 0]),
        "s": static_val([100, 100]),
        "r": static_val(0),
        "o": static_val(100),
    }
