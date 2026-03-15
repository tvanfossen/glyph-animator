"""Geometric data types for bezier curves, contours, and glyphs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Point(BaseModel):
    """2D point in font coordinate space."""

    x: float
    y: float

    def __add__(self, other: Point) -> Point:
        return Point(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, scalar: float) -> Point:
        return Point(x=self.x * scalar, y=self.y * scalar)

    def __rmul__(self, scalar: float) -> Point:
        return self.__mul__(scalar)

    def dot(self, other: Point) -> float:
        return self.x * other.x + self.y * other.y

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, t: tuple[float, float]) -> Point:
        return cls(x=t[0], y=t[1])


class BezierSegment(BaseModel):
    """Cubic bezier segment defined by four control points.

    B(t) = (1-t)³·p0 + 3(1-t)²t·p1 + 3(1-t)t²·p2 + t³·p3
    """

    p0: Point  # Start (on-curve)
    p1: Point  # Control 1
    p2: Point  # Control 2
    p3: Point  # End (on-curve)

    def as_tuples(self) -> tuple[tuple[float, float], ...]:
        return (self.p0.as_tuple(), self.p1.as_tuple(), self.p2.as_tuple(), self.p3.as_tuple())

    @classmethod
    def from_tuples(cls, t: tuple[tuple[float, float], ...]) -> BezierSegment:
        return cls(
            p0=Point.from_tuple(t[0]),
            p1=Point.from_tuple(t[1]),
            p2=Point.from_tuple(t[2]),
            p3=Point.from_tuple(t[3]),
        )


class BoundingBox(BaseModel):
    """Axis-aligned bounding box in font units."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def diagonal_sq(self) -> float:
        return self.width**2 + self.height**2


class Contour(BaseModel):
    """A closed contour made of cubic bezier segments."""

    segments: list[BezierSegment]

    @property
    def segment_count(self) -> int:
        return len(self.segments)

    def start_points(self) -> list[Point]:
        return [seg.p0 for seg in self.segments]

    def to_tuples(self) -> list[tuple[tuple[float, float], ...]]:
        """Convert to list of 4-point tuples for algorithm functions."""
        return [seg.as_tuples() for seg in self.segments]

    @classmethod
    def from_tuples(cls, segs: list) -> Contour:
        """Create from list of 4-point tuples."""
        return cls(segments=[BezierSegment.from_tuples(s) for s in segs])


class GlyphData(BaseModel):
    """Complete extracted + processed glyph data."""

    character: str = Field(min_length=1, max_length=1)
    glyph_name: str
    contours: list[Contour]
    bounds: BoundingBox
    units_per_em: int = Field(gt=0)


class MatchedPair(BaseModel):
    """A pair of contours matched between two glyphs, with alignment applied."""

    contour_a: Contour
    contour_b: Contour
    rotation_offset: int = Field(ge=0, description="Starting point rotation k applied to B")
    is_degenerate_a: bool = False
    is_degenerate_b: bool = False
