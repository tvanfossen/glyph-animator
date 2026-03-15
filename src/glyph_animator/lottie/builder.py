"""Lottie JSON file construction.

All Lottie format knowledge is centralized here. The builder produces
valid bodymovin v5.7.0 JSON consumable by lottie-web, rlottie, ThorVG.

Layer ordering: index 0 = FRONT (topmost visual), last = BACK.
"""

from __future__ import annotations

import json
from pathlib import Path

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class LottieBuilder:
    """Construct a Lottie animation file incrementally."""

    def __init__(self, name: str, width: int, height: int, fps: int = 30, frames: int = 60):
        self._name = name
        self._width = width
        self._height = height
        self._fps = fps
        self._frames = frames
        self._layers: list[dict] = []

    @property
    def frames(self) -> int:
        return self._frames

    @frames.setter
    def frames(self, value: int) -> None:
        self._frames = value

    def add_shape_layer(
        self,
        name: str,
        shapes: list[dict],
        transform: dict | None = None,
        ip: int = 0,
        op: int | None = None,
    ) -> None:
        """Add a shape layer (ty=4). Layers are ordered front-to-back."""
        self._layers.append(
            _shape_layer(name, shapes, transform or _default_transform(), ip, op or self._frames)
        )

    def add_background(self, color: list[float] | None = None) -> None:
        """Add a solid-color background rectangle as the backmost layer."""
        col = color or [0.08, 0.08, 0.14, 1]
        shapes = [
            _rect(self._width / 2, self._height / 2, self._width, self._height),
            _fill(col),
        ]
        self.add_shape_layer("bg", shapes)

    def build(self) -> dict:
        """Return the complete Lottie JSON dict."""
        return {
            "v": "5.7.0",
            "nm": self._name,
            "ddd": 0,
            "fr": self._fps,
            "ip": 0,
            "op": self._frames,
            "w": self._width,
            "h": self._height,
            "layers": self._layers,
        }

    def save(self, path: str | Path) -> None:
        """Write Lottie JSON to file."""
        with open(path, "w") as f:
            json.dump(self.build(), f)


# --- Lottie structure helpers ---


def static_val(v) -> dict:
    """Non-animated property value."""
    return {"a": 0, "k": v}


def animated_val(keyframes: list[dict]) -> dict:
    """Animated property with keyframe array."""
    return {"a": 1, "k": keyframes}


def _default_transform() -> dict:
    return {
        "p": static_val([0, 0, 0]),
        "a": static_val([0, 0, 0]),
        "s": static_val([100, 100, 100]),
        "r": static_val(0),
        "o": static_val(100),
    }


def make_transform(pos=None, anchor=None, scale=None, rotation=None, opacity=None) -> dict:
    """Build a layer transform with optional animated properties."""
    return {
        "p": pos or static_val([0, 0, 0]),
        "a": anchor or static_val([0, 0, 0]),
        "s": scale or static_val([100, 100, 100]),
        "r": rotation or static_val(0),
        "o": opacity or static_val(100),
    }


def _shape_layer(name, shapes, transform, ip, op):
    return {
        "ty": 4,
        "nm": name,
        "sr": 1,
        "ks": transform,
        "ao": 0,
        "shapes": shapes,
        "ip": ip,
        "op": op,
        "st": 0,
    }


def _rect(cx, cy, w, h):
    return {
        "ty": "rc",
        "nm": "rect",
        "p": static_val([cx, cy]),
        "s": static_val([w, h]),
        "r": static_val(0),
    }


def _fill(color, rule=1):
    """Fill shape. rule: 1=non-zero winding, 2=even-odd."""
    return {
        "ty": "fl",
        "nm": "fill",
        "c": static_val(color),
        "r": rule,
        "o": static_val(100),
    }


def _stroke(color, width=2.0):
    return {
        "ty": "st",
        "nm": "stroke",
        "c": static_val(color),
        "w": static_val(width),
        "o": static_val(100),
        "lc": 2,
        "lj": 2,
    }


def shape_group(name: str, items: list[dict]) -> dict:
    """Wrap shapes in a group with default transform."""
    items_with_tr = list(items)
    items_with_tr.append(
        {
            "ty": "tr",
            "p": static_val([0, 0]),
            "a": static_val([0, 0]),
            "s": static_val([100, 100]),
            "r": static_val(0),
            "o": static_val(100),
        }
    )
    return {"ty": "gr", "nm": name, "it": items_with_tr}


def animated_shape(name: str, keyframes: list[dict]) -> dict:
    """Animated shape path item."""
    return {"ty": "sh", "nm": name, "ks": animated_val(keyframes)}


def static_shape(name: str, path: dict) -> dict:
    """Static (non-animated) shape path item."""
    return {"ty": "sh", "nm": name, "ks": static_val(path)}
