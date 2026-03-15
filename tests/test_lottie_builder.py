"""Tests for Lottie builder and keyframe factories."""

import json

from glyph_animator.lottie.builder import (
    LottieBuilder,
    _fill,
    static_shape,
)
from glyph_animator.lottie.keyframes import (
    opacity_keyframe,
    position_keyframe,
    position_keyframe_final,
    rotation_keyframe,
    scale_keyframe,
    shape_keyframe,
)
from glyph_animator.lottie.paths import contour_to_lottie_path

SQUARE = [
    ((0.0, 0.0), (33.0, 0.0), (67.0, 0.0), (100.0, 0.0)),
    ((100.0, 0.0), (100.0, 33.0), (100.0, 67.0), (100.0, 100.0)),
    ((100.0, 100.0), (67.0, 100.0), (33.0, 100.0), (0.0, 100.0)),
    ((0.0, 100.0), (0.0, 67.0), (0.0, 33.0), (0.0, 0.0)),
]


class TestLottieBuilder:
    def test_basic_structure(self):
        b = LottieBuilder("test", 200, 200, fps=30, frames=60)
        lottie = b.build()
        assert lottie["v"] == "5.7.0"
        assert lottie["w"] == 200
        assert lottie["fr"] == 30
        assert lottie["op"] == 60

    def test_add_shape_layer(self):
        b = LottieBuilder("test", 200, 200)
        path = contour_to_lottie_path(SQUARE)
        shapes = [static_shape("sq", path), _fill([1, 1, 1, 1])]
        b.add_shape_layer("layer1", shapes)
        lottie = b.build()
        assert len(lottie["layers"]) == 1
        assert lottie["layers"][0]["nm"] == "layer1"

    def test_background_is_last(self):
        b = LottieBuilder("test", 200, 200)
        b.add_shape_layer("fg", [])
        b.add_background()
        lottie = b.build()
        assert lottie["layers"][-1]["nm"] == "bg"

    def test_valid_json(self):
        """Builder output must be JSON-serializable."""
        b = LottieBuilder("test", 200, 200)
        b.add_background()
        json_str = json.dumps(b.build())
        assert len(json_str) > 0


class TestKeyframeFactories:
    def test_position_has_to_ti(self):
        kf = position_keyframe(0, 50.0, 50.0)
        assert "to" in kf
        assert "ti" in kf
        assert len(kf["s"]) == 3  # [x, y, z]

    def test_position_final_no_easing(self):
        kf = position_keyframe_final(60, 100.0, 100.0)
        assert "o" not in kf
        assert "i" not in kf

    def test_shape_keyframe_with_morph(self):
        path_a = contour_to_lottie_path(SQUARE)
        path_b = contour_to_lottie_path(SQUARE)  # same shape, fine for test
        kf = shape_keyframe(0, path_a, path_b)
        assert len(kf["s"]) == 1  # path wrapped in array
        assert len(kf["e"]) == 1
        # 1D easing handles
        assert len(kf["o"]["x"]) == 1

    def test_shape_keyframe_final(self):
        path = contour_to_lottie_path(SQUARE)
        kf = shape_keyframe(60, path)
        assert "e" not in kf

    def test_opacity_no_to_ti(self):
        kf = opacity_keyframe(0, 100)
        assert "to" not in kf
        assert "ti" not in kf

    def test_scale_no_to_ti(self):
        kf = scale_keyframe(0, 100, 100)
        assert "to" not in kf
        assert "ti" not in kf
        # 2D easing
        assert len(kf["o"]["x"]) == 2

    def test_rotation_1d_easing(self):
        kf = rotation_keyframe(0, 45.0)
        assert len(kf["o"]["x"]) == 1
