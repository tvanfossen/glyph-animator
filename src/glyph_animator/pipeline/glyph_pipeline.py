"""End-to-end glyph processing: font → extracted → resampled → matched contours."""

from __future__ import annotations

from pathlib import Path

from glyph_animator.algorithms.alignment import align_starting_points
from glyph_animator.algorithms.matching import match_contours
from glyph_animator.algorithms.resampling import resample_contour
from glyph_animator.constants import DEFAULT_SEGMENT_COUNT
from glyph_animator.font.extractor import FontExtractor
from glyph_animator.models.geometry import (
    Contour,
    GlyphData,
    MatchedPair,
)
from glyph_animator.pipeline.base import PipelineBase

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class GlyphPipeline(PipelineBase[str, GlyphData]):
    """Extract and process a single glyph from a font file.

    Pipeline: extract → convert (quad→cubic) → resample to N segments.
    """

    def __init__(self, font_path: str | Path, segment_count: int = DEFAULT_SEGMENT_COUNT):
        self._extractor = FontExtractor(font_path)
        self._segment_count = segment_count

    def execute(self, input_data: str) -> GlyphData:
        """Process a single character. Returns GlyphData with resampled contours."""
        char = input_data
        self._log_step("extract", f"char='{char}'")
        glyph = self._extractor.extract_glyph(char)

        self._log_step("resample", f"{len(glyph.contours)} contours → N={self._segment_count}")
        resampled_contours = self._resample_glyph(glyph)

        return GlyphData(
            character=glyph.character,
            glyph_name=glyph.glyph_name,
            contours=resampled_contours,
            bounds=glyph.bounds,
            units_per_em=glyph.units_per_em,
        )

    def process_glyph(self, char: str) -> GlyphData:
        """Convenience alias for execute()."""
        return self.execute(char)

    def process_pair(self, char_a: str, char_b: str) -> list[MatchedPair]:
        """Process two glyphs and return matched, aligned contour pairs."""
        glyph_a = self.execute(char_a)
        glyph_b = self.execute(char_b)

        self._log_step(
            "match", f"'{char_a}' ({len(glyph_a.contours)}) ↔ '{char_b}' ({len(glyph_b.contours)})"
        )

        contours_a = [c.to_tuples() for c in glyph_a.contours]
        contours_b = [c.to_tuples() for c in glyph_b.contours]

        pairs = match_contours(contours_a, contours_b, self._segment_count)

        result = []
        for ca, cb in pairs:
            k, _, _, cb_aligned = align_starting_points(ca, cb)
            is_degen_a = _is_degenerate(ca)
            is_degen_b = _is_degenerate(cb)
            result.append(
                MatchedPair(
                    contour_a=Contour.from_tuples(ca),
                    contour_b=Contour.from_tuples(cb_aligned),
                    rotation_offset=k,
                    is_degenerate_a=is_degen_a,
                    is_degenerate_b=is_degen_b,
                )
            )

        self._log_step("align", f"{len(result)} pairs aligned")
        return result

    def _resample_glyph(self, glyph: GlyphData) -> list[Contour]:
        """Resample all contours to uniform segment count."""
        result = []
        for contour in glyph.contours:
            seg_tuples = contour.to_tuples()
            resampled = resample_contour(seg_tuples, self._segment_count)
            result.append(Contour.from_tuples(resampled))
        return result


def _is_degenerate(contour: list[Seg]) -> bool:
    """Check if all points in a contour are at the same location."""
    if not contour:
        return True
    ref = contour[0][0]
    return all(
        abs(seg[i][0] - ref[0]) < 1e-6 and abs(seg[i][1] - ref[1]) < 1e-6
        for seg in contour
        for i in range(4)
    )
