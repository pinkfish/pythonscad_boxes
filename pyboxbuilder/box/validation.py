# SPDX-License-Identifier: Apache-2.0
"""Pre-CSG geometric invariant validation (FR-092 / SC-092).

Enforces physical and geometric invariants on a :class:`ResolvedBoxSpec` before
invoking PythonSCAD / Manifold boolean operations. Catching impossible envelopes,
degenerate thicknesses, and negative clearances here prevents downstream kernel
faults, unprintable solids, or obscure geometry solver errors.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyboxbuilder.box.spec import ResolvedBoxSpec

MIN_PRINTABLE_WALL_MM = 0.8
"""Minimum printable wall thickness on standard 0.4mm nozzle FDM printers."""

MIN_PRINTABLE_FLOOR_MM = 0.8
"""Minimum printable base floor thickness."""

MIN_CLEARANCE_MARGIN_MM = 1.0
"""Minimum internal clearance margin required beyond outer walls."""


class GeometryValidationError(ValueError):
    """Raised when a box configuration violates physical or geometric invariants (FR-092)."""

    def __init__(
        self,
        label: str,
        invariant: str,
        message: str,
        guidance: str | None = None,
    ) -> None:
        self.label = label
        self.invariant = invariant
        self.guidance = guidance
        full_message = f"Geometric validation failed for box '{label}' [{invariant}]: {message}"
        if guidance:
            full_message += f" Remediation: {guidance}"
        super().__init__(full_message)


class GeometryValidator:
    """Validates physical and geometric invariants on a ResolvedBoxSpec prior to CSG evaluation."""

    @classmethod
    def validate(cls, spec: ResolvedBoxSpec) -> None:
        """Validate all physical invariants on the resolved specification.

        Args:
            spec: The frozen :class:`ResolvedBoxSpec` to validate.

        Raises:
            GeometryValidationError: If any physical invariant is violated.
        """
        cls._validate_envelope_positivity(spec)
        cls._validate_material_thicknesses(spec)
        cls._validate_envelope_sanity(spec)
        cls._validate_clearances(spec)
        cls._validate_closure_bounds(spec)

    @classmethod
    def _validate_envelope_positivity(cls, spec: ResolvedBoxSpec) -> None:
        for dim, name in (
            (spec.width, "width"),
            (spec.length, "length"),
            (spec.height, "height"),
        ):
            if not isinstance(dim, (int, float)) or math.isnan(dim) or math.isinf(dim) or dim <= 0.0:
                raise GeometryValidationError(
                    label=spec.label,
                    invariant="positive_finite_envelope",
                    message=f"{name} must be a positive finite float, got {dim}.",
                    guidance=f"Set a positive {name} value in builder or container layout.",
                )

    @classmethod
    def _validate_material_thicknesses(cls, spec: ResolvedBoxSpec) -> None:
        if spec.wall_thickness < MIN_PRINTABLE_WALL_MM:
            raise GeometryValidationError(
                label=spec.label,
                invariant="min_wall_thickness",
                message=(
                    f"Wall thickness {spec.wall_thickness}mm is below the minimum printable "
                    f"threshold ({MIN_PRINTABLE_WALL_MM}mm)."
                ),
                guidance=f"Increase wall_thickness to at least {MIN_PRINTABLE_WALL_MM}mm (recommended >= 1.2mm).",
            )
        if spec.floor_thickness < MIN_PRINTABLE_FLOOR_MM:
            raise GeometryValidationError(
                label=spec.label,
                invariant="min_floor_thickness",
                message=(
                    f"Floor thickness {spec.floor_thickness}mm is below the minimum printable "
                    f"threshold ({MIN_PRINTABLE_FLOOR_MM}mm)."
                ),
                guidance=f"Increase floor_thickness to at least {MIN_PRINTABLE_FLOOR_MM}mm (recommended >= 1.6mm).",
            )
        if spec.lid_thickness < 0.0:
            raise GeometryValidationError(
                label=spec.label,
                invariant="non_negative_lid_thickness",
                message=f"Lid thickness cannot be negative, got {spec.lid_thickness}mm.",
                guidance="Set lid_thickness to 0.0 for lidless boxes or > 0.0 for lidded boxes.",
            )

    @classmethod
    def _validate_envelope_sanity(cls, spec: ResolvedBoxSpec) -> None:
        min_width = 2 * spec.wall_thickness + MIN_CLEARANCE_MARGIN_MM
        if spec.width < min_width:
            raise GeometryValidationError(
                label=spec.label,
                invariant="envelope_width_sanity",
                message=(
                    f"Box width ({spec.width:.2f}mm) is too small to accommodate two walls of "
                    f"{spec.wall_thickness:.2f}mm plus interior clearance (minimum {min_width:.2f}mm)."
                ),
                guidance=f"Increase width to >= {min_width:.2f}mm or reduce wall_thickness.",
            )

        min_length = 2 * spec.wall_thickness + MIN_CLEARANCE_MARGIN_MM
        if spec.length < min_length:
            raise GeometryValidationError(
                label=spec.label,
                invariant="envelope_length_sanity",
                message=(
                    f"Box length ({spec.length:.2f}mm) is too small to accommodate two walls of "
                    f"{spec.wall_thickness:.2f}mm plus interior clearance (minimum {min_length:.2f}mm)."
                ),
                guidance=f"Increase length to >= {min_length:.2f}mm or reduce wall_thickness.",
            )

        min_height = spec.floor_thickness + spec.lid_thickness
        if spec.height <= min_height:
            raise GeometryValidationError(
                label=spec.label,
                invariant="envelope_height_sanity",
                message=(
                    f"Box height ({spec.height:.2f}mm) must be strictly greater than the sum of floor "
                    f"({spec.floor_thickness:.2f}mm) and lid ({spec.lid_thickness:.2f}mm) thicknesses "
                    f"({min_height:.2f}mm)."
                ),
                guidance=f"Increase height to > {min_height:.2f}mm.",
            )

    @classmethod
    def _validate_clearances(cls, spec: ResolvedBoxSpec) -> None:
        for clearance, name in (
            (spec.size_spacing, "size_spacing"),
            (spec.sliding_slack, "sliding_slack"),
            (spec.cap_slack, "cap_slack"),
            (spec.slip_slack, "slip_slack"),
        ):
            if clearance < 0.0:
                raise GeometryValidationError(
                    label=spec.label,
                    invariant="non_negative_clearance",
                    message=f"Clearance parameter '{name}' cannot be negative, got {clearance}mm.",
                    guidance=f"Set '{name}' to a non-negative clearance (e.g. 0.1 to 0.3mm).",
                )

    @classmethod
    def _validate_closure_bounds(cls, spec: ResolvedBoxSpec) -> None:
        if (
            spec.catch_radius is not None
            and spec.catch_radius > 0.0
            and spec.catch_radius >= spec.wall_thickness
        ):
            raise GeometryValidationError(
                label=spec.label,
                invariant="catch_radius_fits_wall",
                message=(
                    f"Catch radius ({spec.catch_radius:.2f}mm) must be strictly less than "
                    f"wall thickness ({spec.wall_thickness:.2f}mm)."
                ),
                guidance=f"Reduce catch_radius to < {spec.wall_thickness:.2f}mm or increase wall_thickness.",
            )
        if spec.inset > 0.0:
            interior_depth = spec.height - spec.floor_thickness
            if spec.inset >= interior_depth:
                raise GeometryValidationError(
                    label=spec.label,
                    invariant="inset_depth_fits_box",
                    message=(
                        f"Inset depth ({spec.inset:.2f}mm) exceeds available box interior depth "
                        f"({interior_depth:.2f}mm)."
                    ),
                    guidance="Reduce inset or increase box height.",
                )
