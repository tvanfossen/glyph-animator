"""Keyframe factory functions for Lottie animation properties.

Each factory produces a keyframe dict suitable for inclusion in an
animated value's keyframe array. The final keyframe in a sequence
has only `t` and `s` (no easing, no end value).

PROPERTY TYPES AND THEIR KEYFRAME FORMATS:

Position (2D spatial):
    Requires `to`/`ti` spatial tangents for curved motion paths.
    Easing handles are 2D: {x: [x1, x2], y: [y1, y2]}.

Shape (path morph):
    Uses `s` (start path) and `e` (end path) — both wrapped in arrays.
    Easing handles are 1D: {x: [x], y: [y]}.

Opacity / Rotation (1D scalar):
    Simple `s` (start value array).
    Easing handles are 1D: {x: [x], y: [y]}.
    NO `to`/`ti` — these are NOT spatial properties.

Scale (multi-value but not spatial):
    Uses `s` as [sx, sy, sz].
    Easing handles are 2D: {x: [x1, x2], y: [y1, y2]}.
    NO `to`/`ti`.
"""

from __future__ import annotations

from glyph_animator.lottie.easing import EASE_IN_OUT, EasingCurve


def position_keyframe(
    frame: int,
    x: float,
    y: float,
    easing: EasingCurve = EASE_IN_OUT,
    to: tuple[float, float, float] | None = None,
    ti: tuple[float, float, float] | None = None,
) -> dict:
    """Keyframe for position property (2D spatial, requires to/ti)."""
    out_h, in_h = easing.handles_2d()
    kf: dict = {
        "t": frame,
        "s": [x, y, 0],
        "to": list(to) if to else [0, 0, 0],
        "ti": list(ti) if ti else [0, 0, 0],
        "o": out_h,
        "i": in_h,
    }
    return kf


def position_keyframe_final(frame: int, x: float, y: float) -> dict:
    """Final position keyframe (no easing, no end value)."""
    return {"t": frame, "s": [x, y, 0]}


def shape_keyframe(
    frame: int,
    start_path: dict,
    end_path: dict | None = None,
    easing: EasingCurve = EASE_IN_OUT,
) -> dict:
    """Keyframe for animated shape path (1D easing, s/e are path arrays)."""
    if end_path is None:
        return {"t": frame, "s": [start_path]}

    out_h, in_h = easing.handles_1d()
    return {
        "t": frame,
        "s": [start_path],
        "e": [end_path],
        "o": out_h,
        "i": in_h,
    }


def opacity_keyframe(
    frame: int,
    value: float,
    easing: EasingCurve = EASE_IN_OUT,
    is_final: bool = False,
) -> dict:
    """Keyframe for opacity (0-100, 1D scalar)."""
    if is_final:
        return {"t": frame, "s": [value]}
    out_h, in_h = easing.handles_1d()
    return {"t": frame, "s": [value], "o": out_h, "i": in_h}


def scale_keyframe(
    frame: int,
    sx: float,
    sy: float,
    easing: EasingCurve = EASE_IN_OUT,
    is_final: bool = False,
) -> dict:
    """Keyframe for scale (percentage, 2D easing but NO to/ti)."""
    if is_final:
        return {"t": frame, "s": [sx, sy, 100]}
    out_h, in_h = easing.handles_2d()
    return {"t": frame, "s": [sx, sy, 100], "o": out_h, "i": in_h}


def rotation_keyframe(
    frame: int,
    degrees: float,
    easing: EasingCurve = EASE_IN_OUT,
    is_final: bool = False,
) -> dict:
    """Keyframe for rotation (degrees, 1D scalar, NO to/ti)."""
    if is_final:
        return {"t": frame, "s": [degrees]}
    out_h, in_h = easing.handles_1d()
    return {"t": frame, "s": [degrees], "o": out_h, "i": in_h}
