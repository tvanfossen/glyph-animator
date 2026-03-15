---
id: P1-20260315-003
title: "Session 3: Styles + Generators + Docs + CLI"
priority: 1
status: BACKLOG
created: 2026-03-15
updated: 2026-03-15
session: 3
depends_on: P1-20260315-002
---

# Session 3: Styles + Generators

## Scope

- `algorithms/growth.py`, `algorithms/spatial.py`
- `algorithms/shapes.py` (all ShapeGenerator concrete classes)
- `algorithms/transitions.py` (all TransitionAlgorithm concrete classes)
- `styles/base.py` (StyleBase with creation/destruction/transition)
- `styles/loader.py`, `styles/registry.py`
- All concrete styles: morph, floral, vine_garden, vine_lsystem, vine_clipped, comic
- `generators/base.py`, all concrete generators (single_glyph, transition, clock, font_file)
- `scripts/generate.py` CLI
- `docs/styles/*.md` (all style config files with frontmatter)
- `docs/proofs/11-16` (new proofs: dahlia, spiral, verlet, damped oscillator, spring, ray cast)
- `docs/NATURAL_PATTERNS.md`
- Config YAML examples
- README.md
- Tests for all above

## STOP Points (user verification required)

1. **After shapes + transitions**: render sample flowers/leaves/tendrils to PNG — **user verifies**
2. **After StyleBase + morph style**: generate morph digit, load in viewer — **user verifies**
3. **After vine_clipped style**: generate clipped vine digit + transition — **user verifies**
4. **After comic style**: generate "POW!" action lettering — **user verifies**
5. **After generators + CLI**: `generate.py configs/clock_vine_clipped.yaml` produces complete output — **user verifies**

## Acceptance Criteria

- All 6 styles produce valid Lottie under default hardware constraints
- Style loader reads `docs/styles/*.md` frontmatter → instantiated Style
- CLI generates from YAML config
- Clock generator produces seekable file with all 10 transitions
- Font file generator produces complete seekable file with creation+destruction+transitions
- All new proofs documented with YAML frontmatter
- `pytest tests/` passes, `pre-commit` passes

## StyleBase Abstract Methods

```python
class StyleBase(ABC):
    @abstractmethod
    def _build_creation(self, rendered: RenderedDigit) -> list[dict]:
        """Glyph appears from nothing."""

    @abstractmethod
    def _build_destruction(self, rendered: RenderedDigit) -> list[dict]:
        """Glyph disappears. Distinct from reversed creation."""

    @abstractmethod
    def _build_transition(self, rendered_a: RenderedDigit,
                          rendered_b: RenderedDigit,
                          pairs: list[MatchedPair]) -> list[dict]:
        """Glyph A transforms into glyph B."""
```

## Style Inventory

| Style | Creation | Destruction | Transition | Source |
|---|---|---|---|---|
| morph | fade-in outline | fade-out outline | contour interpolation | gate5_morph.py |
| floral_scatter | Vogel spiral bloom | petal scatter | petals migrate | gate6_floral.py |
| vine_garden | vines grow along outline | vines wither | vines bridge A→B | vine_style.py |
| vine_lsystem | L-system branching growth | branches retract | L-system regrows to B | vine_lsystem.py |
| vine_clipped | clipped vine fill | vine drain | vine morph within clip | vine_clipped.py |
| comic_action | impact bounce entrance | shake exit | action wipe transition | new |

## Output Generators

| Generator | Input | Output |
|---|---|---|
| SingleGlyphGenerator | glyph + animation_type (creation/destruction) | single Lottie JSON |
| TransitionGenerator | glyph_a + glyph_b | single transition Lottie |
| ClockGenerator | digit set (0-9) | seekable 0→1→...→9→0 Lottie |
| FontFileGenerator | glyph set + all animation types | complete seekable font file |

## Prototype Source Mapping

| Prototype File | Library Target |
|---|---|
| gate6_floral.py | algorithms/growth.py |
| vine_lsystem.py | algorithms/growth.py (LSystemGrower) |
| vine_clipped.py | styles/vine_clipped.py + renderer/digit_renderer.py |
| vine_style.py | models/style.py (presets) |
| demo_clock.py | generators/clock.py |

## Proof Docs 11-16

| Doc | Algorithm | Source |
|---|---|---|
| 11_fibonacci_petal_phyllotaxis.md | Fibonacci petal placement | gate6_floral.py |
| 12_logarithmic_spiral.md | Spiral growth curves | vine_lsystem.py |
| 13_verlet_integration.md | Petal physics simulation | new |
| 14_damped_harmonic_oscillator.md | Bounce/shake dynamics | new |
| 15_critically_damped_spring.md | Smooth settle animation | new |
| 16_ray_casting.md | Point-in-contour testing | vine_clipped.py |
