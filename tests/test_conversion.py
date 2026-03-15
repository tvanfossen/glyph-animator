"""Tests for quadratic→cubic and line→cubic conversion (must be exact)."""

import math

from glyph_animator.algorithms.conversion import line_to_cubic, quad_to_cubic
from glyph_animator.algorithms.curves import eval_cubic


def eval_quadratic(p0, p1, p2, t):
    """Evaluate quadratic bezier at t."""
    mt = 1 - t
    x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
    y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
    return (x, y)


class TestQuadToCubic:
    def test_endpoints_preserved(self):
        """Converted cubic must start at P₀ and end at P₂."""
        p0, p1, p2 = (10.0, 20.0), (50.0, 80.0), (90.0, 20.0)
        c0, c1, c2, c3 = quad_to_cubic(p0, p1, p2)
        assert c0 == p0
        assert c3 == p2

    def test_algebraic_identity(self):
        """Max deviation between quad and converted cubic must be < 10⁻¹⁰."""
        p0, p1, p2 = (0.0, 0.0), (250.0, 500.0), (500.0, 0.0)
        c0, c1, c2, c3 = quad_to_cubic(p0, p1, p2)

        max_dev = 0.0
        for i in range(101):
            t = i / 100.0
            qx, qy = eval_quadratic(p0, p1, p2, t)
            cx, cy = eval_cubic(c0, c1, c2, c3, t)
            dev = math.sqrt((qx - cx) ** 2 + (qy - cy) ** 2)
            max_dev = max(max_dev, dev)

        assert max_dev < 1e-10, f"Max deviation {max_dev} exceeds 10⁻¹⁰"

    def test_multiple_segments(self):
        """Test several different quadratic shapes."""
        cases = [
            ((0, 0), (0, 100), (100, 100)),  # L-shape
            ((0, 0), (50, 0), (100, 0)),  # degenerate (line)
            ((100, 200), (300, 400), (500, 200)),  # arch
        ]
        for p0, p1, p2 in cases:
            p0f = (float(p0[0]), float(p0[1]))
            p1f = (float(p1[0]), float(p1[1]))
            p2f = (float(p2[0]), float(p2[1]))
            cubic = quad_to_cubic(p0f, p1f, p2f)

            for j in range(21):
                t = j / 20.0
                qpt = eval_quadratic(p0f, p1f, p2f, t)
                cpt = eval_cubic(*cubic, t)
                assert abs(qpt[0] - cpt[0]) < 1e-10
                assert abs(qpt[1] - cpt[1]) < 1e-10


class TestLineToCubic:
    def test_endpoints_preserved(self):
        p0, p1 = (10.0, 20.0), (90.0, 80.0)
        c0, c1, c2, c3 = line_to_cubic(p0, p1)
        assert c0 == p0
        assert c3 == p1

    def test_points_on_line(self):
        """All evaluated points must lie exactly on the line."""
        p0, p1 = (0.0, 0.0), (300.0, 150.0)
        cubic = line_to_cubic(p0, p1)

        for i in range(101):
            t = i / 100.0
            cx, cy = eval_cubic(*cubic, t)
            # Expected: linear interpolation
            ex = p0[0] + t * (p1[0] - p0[0])
            ey = p0[1] + t * (p1[1] - p0[1])
            assert abs(cx - ex) < 1e-10
            assert abs(cy - ey) < 1e-10
