# SPDX-License-Identifier: Apache-2.0
"""Interactive PythonSCAD GUI classes (``Box`` and ``CardBox``).

Implements PythonSCAD's Qt6 class-form protocol (``__new__``, ``get_calltip``,
and ``on_editor_trigger``) so users can create single boxes or card trays in one
line **and** edit their parameters with a native PyQt6 dialog directly from the
PythonSCAD editor (click the ``▷`` calltip marker or press ``Ctrl+Shift+Space``
inside the call).

In headless Python, CLI scripts, or Qt5 builds without PyQt6, ``Box(...)`` and
``CardBox(...)`` still work normally as concise one-line geometry builders.
"""

from __future__ import annotations

import ast
import builtins
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import BoxType, CatchType, PatternType, StackableMode
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
from pyboxbuilder.project.core import Project

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@dataclass(frozen=True)
class FormField:
    """Declarative metadata for one parameter in a PythonSCAD PyQt6 form."""

    name: str
    label: str
    kind: str  # "float", "int", "bool", "str", "choice"
    default: Any
    choices: tuple[str, ...] = ()
    minimum: float = 0.0
    maximum: float = 1000.0
    step: float = 1.0
    decimals: int = 1


def parse_call_args(
    arg_text: str,
    param_names: Sequence[str],
) -> tuple[dict[str, Any], list[str]]:
    """Parse a Python call argument string into known values and preserved extra args.

    Uses ``ast.parse`` and ``ast.literal_eval`` so no user code is executed.
    Positional arguments are mapped to ``param_names``; unknown keywords or
    non-literal expressions are preserved verbatim in ``extra`` so hand-edited
    code is never lost on round-trip.
    """
    text = arg_text.strip()
    if not text:
        return {}, []

    try:
        tree = ast.parse(f"_f({text})", mode="eval")
    except SyntaxError:
        return {}, [text]

    call = tree.body
    if not isinstance(call, ast.Call):
        return {}, [text]

    known_set = set(param_names)
    parsed: dict[str, Any] = {}
    extra: list[str] = []

    for idx, node in enumerate(call.args):
        if idx < len(param_names):
            try:
                parsed[param_names[idx]] = ast.literal_eval(node)
            except (ValueError, TypeError):
                extra.append(f"{param_names[idx]}={ast.unparse(node)}")
        else:
            extra.append(ast.unparse(node))

    for kw in call.keywords:
        if kw.arg is None:
            extra.append(f"**{ast.unparse(kw.value)}")
            continue
        if kw.arg in known_set:
            try:
                parsed[kw.arg] = ast.literal_eval(kw.value)
            except (ValueError, TypeError):
                extra.append(f"{kw.arg}={ast.unparse(kw.value)}")
        else:
            extra.append(f"{kw.arg}={ast.unparse(kw.value)}")

    return parsed, extra


def format_call_args(
    values: Mapping[str, Any],
    defaults: Mapping[str, Any],
    extra: Sequence[str] = (),
) -> str:
    """Format non-default parameter values and preserved extra args as a call string."""
    parts: list[str] = []
    for name, default in defaults.items():
        if name not in values:
            continue
        val = values[name]
        if isinstance(default, float) and isinstance(val, (int, float)) and abs(float(val) - default) < 1e-9:
            continue
        if val == default:
            continue
        if isinstance(val, float):
            val = round(val, 4)
        parts.append(f"{name}={val!r}")
    parts.extend(extra)
    return ", ".join(parts)


def _get_editor_hooks() -> tuple[Callable[[Any], str], Callable[[Any, str], None]] | None:
    """Locate PythonSCAD's ``editor_get_call_args`` and ``editor_replace_call_args``."""
    for mod_name in ("openscad", "pythonscad"):
        try:
            mod = __import__(mod_name)
        except ImportError:
            continue
        getter = getattr(mod, "editor_get_call_args", None)
        setter = getattr(mod, "editor_replace_call_args", None)
        if callable(getter) and callable(setter):
            return getter, setter
    getter = getattr(builtins, "editor_get_call_args", None)
    setter = getattr(builtins, "editor_replace_call_args", None)
    if callable(getter) and callable(setter):
        return getter, setter
    return None


