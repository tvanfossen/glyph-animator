"""Hardware constraint validation for generated Lottie files."""

from __future__ import annotations

import json

from glyph_animator.models.config import HardwareConstraints


class HardwareValidator:
    """Validate a Lottie animation against hardware constraints.

    Raises ValueError with a descriptive message when any limit is exceeded.
    Consumer-side constraints — the library itself has no hard limits.
    """

    def __init__(self, constraints: HardwareConstraints):
        self._constraints = constraints

    def validate(self, lottie: dict) -> None:
        """Validate a Lottie JSON dict against all constraints."""
        self._check_layers(lottie)
        self._check_shapes(lottie)
        self._check_keyframes(lottie)
        self._check_file_size(lottie)

    def _check_layers(self, lottie: dict) -> None:
        count = len(lottie.get("layers", []))
        limit = self._constraints.max_layers
        if count > limit:
            msg = f"Layer count {count} exceeds limit {limit}"
            raise ValueError(msg)

    def _check_shapes(self, lottie: dict) -> None:
        limit = self._constraints.max_shapes_per_layer
        for layer in lottie.get("layers", []):
            count = _count_shapes(layer)
            if count > limit:
                msg = f"Layer '{layer.get('nm', '?')}' has {count} shapes (limit {limit})"
                raise ValueError(msg)

    def _check_keyframes(self, lottie: dict) -> None:
        limit = self._constraints.max_keyframes
        total = _count_keyframes(lottie)
        if total > limit:
            msg = f"Total keyframes {total} exceeds limit {limit}"
            raise ValueError(msg)

    def _check_file_size(self, lottie: dict) -> None:
        size_kb = len(json.dumps(lottie)) / 1024
        limit = self._constraints.max_file_size_kb
        if size_kb > limit:
            msg = f"File size {size_kb:.0f}KB exceeds limit {limit}KB"
            raise ValueError(msg)


def _count_shapes(layer: dict) -> int:
    """Count shape items in a layer (recursive through groups)."""
    count = 0
    for shape in layer.get("shapes", []):
        if shape.get("ty") == "gr":
            count += sum(1 for it in shape.get("it", []) if it.get("ty") not in ("tr",))
        else:
            count += 1
    return count


def _count_keyframes(obj) -> int:
    """Recursively count all keyframes in a Lottie structure."""
    if isinstance(obj, dict):
        total = 0
        if obj.get("a") == 1 and isinstance(obj.get("k"), list):
            total += len(obj["k"])
        for v in obj.values():
            total += _count_keyframes(v)
        return total
    if isinstance(obj, list):
        return sum(_count_keyframes(item) for item in obj)
    return 0
