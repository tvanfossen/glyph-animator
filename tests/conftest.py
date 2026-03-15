"""Shared test fixtures for glyph-animator."""

from pathlib import Path

import pytest


@pytest.fixture
def font_path() -> Path:
    """Path to Nunito ExtraBold used in prototype development."""
    path = Path.home() / "Projects/greenwood-clock/components/fonts/fonts/Nunito-ExtraBold.ttf"
    if not path.exists():
        pytest.skip(f"Font not found: {path}")
    return path


@pytest.fixture
def docs_path() -> Path:
    """Path to docs directory."""
    return Path(__file__).parent.parent / "docs"
