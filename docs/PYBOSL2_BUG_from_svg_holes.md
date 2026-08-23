# pybosl2 bug: `Region.from_svg` loses even-odd holes when the SVG has a `viewBox`

## Environment

- **pybosl2** 0.7.10
- **shapely** 2.1.2
- **svgelements** 1.9.6
- Python 3.14.6

## Summary

`Region.from_svg` (and the underlying `pybosl2.svg.region_from_svg`) flattens a
shape's nested subpaths into a solid blob whenever the SVG declares a `viewBox`.
Inner cutouts — a donut's centre, a plate's windows, a radar icon's ring gaps —
come back as solid, because the viewport-clipping step unions the rings together
*before* the even-odd rule gets a chance to turn the nested ring into a hole.

The default `clip_to_viewbox=True` triggers the bug, and `Region.from_svg`
does not expose `clip_to_viewbox`, so every caller with a viewBox'd SVG hits it.

## Root cause

`pybosl2/svg.py` clips each shape's rings to the viewBox inside
`svg_element_groups` (lines ~483–486):

```python
raw_rings = _shape_rings(element, sign, fn, fs)
if mask is not None and raw_rings:
    raw_rings = _shapely_to_rings(_clip_rings(raw_rings, mask))
```

`_clip_rings` (lines ~318–323) turns the rings into shapely geometry, and
`_rings_to_shapely` (lines ~285–299) combines them with `unary_union`:

```python
def _rings_to_shapely(rings):
    polys = []
    for ring in rings:
        poly = _Polygon(ring)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if not poly.is_empty:
            polys.append(poly)
    if not polys:
        return None
    return _unary_union(polys)   # <-- union treats nested rings as filled, not holes
```

`shapely.ops.unary_union` takes each ring as a *filled* polygon and merges them,
so a nested ring (which the even-odd rule would read as a hole) is absorbed into
the outer shape. The even-odd pass (`Region.even_odd`, line ~243) runs later,
but the hole is already gone by then.

## Minimal reproduction

`donut.svg` — one `<path>` with an outer square and a nested inner square, and a
`viewBox`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M0,0 L100,0 L100,100 L0,100 Z M25,25 L75,25 L75,75 L25,75 Z"/>
</svg>
```

```python
from pybosl2 import Region

region = Region.from_svg("donut.svg")     # clip_to_viewbox defaults to True
shape = region.to_shapely()
holes = len(shape.interiors) if shape.geom_type == "Polygon" else sum(len(g.interiors) for g in shape.geoms)
print(holes, shape.area)
```

### Expected

```
1 7500.0     # a square plate with a square hole in the middle
```

### Actual

```
0 10000.0    # the hole is gone — a solid square
```

## Workaround

Skip the viewport clip, which sidesteps the buggy union. The clip is unnecessary
for drawings whose content already sits inside their `viewBox` (the common case
for CAD-style silhouettes):

```python
from pybosl2.svg import region_from_svg

region = region_from_svg("donut.svg", clip_to_viewbox=False)
```

Note: the `Region.from_svg` classmethod does **not** forward `clip_to_viewbox`,
so the module-level `region_from_svg` is the only way to opt out today. It would
be helpful to expose `clip_to_viewbox` on `Region.from_svg` too.

## Suggested fix

Make `_rings_to_shapely` honour even-odd nesting instead of unioning filled
polygons. Concretely:

1. Sort the rings by containment depth (an even-odd sweep: a ring inside an odd
   number of other rings is a shell, inside an even number is a hole).
2. Build each polygon as `shapely.geometry.Polygon(shell, holes)` for its holes.

That preserves holes through the `intersection(mask)` clip, and the existing
`Region.even_odd` pass then works as intended. Alternatively, apply the even-odd
rule to the raw rings *before* clipping.
