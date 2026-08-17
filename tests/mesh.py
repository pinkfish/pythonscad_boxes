# SPDX-License-Identifier: Apache-2.0
"""Measuring a solid's volume, for tests that assert about material.

The property most box tests care about is not a bounding box or a facet count
but "how much material is *here*" — a lid that intersects its body, a fillet
that removed a corner, a cut that opened the base. That number has to come from
the mesh, so it is taken by exporting to 3MF and summing the divergence over
its triangles.

One module rather than a copy per test file: there were seven, each with its own
escaping of the same two regexes, and they are equally needed inside the app
(`measure_python` scripts) and outside it (tests that build geometry directly).
Kept free of import-time side effects so it is safe to import in either.
"""

from __future__ import annotations

import os
import re
import tempfile
import zipfile

_VERTEX = re.compile(r'<vertex x="([-0-9.e+]+)" y="([-0-9.e+]+)" z="([-0-9.e+]+)"')
_TRIANGLE = re.compile(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"')


def volume(solid) -> float:
    """The solid's volume in mm³.

    Args:
        solid: A pybosl2 solid, or anything with a `.shape` the exporter takes.

    Returns:
        The enclosed volume. Signed by winding, so the absolute value is taken —
        a mesh the exporter hands back inside-out measures the same size.
    """
    from openscad import export  # only inside a PythonSCAD runtime

    node = solid.shape if hasattr(solid, "shape") else solid
    with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as handle:
        path = handle.name
    try:
        export(node, path)
        model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
    finally:
        os.unlink(path)

    verts = [(float(x), float(y), float(z)) for x, y, z in _VERTEX.findall(model)]
    total = 0.0
    for a, b, c in _TRIANGLE.findall(model):
        p, q, r = verts[int(a)], verts[int(b)], verts[int(c)]
        total += (
            p[0] * (q[1] * r[2] - r[1] * q[2])
            - p[1] * (q[0] * r[2] - r[0] * q[2])
            + p[2] * (q[0] * r[1] - r[0] * q[1])
        ) / 6.0
    return abs(total)
