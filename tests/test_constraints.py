"""Tests for hardware constraint validation."""

import pytest

from glyph_animator.lottie.constraints import HardwareValidator
from glyph_animator.models.config import HardwareConstraints


def _minimal_lottie(n_layers=1, n_shapes=1):
    """Build a minimal Lottie dict for testing."""
    shapes = [{"ty": "sh", "nm": f"s{i}"} for i in range(n_shapes)]
    layers = [{"ty": 4, "nm": f"L{i}", "shapes": shapes} for i in range(n_layers)]
    return {"v": "5.7.0", "layers": layers, "w": 100, "h": 100, "fr": 30, "ip": 0, "op": 60}


class TestHardwareValidator:
    def test_valid_passes(self):
        """Within limits → no exception."""
        v = HardwareValidator(HardwareConstraints())
        v.validate(_minimal_lottie())

    def test_too_many_layers(self):
        v = HardwareValidator(HardwareConstraints(max_layers=2))
        with pytest.raises(ValueError, match="Layer count"):
            v.validate(_minimal_lottie(n_layers=5))

    def test_too_many_shapes(self):
        v = HardwareValidator(HardwareConstraints(max_shapes_per_layer=2))
        with pytest.raises(ValueError, match="shapes"):
            v.validate(_minimal_lottie(n_shapes=10))

    def test_file_size_exceeded(self):
        v = HardwareValidator(HardwareConstraints(max_file_size_kb=1))
        # Build a lottie that's >1KB
        big = _minimal_lottie(n_layers=50, n_shapes=20)
        with pytest.raises(ValueError, match="File size"):
            v.validate(big)

    def test_keyframe_limit(self):
        v = HardwareValidator(HardwareConstraints(max_keyframes=5))
        lottie = _minimal_lottie()
        # Inject many keyframes
        kfs = [{"t": i, "s": [0]} for i in range(20)]
        lottie["layers"][0]["ks"] = {"a": 1, "k": kfs}
        with pytest.raises(ValueError, match="keyframes"):
            v.validate(lottie)
