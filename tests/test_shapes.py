"""Tests for shape generators: daisy, leaf, tendril."""

from glyph_animator.algorithms.shapes import DaisyGenerator, LeafGenerator, TendrilGenerator


class TestDaisyGenerator:
    def test_generates_items(self):
        gen = DaisyGenerator()
        items = gen.generate(0)
        assert len(items) > 0

    def test_last_item_is_transform(self):
        """Group transform must be last item."""
        gen = DaisyGenerator()
        items = gen.generate(0)
        assert items[-1]["ty"] == "tr"

    def test_deterministic_variation(self):
        """Different indices produce different petal counts."""
        gen = DaisyGenerator()
        items_0 = gen.generate(0)
        items_1 = gen.generate(1)
        # Petal counts differ for index 0 (5 petals) vs 1 (6 petals)
        petals_0 = sum(1 for i in items_0 if i.get("ty") == "el" and "petal" in i.get("nm", ""))
        petals_1 = sum(1 for i in items_1 if i.get("ty") == "el" and "petal" in i.get("nm", ""))
        assert petals_0 != petals_1


class TestLeafGenerator:
    def test_generates_items(self):
        gen = LeafGenerator()
        items = gen.generate(0)
        assert len(items) > 0
        assert items[-1]["ty"] == "tr"


class TestTendrilGenerator:
    def test_generates_stroke(self):
        gen = TendrilGenerator()
        items = gen.generate(0)
        has_stroke = any(i.get("ty") == "st" for i in items)
        assert has_stroke
        assert items[-1]["ty"] == "tr"
