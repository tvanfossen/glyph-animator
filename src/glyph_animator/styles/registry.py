"""Style registry: maps style names to their implementation classes."""

from __future__ import annotations

from glyph_animator.styles.base import StyleBase

_REGISTRY: dict[str, type[StyleBase]] = {}


def register_style(name: str, cls: type[StyleBase]) -> None:
    """Register a style class by name."""
    _REGISTRY[name] = cls


def get_style_class(name: str) -> type[StyleBase]:
    """Look up a style class by name."""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        msg = f"Unknown style '{name}'. Available: {available}"
        raise ValueError(msg)
    return _REGISTRY[name]


def list_styles() -> list[str]:
    """Return sorted list of registered style names."""
    return sorted(_REGISTRY.keys())
