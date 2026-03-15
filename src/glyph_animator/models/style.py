"""Style-related data models: colors, palettes, vine presets."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ColorRGBA(BaseModel):
    """RGBA color with float components in [0, 1]."""

    r: float = Field(ge=0.0, le=1.0)
    g: float = Field(ge=0.0, le=1.0)
    b: float = Field(ge=0.0, le=1.0)
    a: float = Field(default=1.0, ge=0.0, le=1.0)

    def as_lottie_rgb(self) -> list[float]:
        """Lottie uses [r, g, b] with 0-1 range."""
        return [self.r, self.g, self.b]

    def as_lottie_rgba(self) -> list[float]:
        return [self.r, self.g, self.b, self.a]


class BloomPalette(BaseModel):
    """Color palette for floral/bloom style animations."""

    petal_colors: list[ColorRGBA] = Field(min_length=1)
    pistil_color: ColorRGBA = Field(default_factory=lambda: ColorRGBA(r=0.9, g=0.8, b=0.2))
    leaf_color: ColorRGBA = Field(default_factory=lambda: ColorRGBA(r=0.2, g=0.6, b=0.2))
    stem_color: ColorRGBA = Field(default_factory=lambda: ColorRGBA(r=0.3, g=0.5, b=0.2))


class VineStylePreset(BaseModel):
    """Tunable parameters for vine-based animation styles."""

    attraction_bias: float = Field(default=0.92, ge=0.0, le=1.0)
    prune_distance: float = Field(default=18.0, ge=0.0)
    flourish_distance: float = Field(default=10.0, ge=0.0)
    flower_distance: float = Field(default=8.0, ge=0.0)
    max_depth: int = Field(default=8, ge=1)
    min_branch_length: float = Field(default=3.0, ge=0.0)
    palette: BloomPalette | None = None