def _show_form_dialog(
    title: str,
    fields: Sequence[FormField],
    current: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Display a PyQt6 parameter form and return edited values, or ``None`` if cancelled."""
    try:
        from PyQt6 import QtWidgets  # type: ignore[import-not-found]
    except ImportError:
        return None

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle(title)
    layout = QtWidgets.QFormLayout(dialog)
    widgets: dict[str, tuple[FormField, Any]] = {}

    for spec in fields:
        val = current.get(spec.name, spec.default)
        if spec.kind == "float":
            w = QtWidgets.QDoubleSpinBox()
            w.setRange(spec.minimum, spec.maximum)
            w.setSingleStep(spec.step)
            w.setDecimals(spec.decimals)
            w.setValue(float(val))
        elif spec.kind == "int":
            w = QtWidgets.QSpinBox()
            w.setRange(int(spec.minimum), int(spec.maximum))
            w.setSingleStep(int(spec.step))
            w.setValue(int(val))
        elif spec.kind == "bool":
            w = QtWidgets.QCheckBox()
            w.setChecked(bool(val))
        elif spec.kind == "choice":
            w = QtWidgets.QComboBox()
            w.addItems(list(spec.choices))
            idx = w.findText(str(val))
            if idx >= 0:
                w.setCurrentIndex(idx)
        else:
            w = QtWidgets.QLineEdit(str(val))
        layout.addRow(spec.label, w)
        widgets[spec.name] = (spec, w)

    buttons = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.StandardButton.Ok
        | QtWidgets.QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addRow(buttons)

    if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
        return None

    result: dict[str, Any] = {}
    for name, (spec, w) in widgets.items():
        if spec.kind == "float":
            result[name] = float(w.value())
        elif spec.kind == "int":
            result[name] = int(w.value())
        elif spec.kind == "bool":
            result[name] = bool(w.isChecked())
        elif spec.kind == "choice":
            result[name] = str(w.currentText())
        else:
            result[name] = str(w.text())
    return result


def _coerce_enum_str(value: Any, enum_cls: type[Any]) -> Any:
    """Coerce a non-empty string or enum value into ``enum_cls`` (or ``None`` if empty)."""
    if value is None or value == "":
        return None
    if isinstance(value, enum_cls):
        return value
    return enum_cls(str(value).lower())


def _combine_pieces(project: Project, *, show_lid: bool, lid_offset: float) -> Bosl2Solid:
    """Build the single box in ``project`` and return body (plus optional decorated lid beside it)."""
    build = project.build()
    body_solid: Bosl2Solid | None = None
    lid_solid: Bosl2Solid | None = None
    body_w = 0.0
    for piece in build.pieces:
        if piece.kind == "lid":
            decorated, _ = project._decorated_lid(piece, "single")
            lid_solid = decorated if decorated is not None else piece.solid
        elif body_solid is None:
            body_solid = piece.solid
            if piece.size is not None:
                body_w = float(piece.size[0])
    if body_solid is None:
        raise RuntimeError("Box build produced no body geometry")
    if show_lid and lid_solid is not None:
        return body_solid | lid_solid.translate([body_w + lid_offset, 0.0, 0.0])
    return body_solid


_BOX_TYPE_CHOICES: tuple[str, ...] = tuple(m.value for m in BoxType)
_PATTERN_CHOICES: tuple[str, ...] = tuple(m.value for m in PatternType)
_CATCH_CHOICES: tuple[str, ...] = ("", *(m.value for m in CatchType))
_STACKABLE_CHOICES: tuple[str, ...] = ("", *(m.value for m in StackableMode))
_SLEEVE_CHOICES: tuple[str, ...] = ("", "Gamegenic", "Sleeve Kings", "Mayday Games", "Standard", "Premium")

_BOX_FIELDS: tuple[FormField, ...] = (
    FormField("box_type", "Box Type", "choice", "sliding", _BOX_TYPE_CHOICES),
    FormField("width", "Width (mm)", "float", 80.0, minimum=10.0, maximum=500.0, step=5.0),
    FormField("length", "Length (mm)", "float", 60.0, minimum=10.0, maximum=500.0, step=5.0),
    FormField("height", "Height (mm)", "float", 30.0, minimum=8.0, maximum=300.0, step=2.0),
    FormField("wall_thickness", "Wall Thickness (mm)", "float", 2.0, minimum=0.8, maximum=10.0, step=0.2),
    FormField("floor_thickness", "Floor Thickness (mm)", "float", 1.6, minimum=0.6, maximum=10.0, step=0.2),
    FormField("lid_thickness", "Lid Thickness (mm)", "float", 2.0, minimum=0.8, maximum=10.0, step=0.2),
    FormField("pattern", "Lid Pattern", "choice", "hex", _PATTERN_CHOICES),
    FormField("label", "Lid Label", "str", ""),
    FormField("catch_type", "Catch Type", "choice", "", _CATCH_CHOICES),
    FormField("base_chamfer", "Base Chamfer (mm)", "float", 0.0, minimum=0.0, maximum=5.0, step=0.2),
    FormField("stackable", "Stackable Mode", "choice", "", _STACKABLE_CHOICES),
    FormField("show_lid", "Show Lid", "bool", True),
)

_CARD_BOX_FIELDS: tuple[FormField, ...] = (
    FormField("card_width", "Card Width (mm)", "float", 63.5, minimum=20.0, maximum=250.0, step=0.5),
    FormField("card_length", "Card Length (mm)", "float", 88.0, minimum=20.0, maximum=250.0, step=0.5),
    FormField("count", "Card Count", "int", 60, minimum=1, maximum=1000, step=5),
    FormField("thickness", "Card Thickness (mm)", "float", 0.35, minimum=0.1, maximum=5.0, step=0.05, decimals=2),
    FormField("sleeved", "Sleeved", "bool", False),
    FormField("sleeve", "Sleeve Brand / SKU", "choice", "", _SLEEVE_CHOICES),
    FormField("orientation", "Orientation", "choice", "flat", ("flat", "vertical", "angled")),
    FormField("tilt_angle", "Tilt Angle (deg)", "float", 0.0, minimum=0.0, maximum=45.0, step=5.0),
    FormField("divider_slots", "Divider Slots", "int", 0, minimum=0, maximum=20, step=1),
    FormField("box_type", "Box Type (auto if blank)", "choice", "", ("", *_BOX_TYPE_CHOICES)),
    FormField("pattern", "Lid Pattern", "choice", "hex", _PATTERN_CHOICES),
    FormField("label", "Lid Label", "str", ""),
    FormField("base_chamfer", "Base Chamfer (mm)", "float", 0.0, minimum=0.0, maximum=5.0, step=0.2),
    FormField("show_lid", "Show Lid", "bool", True),
)


class Box:
    """One-line parametric box builder with PythonSCAD Qt6 GUI form support.

    Calling ``Box(...)`` directly returns a 3D solid (body, plus lid placed beside
    it when ``show_lid=True``) without needing a :class:`~pyboxbuilder.project.core.Project`
    or component inventory::

        from pyboxbuilder import Box

        Box(box_type="sliding", width=80, length=60, height=30, pattern="hex", label="TOKENS").show()

    In PythonSCAD (Qt6 builds), typing ``Box(`` or pressing ``Ctrl+Shift+Space``
    inside an existing ``Box(...)`` call opens a PyQt6 form that edits the call
    arguments in place.
    """

    _FIELDS: tuple[FormField, ...] = _BOX_FIELDS

    def __new__(
        cls,
        box_type: BoxType | str = "sliding",
        width: float = 80.0,
        length: float = 60.0,
        height: float = 30.0,
        wall_thickness: float = 2.0,
        floor_thickness: float = 1.6,
        lid_thickness: float = 2.0,
        pattern: PatternType | str = "hex",
        label: str = "",
        catch_type: CatchType | str = "",
        base_chamfer: float = 0.0,
        stackable: StackableMode | str = "",
        show_lid: bool = True,
        lid_offset: float = 10.0,
        **kwargs: Any,
    ) -> Bosl2Solid:
        """Build and return the 3D solid for a single standalone box."""
        bt = _coerce_enum_str(box_type, BoxType) or BoxType.SLIDING
        pat = _coerce_enum_str(pattern, PatternType) or PatternType.HEX
        ct = _coerce_enum_str(catch_type, CatchType)
        st = _coerce_enum_str(stackable, StackableMode)

        project = Project(
            "InteractiveBox",
            wall_thickness=float(wall_thickness),
            floor_thickness=float(floor_thickness),
            lid_thickness=float(lid_thickness),
            base_chamfer=float(base_chamfer) if base_chamfer > 0 else None,
        )

        box_kwargs: dict[str, Any] = dict(kwargs)
        if ct is not None:
            box_kwargs["catch_type"] = ct
        if st is not None:
            box_kwargs["stackable"] = st
        if label or pat != PatternType.HEX:
            lid_obj = LidBuilder(pattern=PatternBuilder(pat))
            if label:
                lid_obj = lid_obj.titled(label)
            box_kwargs.setdefault("lid", lid_obj)

        project.box(bt, label or "Box", size=(float(width), float(length), float(height)), **box_kwargs)
        return _combine_pieces(project, show_lid=show_lid, lid_offset=float(lid_offset))

    @staticmethod
    def get_calltip() -> str:
        """Return the PythonSCAD editor calltip signature for ``Box``."""
        names = ", ".join(f.name for f in _BOX_FIELDS)
        return f"Box({names})"

    @classmethod
    def on_editor_trigger(cls, pos: Any) -> None:
        """Open the PyQt6 parameter form and rewrite the ``Box(...)`` call in the editor."""
        hooks = _get_editor_hooks()
        if hooks is None:
            return
        get_args, replace_args = hooks
        arg_text = get_args(pos)
        param_names = [f.name for f in cls._FIELDS]
        defaults = {f.name: f.default for f in cls._FIELDS}
        parsed, extra = parse_call_args(arg_text, param_names)
        updated = _show_form_dialog("pyboxbuilder — Box", cls._FIELDS, parsed)
        if updated is not None:
            replace_args(pos, format_call_args(updated, defaults, extra))


class CardBox:
    """One-line parametric card box / tray builder with PythonSCAD Qt6 GUI form support.

    Supports flat card boxes, upright/angled card trays with divider slots, and
    automatic sleeve sizing without needing a :class:`~pyboxbuilder.project.core.Project`
    or component inventory::

        from pyboxbuilder import CardBox

        CardBox(count=80, sleeved=True, sleeve="Gamegenic", orientation="angled", tilt_angle=25, divider_slots=3).show()
    """

    _FIELDS: tuple[FormField, ...] = _CARD_BOX_FIELDS

    def __new__(
        cls,
        card_width: float = 63.5,
        card_length: float = 88.0,
        count: int = 60,
        thickness: float = 0.35,
        sleeved: bool = False,
        sleeve: Any = "",
        orientation: str = "flat",
        tilt_angle: float = 0.0,
        divider_slots: int = 0,
        box_type: BoxType | str = "",
        pattern: PatternType | str = "hex",
        label: str = "",
        wall_thickness: float = 2.0,
        floor_thickness: float = 1.6,
        lid_thickness: float = 2.0,
        base_chamfer: float = 0.0,
        show_lid: bool = True,
        lid_offset: float = 10.0,
        **kwargs: Any,
    ) -> Bosl2Solid:
        """Build and return the 3D solid for a standalone card box or card tray."""
        bt = _coerce_enum_str(box_type, BoxType)
        pat = _coerce_enum_str(pattern, PatternType) or PatternType.HEX
        eff_sleeve = None if sleeve == "" else sleeve

        project = Project(
            "InteractiveCardBox",
            wall_thickness=float(wall_thickness),
            floor_thickness=float(floor_thickness),
            lid_thickness=float(lid_thickness),
            base_chamfer=float(base_chamfer) if base_chamfer > 0 else None,
            sleeved=bool(sleeved) or (eff_sleeve is not None),
            sleeve=eff_sleeve,
        )

        card_kwargs: dict[str, Any] = dict(kwargs)
        resolved_type = bt or (
            BoxType.CARD_TRAY if orientation in ("vertical", "angled") else BoxType.SLIDING
        )
        if resolved_type is BoxType.CARD_TRAY and divider_slots > 0:
            card_kwargs.setdefault("divider_slots", int(divider_slots))
        if label or pat != PatternType.HEX:
            lid_obj = LidBuilder(pattern=PatternBuilder(pat))
            if label:
                lid_obj = lid_obj.titled(label)
            card_kwargs.setdefault("lid", lid_obj)

        project.card_box(
            label or "Cards",
            card_size=(float(card_width), float(card_length)),
            count=int(count),
            thickness=float(thickness),
            sleeved=bool(sleeved) or (eff_sleeve is not None),
            sleeve=eff_sleeve,
            orientation=orientation,
            tilt_angle=float(tilt_angle),
            box_type=bt,
            **card_kwargs,
        )
        return _combine_pieces(project, show_lid=show_lid, lid_offset=float(lid_offset))

    @staticmethod
    def get_calltip() -> str:
        """Return the PythonSCAD editor calltip signature for ``CardBox``."""
        names = ", ".join(f.name for f in _CARD_BOX_FIELDS)
        return f"CardBox({names})"

    @classmethod
    def on_editor_trigger(cls, pos: Any) -> None:
        """Open the PyQt6 parameter form and rewrite the ``CardBox(...)`` call in the editor."""
        hooks = _get_editor_hooks()
        if hooks is None:
            return
        get_args, replace_args = hooks
        arg_text = get_args(pos)
        param_names = [f.name for f in cls._FIELDS]
        defaults = {f.name: f.default for f in cls._FIELDS}
        parsed, extra = parse_call_args(arg_text, param_names)
        updated = _show_form_dialog("pyboxbuilder — CardBox", cls._FIELDS, parsed)
        if updated is not None:
            replace_args(pos, format_call_args(updated, defaults, extra))
