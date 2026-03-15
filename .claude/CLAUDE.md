# Glyph Animator — Project Instructions

Font-to-Lottie animation library. Extracts glyph outlines from TTF/OTF fonts, applies mathematically-grounded natural animation patterns, outputs Lottie JSON.

## Architecture

### Three-layer pipeline
```
Pipeline (font → contours) → Renderer (contours → RenderedDigit) → Style (RenderedDigit → Lottie layers)
```

### Three animation types (distinct)
- **Creation**: glyph appears from nothing
- **Destruction**: glyph disappears (NOT reversed creation)
- **Transition**: glyph A morphs into glyph B

### Configuration hierarchy
```
docs/constants.md → docs/proofs/*.md → docs/styles/*.md → configs/*.yaml
```
Each layer can reference prior layers via Jinja2 `{{constants.*}}`, `{{proofs.*}}`, etc.

## Key Conventions

- **Proof docs are dual-purpose**: markdown body = mathematical proof, YAML frontmatter = algorithm config
- **Style docs are dual-purpose**: markdown body = design rationale, YAML frontmatter = style config
- **Algorithm ABC**: every algorithm has `proof_reference`, `complexity`, `error_bound`, `execute()`
- **Strong base classes**: 80%+ logic in base, concrete classes are thin
- **Hardware constraints are consumer config**, not baked into the library

## Build / Test

```bash
.venv/bin/python -m pytest tests/ -v
.venv/bin/pre-commit run --all-files
```

## Prototype Source
Reference code (read-only): `~/Projects/greenwood-clock/tools/lottie_gen/glyph_animator/`

## Module Size Targets
- Cognitive complexity ≤ 15
- Max 3 returns per function
- Modules < 200 lines (guideline, not hard limit)

## Dependencies
- fonttools: TTF/OTF font parsing
- pydantic: data models and validation
- pyyaml: YAML frontmatter parsing
- jinja2: template resolution in config chain
- pillow (dev): PNG output for visual verification
- pytest (dev): test suite
- ruff (dev): linting and formatting
