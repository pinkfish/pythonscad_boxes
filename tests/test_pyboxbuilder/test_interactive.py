# SPDX-License-Identifier: Apache-2.0
"""Tests for interactive PythonSCAD GUI classes (Box and CardBox)."""

from __future__ import annotations

import builtins
import sys
import types
from typing import Any

import pytest

from pyboxbuilder import Box, BoxType, CardBox, CatchType, PatternType
from pyboxbuilder.interactive import (
    _get_editor_hooks,
    _show_form_dialog,
    format_call_args,
    parse_call_args,
)


class _FakeSignal:
    def __init__(self) -> None:
        self.callbacks: list[Any] = []

    def connect(self, cb: Any) -> None:
        self.callbacks.append(cb)


class _FakeQtWidgets:
    """Minimal in-memory PyQt6.QtWidgets stub for testing dialog round-trips."""

    def __init__(self, *, accept: bool = True, overrides: dict[str, Any] | None = None) -> None:
        self.accept_result = accept
        self.overrides = overrides or {}
        self._last_widgets: dict[str, Any] = {}

    def make_module(self) -> types.ModuleType:
        parent = self

        class _DialogCode:
            Accepted = 1
            Rejected = 0

        class _StandardButton:
            Ok = 1
            Cancel = 2

        class QDialog:
            DialogCode = _DialogCode

            def __init__(self) -> None:
                self.title = ""

            def setWindowTitle(self, t: str) -> None:
                self.title = t

            def accept(self) -> None:
                pass

            def reject(self) -> None:
                pass

            def exec(self) -> int:
                return _DialogCode.Accepted if parent.accept_result else _DialogCode.Rejected

        class QFormLayout:
            def __init__(self, _dialog: Any) -> None:
                self.rows: list[Any] = []

            def addRow(self, *args: Any) -> None:
                self.rows.append(args)
                if len(args) == 2 and isinstance(args[0], str):
                    lbl, widget = args
                    if lbl in parent.overrides:
                        val = parent.overrides[lbl]
                        if hasattr(widget, "setValue"):
                            widget.setValue(val)
                        elif hasattr(widget, "setChecked"):
                            widget.setChecked(val)
                        elif hasattr(widget, "setCurrentText"):
                            widget.setCurrentText(val)
                        elif hasattr(widget, "setText"):
                            widget.setText(val)

        class QDoubleSpinBox:
            def __init__(self) -> None:
                self._val = 0.0

            def setRange(self, _a: float, _b: float) -> None:
                pass

            def setSingleStep(self, _s: float) -> None:
                pass

            def setDecimals(self, _d: int) -> None:
                pass

            def setValue(self, v: float) -> None:
                self._val = float(v)

            def value(self) -> float:
                return self._val

        class QSpinBox:
            def __init__(self) -> None:
                self._val = 0

            def setRange(self, _a: int, _b: int) -> None:
                pass

            def setSingleStep(self, _s: int) -> None:
                pass

            def setValue(self, v: int) -> None:
                self._val = int(v)

            def value(self) -> int:
                return self._val

        class QCheckBox:
            def __init__(self) -> None:
                self._checked = False

            def setChecked(self, c: bool) -> None:
                self._checked = bool(c)

            def isChecked(self) -> bool:
                return self._checked

        class QComboBox:
            def __init__(self) -> None:
                self._items: list[str] = []
                self._idx = 0

            def addItems(self, items: list[str]) -> None:
                self._items = list(items)

            def findText(self, text: str) -> int:
                return self._items.index(text) if text in self._items else -1

            def setCurrentIndex(self, idx: int) -> None:
                self._idx = idx

            def setCurrentText(self, text: str) -> None:
                if text in self._items:
                    self._idx = self._items.index(text)
                else:
                    self._items.append(text)
                    self._idx = len(self._items) - 1

            def currentText(self) -> str:
                return self._items[self._idx] if self._items else ""

        class QLineEdit:
            def __init__(self, text: str = "") -> None:
                self._text = text

            def setText(self, t: str) -> None:
                self._text = t

            def text(self) -> str:
                return self._text

        class QDialogButtonBox:
            StandardButton = _StandardButton

            def __init__(self, _buttons: int) -> None:
                self.accepted = _FakeSignal()
                self.rejected = _FakeSignal()

        qt_widgets = types.ModuleType("PyQt6.QtWidgets")
        qt_widgets.QDialog = QDialog  # type: ignore[attr-defined]
        qt_widgets.QFormLayout = QFormLayout  # type: ignore[attr-defined]
        qt_widgets.QDoubleSpinBox = QDoubleSpinBox  # type: ignore[attr-defined]
        qt_widgets.QSpinBox = QSpinBox  # type: ignore[attr-defined]
        qt_widgets.QCheckBox = QCheckBox  # type: ignore[attr-defined]
        qt_widgets.QComboBox = QComboBox  # type: ignore[attr-defined]
        qt_widgets.QLineEdit = QLineEdit  # type: ignore[attr-defined]
        qt_widgets.QDialogButtonBox = QDialogButtonBox  # type: ignore[attr-defined]
        return qt_widgets


