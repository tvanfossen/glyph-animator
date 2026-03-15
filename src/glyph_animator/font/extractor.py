"""Extract glyph outlines from TTF/OTF fonts as cubic bezier contours."""

from __future__ import annotations

from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from glyph_animator.algorithms.conversion import line_to_cubic, quad_to_cubic
from glyph_animator.models.geometry import BezierSegment, BoundingBox, Contour, GlyphData, Point

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class FontExtractor:
    """Extract glyph outlines from a font file.

    Handles both TTF (quadratic beziers → converted to cubic) and
    OTF (cubic beziers → passed through directly).
    """

    def __init__(self, font_path: str | Path):
        self.font_path = Path(font_path)
        self._font = TTFont(str(self.font_path))
        self._glyph_set = self._font.getGlyphSet()
        self._cmap = self._font.getBestCmap()

    @property
    def units_per_em(self) -> int:
        return self._font["head"].unitsPerEm

    @property
    def family_name(self) -> str:
        return self._font["name"].getDebugName(1) or "Unknown"

    @property
    def is_ttf(self) -> bool:
        return "glyf" in self._font

    def extract_glyph(self, char: str) -> GlyphData:
        """Extract a single character as GlyphData with cubic bezier contours."""
        glyph_name = self._char_to_glyph_name(char)
        operations = self._record_operations(glyph_name)
        bounds = self._get_bounds(glyph_name)
        contours = self._operations_to_contours(operations)

        return GlyphData(
            character=char,
            glyph_name=glyph_name,
            contours=contours,
            bounds=bounds,
            units_per_em=self.units_per_em,
        )

    def extract_glyphs(self, chars: str) -> list[GlyphData]:
        """Extract multiple characters."""
        return [self.extract_glyph(c) for c in chars]

    def _char_to_glyph_name(self, char: str) -> str:
        code_point = ord(char)
        if code_point not in self._cmap:
            msg = f"Character '{char}' (U+{code_point:04X}) not in font"
            raise ValueError(msg)
        return self._cmap[code_point]

    def _record_operations(self, glyph_name: str) -> list:
        pen = RecordingPen()
        self._glyph_set[glyph_name].draw(pen)
        return pen.value

    def _get_bounds(self, glyph_name: str) -> BoundingBox:
        pen = BoundsPen(self._glyph_set)
        self._glyph_set[glyph_name].draw(pen)
        if pen.bounds is None:
            return BoundingBox(x_min=0, y_min=0, x_max=0, y_max=0)
        x_min, y_min, x_max, y_max = pen.bounds
        return BoundingBox(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max)

    def _operations_to_contours(self, operations: list) -> list[Contour]:
        """Convert font pen operations to list of Contour with cubic segments."""
        contours: list[Contour] = []
        current_segments: list[BezierSegment] = []
        pen = (0.0, 0.0)

        for op_type, args in operations:
            if op_type == "moveTo":
                if current_segments:
                    contours.append(Contour(segments=current_segments))
                current_segments = []
                pen = _to_pt(args[0])

            elif op_type == "lineTo":
                p1 = _to_pt(args[0])
                current_segments.append(_seg_from_tuple(line_to_cubic(pen, p1)))
                pen = p1

            elif op_type == "qCurveTo":
                pen = self._handle_qcurve(pen, args, current_segments)

            elif op_type == "curveTo":
                c1 = _to_pt(args[0])
                c2 = _to_pt(args[1])
                c3 = _to_pt(args[2])
                current_segments.append(_seg_from_tuple((pen, c1, c2, c3)))
                pen = c3

            elif op_type in ("closePath", "endPath"):
                if current_segments:
                    contours.append(Contour(segments=current_segments))
                current_segments = []

        return contours

    def _handle_qcurve(self, pen: Pt, args: tuple, segments: list[BezierSegment]) -> Pt:
        """Process a qCurveTo operation, decomposing implied midpoints."""
        points = [_to_pt(p) for p in args]

        if len(points) == 1:
            segments.append(_seg_from_tuple(line_to_cubic(pen, points[0])))
            return points[0]

        prev = pen
        for i in range(len(points) - 1):
            ctrl = points[i]
            if i < len(points) - 2:
                nxt = points[i + 1]
                end = ((ctrl[0] + nxt[0]) / 2, (ctrl[1] + nxt[1]) / 2)
            else:
                end = points[-1]
            segments.append(_seg_from_tuple(quad_to_cubic(prev, ctrl, end)))
            prev = end
        return points[-1]


def _to_pt(p) -> Pt:
    """Convert any point representation to (float, float)."""
    return (float(p[0]), float(p[1]))


def _seg_from_tuple(t: tuple[Pt, Pt, Pt, Pt]) -> BezierSegment:
    """Convert 4-tuple of (x,y) pairs to BezierSegment."""
    return BezierSegment(
        p0=Point(x=t[0][0], y=t[0][1]),
        p1=Point(x=t[1][0], y=t[1][1]),
        p2=Point(x=t[2][0], y=t[2][1]),
        p3=Point(x=t[3][0], y=t[3][1]),
    )
