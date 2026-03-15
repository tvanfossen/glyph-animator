"""Tests for Lottie easing curves."""

from glyph_animator.lottie.easing import (
    EASE_IN_OUT,
    ELASTIC,
    LINEAR,
    ORGANIC,
    Custom,
    EaseInOut,
)


class TestEasingHandleFormats:
    def test_1d_handles_single_element_arrays(self):
        """1D handles must be single-element arrays [x], [y]."""
        for easing in [LINEAR, EASE_IN_OUT, ORGANIC, ELASTIC]:
            out_h, in_h = easing.handles_1d()
            assert len(out_h["x"]) == 1
            assert len(out_h["y"]) == 1
            assert len(in_h["x"]) == 1
            assert len(in_h["y"]) == 1

    def test_2d_handles_two_element_arrays(self):
        """2D handles must be two-element arrays [x1, x2], [y1, y2]."""
        for easing in [LINEAR, EASE_IN_OUT, ORGANIC, ELASTIC]:
            out_h, in_h = easing.handles_2d()
            assert len(out_h["x"]) == 2
            assert len(out_h["y"]) == 2
            assert len(in_h["x"]) == 2
            assert len(in_h["y"]) == 2

    def test_linear_values(self):
        """Linear: out=(0,0), in=(1,1)."""
        out_h, in_h = LINEAR.handles_1d()
        assert out_h["x"] == [0.0]
        assert in_h["x"] == [1.0]

    def test_ease_in_out_symmetric(self):
        """Default EaseInOut is symmetric: out.x + in.x = 1."""
        eio = EaseInOut(0.42)
        out_h, in_h = eio.handles_1d()
        assert abs(out_h["x"][0] + in_h["x"][0] - 1.0) < 1e-10

    def test_custom_passthrough(self):
        """Custom easing preserves provided values."""
        c = Custom(0.1, 0.2, 0.8, 0.9)
        out_h, in_h = c.handles_1d()
        assert out_h["x"] == [0.1]
        assert out_h["y"] == [0.2]
        assert in_h["x"] == [0.8]
        assert in_h["y"] == [0.9]

    def test_elastic_overshoots(self):
        """Elastic in-handle y > 1 (overshoot)."""
        _, in_h = ELASTIC.handles_1d()
        assert in_h["y"][0] > 1.0
