# SPDX-License-Identifier: Apache-2.0
"""FR-000h: the library says when it cannot do what was asked.

The failure being tested for is not a crash — it is the absence of one. A
missing geometry backend used to return ``None`` from every builder, ``False``
from the exporter, and an export that built the whole directory tree, wrote a
0-byte 3MF for each piece, recorded every one as written, and exited 0. There
was nothing to see until the files reached a slicer.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pyboxbuilder.deps import MissingDependencyError, require


class MissingDependencyTests(unittest.TestCase):
    """A dependency that is not there is named, not worked around."""

    def test_it_names_the_package_the_purpose_and_the_fix(self) -> None:
        """The three things a user needs in order to get unstuck."""
        with self.assertRaises(MissingDependencyError) as caught:
            require("no_such_module_xyz", "build the thing")
        message = str(caught.exception)
        self.assertIn("no_such_module_xyz", message)
        self.assertIn("build the thing", message)
        self.assertIn("pip install", message)

    def test_a_package_whose_install_name_differs_says_the_install_name(self) -> None:
        """`pip install fpdf` gets you a different, abandoned package."""
        from pyboxbuilder.deps import INSTALL_HINTS

        self.assertEqual(INSTALL_HINTS["fpdf"], "pip install fpdf2")

    def test_the_backend_is_not_something_pip_can_fetch(self) -> None:
        """Telling a user to `pip install openscad` sends them nowhere."""
        from pyboxbuilder.deps import INSTALL_HINTS

        self.assertNotIn("pip install", INSTALL_HINTS["openscad"])
        self.assertIn("PythonSCAD", INSTALL_HINTS["openscad"])

    def test_it_still_answers_to_except_importerror(self) -> None:
        """So a caller that already handles a missing import is not surprised."""
        self.assertTrue(issubclass(MissingDependencyError, ImportError))

    def test_a_present_module_is_returned(self) -> None:
        self.assertEqual(require("json", "parse a cache").loads("[]"), [])


class NothingToWriteTests(unittest.TestCase):
    """An empty piece is an error, not a 0-byte file."""

    def test_a_piece_with_no_geometry_raises(self) -> None:
        from pyboxbuilder.export.exporter import BoxExporter

        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            with self.assertRaises(RuntimeError) as caught:
                exporter.write_piece("Cards", "body", "mmu", None)
            self.assertIn("Cards", str(caught.exception))

    def test_it_leaves_no_file_behind(self) -> None:
        """Not even the temporary one: a half-written export is still an export
        that looks like it happened."""
        from pyboxbuilder.export.exporter import BoxExporter

        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            with self.assertRaises(RuntimeError):
                exporter.write_piece("Cards", "body", "mmu", None)
            self.assertEqual(list(Path(tmp).rglob("*.3mf")), [])

    def test_it_is_not_recorded_as_written(self) -> None:
        from pyboxbuilder.export.exporter import BoxExporter

        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            with self.assertRaises(RuntimeError):
                exporter.write_piece("Cards", "body", "mmu", None)
            self.assertEqual(exporter.state.written, [])

    def test_a_missing_backend_raises_rather_than_writing_placeholders(self) -> None:
        """The whole failure, end to end: no backend, no silent tree of 0-byte
        files, and a message that says which file wanted it."""
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.export.exporter import BoxExporter

        # Built before the backend is hidden: the geometry is fine, and it is
        # the *write* that has nowhere to go. That is the real shape of the
        # failure — a user with a working description and a broken install.
        solid = block([10.0, 10.0, 10.0])

        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            # None in sys.modules is how the import system spells "this module
            # is not available", so the backend goes missing without touching
            # the machinery that finds it.
            with patch.dict(sys.modules, {"openscad": None}):
                with self.assertRaises(MissingDependencyError) as caught:
                    exporter.write_piece("Cards", "body", "mmu", solid)
            self.assertIn("openscad", str(caught.exception))
            self.assertEqual(
                [p for p in Path(tmp).rglob("*.3mf") if p.stat().st_size == 0], []
            )


class SizingDoesNotGuessTests(unittest.TestCase):
    """A wrong number that looks measured is worse than an error."""

    def test_a_failed_layout_does_not_fall_back_to_an_estimate(self) -> None:
        from pyboxbuilder.compartments import layout as layout_mod

        compartments = [("A", 30.0, 20.0, 10.0), ("B", 25.0, 15.0, 10.0)]
        with patch.object(
            layout_mod, "layout_compartments", side_effect=ArithmeticError("boom")
        ):
            with self.assertRaises(ArithmeticError):
                layout_mod.compute_min_box_size(
                    compartments, max_w=100.0, max_l=100.0
                )

    def test_the_estimate_is_still_used_when_there_is_nothing_to_lay_out(self) -> None:
        """Removing the swallow must not remove the legitimate fallback: no
        bounds given is a question, not a failure."""
        from pyboxbuilder.compartments.layout import compute_min_box_size

        size = compute_min_box_size([("A", 30.0, 20.0, 10.0)])
        self.assertTrue(all(v > 0 for v in size))


class CachesStayForgivingTests(unittest.TestCase):
    """The one exception, and the reason for it: a cache loses no output."""

    def test_a_corrupt_fingerprint_is_a_miss_not_an_error(self) -> None:
        from pyboxbuilder.export import fingerprint as fp

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "Cards_body.3mf"
            target.write_bytes(b"x")
            (Path(tmp) / fp.SIDECAR_NAME).write_text("{not json")
            self.assertFalse(fp.matches(target, "abc"))

    def test_an_unwritable_record_does_not_break_the_export(self) -> None:
        from pyboxbuilder.export import fingerprint as fp

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sub" / "Cards_body.3mf"
            target.parent.mkdir()
            target.write_bytes(b"x")
            with patch(
                "pathlib.Path.write_text", side_effect=OSError("read-only")
            ):
                fp.record(target, "abc")  # must not raise


if __name__ == "__main__":
    unittest.main()
