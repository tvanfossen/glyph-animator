"""Base class for animation generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from glyph_animator.lottie.builder import LottieBuilder


class GeneratorBase(ABC):
    """Base class for generators that produce Lottie output files."""

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate(self) -> list[Path]:
        """Generate output files. Returns list of created file paths."""

    def _save(self, builder: LottieBuilder, filename: str) -> Path:
        """Save a LottieBuilder to the output directory."""
        path = self.output_dir / filename
        builder.save(path)
        return path