class TestArgParsingAndFormatting:
    """Tests for AST-based call argument parsing and minimal formatting."""

    def test_parse_and_format_roundtrip(self) -> None:
        params = ("box_type", "width", "length", "height", "show_lid")
        defaults = {
            "box_type": "sliding",
            "width": 80.0,
            "length": 60.0,
            "height": 30.0,
            "show_lid": True,
        }
        parsed, extra = parse_call_args("'cap', 100, height=40, custom_kw=foo()", params)
        assert parsed == {"box_type": "cap", "width": 100, "height": 40}
        assert extra == ["custom_kw=foo()"]

        formatted = format_call_args(
            {"box_type": "cap", "width": 100.0, "length": 60.0, "height": 40.0, "show_lid": True},
            defaults,
            extra,
        )
        assert formatted == "box_type='cap', width=100.0, height=40.0, custom_kw=foo()"

    def test_parse_edge_cases(self) -> None:
        assert parse_call_args("", ("width",)) == ({}, [])
        parsed, extra = parse_call_args("not valid python (", ("width",))
        assert parsed == {}
        assert extra == ["not valid python ("]

        parsed2, extra2 = parse_call_args("my_var, 10, **opts", ("width",))
        assert parsed2 == {}
        assert extra2 == ["width=my_var", "10", "**opts"]


class TestInteractiveBoxAndCardBox:
    """Tests for Box and CardBox geometry construction, calltips, and editor triggers."""

    def test_box_builds_solids_directly(self) -> None:
        solid_lidded = Box(
            box_type="sliding",
            width=70.0,
            length=50.0,
            height=25.0,
            pattern="hex",
            label="TOKENS",
            catch_type=CatchType.WEDGE,
            base_chamfer=0.4,
            show_lid=True,
        )
        assert solid_lidded is not None

        solid_body_only = Box(
            box_type=BoxType.NO_LID,
            width=60.0,
            length=40.0,
            height=20.0,
            pattern=PatternType.SOLID,
            stackable="inside",
            show_lid=False,
        )
        assert solid_body_only is not None
        assert Box.get_calltip().startswith("Box(box_type, width, length, height")

    def test_card_box_builds_flat_and_angled_solids(self) -> None:
        flat = CardBox(card_width=63.5, card_length=88.0, count=50, sleeved=True, sleeve="Gamegenic", label="DECK")
        assert flat is not None

        angled = CardBox(
            card_width=63.5,
            card_length=88.0,
            count=60,
            orientation="angled",
            tilt_angle=25.0,
            divider_slots=2,
            base_chamfer=0.4,
            show_lid=False,
        )
        assert angled is not None
        assert CardBox.get_calltip().startswith("CardBox(card_width, card_length, count")

    def test_on_editor_trigger_updates_script_via_pyqt6_dialog(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Stub PyQt6 in sys.modules
        fake_qt = _FakeQtWidgets(accept=True, overrides={"Width (mm)": 120.0, "Lid Label": "COINS"})
        qt_pkg = types.ModuleType("PyQt6")
        qt_widgets = fake_qt.make_module()
        qt_pkg.QtWidgets = qt_widgets  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "PyQt6", qt_pkg)
        monkeypatch.setitem(sys.modules, "PyQt6.QtWidgets", qt_widgets)

        # Stub PythonSCAD editor hooks in builtins
        written: list[tuple[Any, str]] = []
        monkeypatch.setattr(builtins, "editor_get_call_args", lambda _pos: "box_type='cap', width=90.0", raising=False)
        monkeypatch.setattr(
            builtins, "editor_replace_call_args", lambda pos, text: written.append((pos, text)), raising=False
        )

        assert _get_editor_hooks() is not None
        Box.on_editor_trigger(42)
        assert len(written) == 1
        assert written[0][0] == 42
        assert "box_type='cap'" in written[0][1]
        assert "width=120.0" in written[0][1]
        assert "label='COINS'" in written[0][1]

        # Test CardBox trigger too
        fake_qt_cards = _FakeQtWidgets(accept=True, overrides={"Card Count": 100, "Sleeved": True})
        qt_pkg.QtWidgets = fake_qt_cards.make_module()  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "PyQt6.QtWidgets", qt_pkg.QtWidgets)
        CardBox.on_editor_trigger(99)
        assert len(written) == 2
        assert written[1][0] == 99
        assert "count=100" in written[1][1]
        assert "sleeved=True" in written[1][1]

        # Cancelled dialog should not overwrite editor text
        fake_qt_cancel = _FakeQtWidgets(accept=False)
        qt_pkg.QtWidgets = fake_qt_cancel.make_module()  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "PyQt6.QtWidgets", qt_pkg.QtWidgets)
        Box.on_editor_trigger(77)
        assert len(written) == 2

    def test_on_editor_trigger_graceful_without_hooks_or_pyqt6(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Without editor hooks, should quietly return None
        assert _get_editor_hooks() is None
        Box.on_editor_trigger(0)
        CardBox.on_editor_trigger(0)

        # Without PyQt6, _show_form_dialog returns None
        monkeypatch.setitem(sys.modules, "PyQt6", None)  # type: ignore[arg-type]
        assert _show_form_dialog("Test", Box._FIELDS, {}) is None
