# Specification Quality Checklist: Board Game Box Library

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-11
**Feature**: [spec.md](../spec.md)

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs) — **fails as of the 2026-08-15 review**: FR-047 named `pyboxbuilder/compartments/finger_hole.py` and the legacy `components.py`, and FR-002g/FR-002j name `FingerHoleWall`/`CornerCatch`. Some of this is deliberate (the requirement is "reuse the one builder, do not port a second"), but it is a module reference in a spec and it is recorded here rather than silently ticked.
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## 2026-08-15 review of the finger-cut requirements

A senior review of everything covering finger cuts (FR-006, the FR-043 family, FR-047, FR-042, FR-002f–FR-002u) found the two ticks above to be false, and the spec has been revised accordingly. What was wrong, and where it now lives:

- **Two pairs of requirements contradicted each other.** FR-043a's tangent roll against FR-043b1's alignment plane on a lidded box (resolved by FR-043b1a: the cut is built shorter so the roll finishes below it), and FR-043g's rolled base against FR-043b5's 0.2mm floor dip (resolved by FR-043g1: the face fillet tapers to zero at the base).
- **Three statements were simply wrong**: acceptance scenarios 2 and 3, and FR-047's height formula, which named an undefined `finger_hole_size` and differed from the built behaviour in three terms.
- **The vocabulary was unstable** — notch/scoop/cutout/hole/bore used interchangeably and, in FR-006, assigned oppositely to FR-043a — now fixed by FR-006a.
- **No datum was given for a cut's depth**, which is what produced T306; now FR-006b.
- **Missing rules**, now added: FR-006c (overlapping cuts), FR-039a (magnets off the hole walls), FR-047a/b/c (skip, opt-out, polygon path boxes), FR-002m1 (a footprint too small for corner cutouts).
- **Two pairs of duplicate ids** (SC-045, SC-053) and four in the FR-002 series (c, d, e, f, split between a hinge series and the sliding series) were renumbered, with every citation updated.

## Notes

- All items pass except as noted above. Clarifications from 2026-08-11 sessions integrated: auto-sizing (fill-to-fit rows, variable row widths, 10mm gap threshold, 15mm spacer minimums), spacer boxes as hollow trays, both-dimension expansion with row-length alignment, 3MF export (body/lid separate, spacers independent, Hausdorff caching, always both multi+single), lid decoration (framed/frameless modes, corner-to-corner diagonal text, through-hole patterns, three independent accent colors, 4mm min text threshold). Spec ready for `/speckit.plan`.
