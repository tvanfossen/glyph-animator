"""Configuration models for fonts, hardware constraints, and animation parameters."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class AnimationType(str, Enum):
    """The three distinct animation types."""

    CREATION = "creation"
    DESTRUCTION = "destruction"
    TRANSITION = "transition"


class FontConfig(BaseModel):
    """Font extraction configuration."""

    font_path: Path
    glyphs: str = Field(default="0123456789", description="Characters to extract")
    units_per_em: int | None = Field(default=None, description="Override; None = read from font")


class HardwareConstraints(BaseModel):
    """Consumer-side hardware limits, NOT baked into algorithms."""

    max_layers: int = Field(default=100, ge=1)
    max_shapes_per_layer: int = Field(default=50, ge=1)
    max_keyframes: int = Field(default=300, ge=1)
    max_file_size_kb: int = Field(default=500, ge=1)
    target_fps: int = Field(default=30, ge=1, le=120)
    canvas_width: int = Field(default=1024, ge=1)
    canvas_height: int = Field(default=600, ge=1)


class AnimationConfig(BaseModel):
    """Parameters controlling animation generation."""

    animation_type: AnimationType
    style: str = Field(default="morph", description="Style name from docs/styles/")
    duration_frames: int = Field(default=60, ge=1)
    segment_count: int = Field(default=64, ge=8)
    hardware: HardwareConstraints = Field(default_factory=HardwareConstraints)
