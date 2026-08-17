# SPDX-License-Identifier: Apache-2.0
"""The cut outlines under test, and the sweep of proportions they run through."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator

from pyboxbuilder.compartments.finger_hole import _fit_radii, scoop_outline


@dataclass(frozen=True)
class Cut:
    """One cut's outline at one set of proportions."""

    kind: str
    half_width: float
    depth: float
    flare: float
    points: tuple[tuple[float, float], ...]

    def right_half(self) -> list[tuple[float, float]]:
        """The outline's right side, bottom to rim, without the rim overshoot.

        The overshoot lives above the wall and exists only so the ring has no
        cusp to offset (see `RIM_OVERSHOOT_MM`); it is not part of the shape a
        finger meets, and including it would make every "never doubles back"
        assertion trivially fail at the top.
        """
        return sorted(
            (p for p in self.points if p[0] >= -1e-9 and p[1] <= self.depth + 1e-9),
            key=lambda point: point[1],
        )


def _grip(half_width: float, depth: float, flare: float) -> tuple:
    roll, rise, base = _fit_radii(half_width, depth, flare, None, keep_flat_bottom=False)
    return scoop_outline(half_width, depth, roll, base, rise)


def _compartment_scoop(half_width: float, depth: float, flare: float) -> tuple:
    roll, rise, base = _fit_radii(half_width, depth, flare, None, keep_flat_bottom=True)
    return scoop_outline(half_width, depth, roll, base, rise)


#: Every outline an invariant applies to. A new cut kind is one line here.
CUT_KINDS: dict[str, Callable[[float, float, float], tuple]] = {
    "grip": _grip,
    "compartment_scoop": _compartment_scoop,
}

#: The proportions to sweep. Deliberately wide and deliberately including the
#: awkward ones — a cut shallower than its roll, one barely wider than its
#: fillet, one many times deeper than wide — because that is where each of the
#: three defects lived.
HALF_WIDTHS = (3.0, 5.0, 8.0, 12.0, 20.0, 30.0)
DEPTHS = (2.0, 4.0, 6.0, 9.0, 14.0, 25.0, 45.0)
FLARES = (0.5, 1.0, 3.0, 5.0, 8.0)


def sweep(kinds: tuple[str, ...] = tuple(CUT_KINDS)) -> Iterator[Cut]:
    """Every cut in the grid, as `Cut` records."""
    for kind in kinds:
        build = CUT_KINDS[kind]
        for half_width in HALF_WIDTHS:
            for depth in DEPTHS:
                for flare in FLARES:
                    yield Cut(kind, half_width, depth, flare,
                              tuple(build(half_width, depth, flare)))
