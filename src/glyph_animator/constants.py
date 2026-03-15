"""Constants loaded from docs/constants.md YAML frontmatter.

This module provides convenient Python access to the constants defined in
docs/constants.md. The YAML frontmatter is the source of truth — this module
parses it once at import time and exposes the values as module-level attributes.
"""

from pathlib import Path

import yaml


def _load_constants() -> dict:
    """Parse YAML frontmatter from docs/constants.md."""
    docs_path = Path(__file__).resolve().parents[2] / "docs" / "constants.md"
    text = docs_path.read_text()
    if not text.startswith("---"):
        msg = f"No YAML frontmatter in {docs_path}"
        raise ValueError(msg)
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end])


_data = _load_constants()
_constants = _data["constants"]
_defaults = _data["defaults"]

# Mathematical constants
PHI: float = _constants["PHI"]["value"]
GOLDEN_ANGLE: float = _constants["GOLDEN_ANGLE"]["value"]
LENGTH_DECAY: float = _constants["LENGTH_DECAY"]["value"]

# Gauss quadrature
GAUSS_5PT_NODES: tuple[float, ...] = tuple(_constants["GAUSS_5PT"]["nodes"])
GAUSS_5PT_WEIGHTS: tuple[float, ...] = tuple(_constants["GAUSS_5PT"]["weights"])

# Algorithm defaults
DEFAULT_SEGMENT_COUNT: int = _defaults["segment_count"]["value"]
NEWTON_TOLERANCE: float = _defaults["newton_tolerance"]["value"]
NEWTON_MAX_ITERATIONS: int = _defaults["newton_max_iterations"]["value"]
SPEED_EPSILON: float = _defaults["speed_epsilon"]["value"]
ARC_LENGTH_EPSILON: float = _defaults["arc_length_epsilon"]["value"]
