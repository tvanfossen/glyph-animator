"""Easing curve definitions for Lottie keyframe interpolation.

Lottie easing uses cubic bezier handles in [0,1]×[0,1] space:
- `i` (in): handle at the keyframe destination {x: [...], y: [...]}
- `o` (out): handle at the keyframe source {x: [...], y: [...]}

CRITICAL FORMAT DIFFERENCE:
- 1D properties (opacity, rotation): handles are [x], [y] (single-element arrays)
- 2D properties (position, scale): handles are [x1, x2], [y1, y2] (per-component)
- Shape properties: handles are [x], [y] (same as 1D)
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class EasingCurve(ABC):
    """Base class for easing curve definitions."""

    @abstractmethod
    def handles_1d(self) -> tuple[dict, dict]:
        """Return (in_handle, out_handle) for 1D/shape properties."""

    @abstractmethod
    def handles_2d(self) -> tuple[dict, dict]:
        """Return (in_handle, out_handle) for 2D properties (position, scale)."""


class Linear(EasingCurve):
    """Linear interpolation — no easing."""

    def handles_1d(self) -> tuple[dict, dict]:
        return ({"x": [0.0], "y": [0.0]}, {"x": [1.0], "y": [1.0]})

    def handles_2d(self) -> tuple[dict, dict]:
        return (
            {"x": [0.0, 0.0], "y": [0.0, 0.0]},
            {"x": [1.0, 1.0], "y": [1.0, 1.0]},
        )


class EaseInOut(EasingCurve):
    """Standard ease-in-out with configurable strength."""

    def __init__(self, strength: float = 0.42):
        self.strength = strength

    def handles_1d(self) -> tuple[dict, dict]:
        s = self.strength
        return ({"x": [s], "y": [0.0]}, {"x": [1 - s], "y": [1.0]})

    def handles_2d(self) -> tuple[dict, dict]:
        s = self.strength
        return (
            {"x": [s, s], "y": [0.0, 0.0]},
            {"x": [1 - s, 1 - s], "y": [1.0, 1.0]},
        )


class Organic(EasingCurve):
    """Asymmetric ease — slow start, fast middle, gentle settle."""

    def handles_1d(self) -> tuple[dict, dict]:
        return ({"x": [0.25], "y": [0.1]}, {"x": [0.75], "y": [0.9]})

    def handles_2d(self) -> tuple[dict, dict]:
        return (
            {"x": [0.25, 0.25], "y": [0.1, 0.1]},
            {"x": [0.75, 0.75], "y": [0.9, 0.9]},
        )


class Elastic(EasingCurve):
    """Overshoot easing — settles with a bounce past the target."""

    def handles_1d(self) -> tuple[dict, dict]:
        return ({"x": [0.5], "y": [0.0]}, {"x": [0.3], "y": [1.4]})

    def handles_2d(self) -> tuple[dict, dict]:
        return (
            {"x": [0.5, 0.5], "y": [0.0, 0.0]},
            {"x": [0.3, 0.3], "y": [1.4, 1.4]},
        )


class Custom(EasingCurve):
    """Arbitrary cubic bezier handles."""

    def __init__(self, ox: float, oy: float, ix: float, iy: float):
        self._ox = ox
        self._oy = oy
        self._ix = ix
        self._iy = iy

    def handles_1d(self) -> tuple[dict, dict]:
        return ({"x": [self._ox], "y": [self._oy]}, {"x": [self._ix], "y": [self._iy]})

    def handles_2d(self) -> tuple[dict, dict]:
        return (
            {"x": [self._ox, self._ox], "y": [self._oy, self._oy]},
            {"x": [self._ix, self._ix], "y": [self._iy, self._iy]},
        )


# Convenient singletons
LINEAR = Linear()
EASE_IN_OUT = EaseInOut()
ORGANIC = Organic()
ELASTIC = Elastic()
