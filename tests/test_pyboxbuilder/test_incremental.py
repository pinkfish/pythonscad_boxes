# SPDX-License-Identifier: Apache-2.0
"""An export rebuilds what changed, and nothing else (FR-031).

The write gate was already decided from the description rather than the mesh,
but the geometry was built first and then discarded, so a no-op re-export still
paid for every box — 15 of Emberleaf's 21 seconds at draft precision, and
minutes at the 256 facets an export actually uses. These tests hold the line on
both halves: that nothing unchanged is *built*, and that what did change is.
"""

from __future__ import annotations

import tempfile
import unittest

from pyboxbuilder import BoxType, LidBuilder, Project


def project(cards: int = 20, label: str = "Cards", lid_text: str = "Cards") -> Project:
    """A two-box insert whose card box is sized by its cards."""
    p = Project("Inc", game_box_size=(300, 200, 90), generate_spacers=False)
    deck = p.box(
        BoxType.SLIDING, "Deck", size=(70, 100, None), position=(0, 0, 0),
        lid=LidBuilder().titled(lid_text),
    )
    deck.cards(label, count=cards, size=(62.0, 93.0))

    tray = p.box(BoxType.NO_LID, "Tray", size=(70, 100, 20), position=(70, 0, 0))
    tray.compartment("Bits", holds_pieces=True)
    return p


class BuildsOnDemandTests(unittest.TestCase):
    """`build()` describes every piece; the geometry waits to be asked for."""

    def test_describing_a_project_builds_no_geometry(self) -> None:
        built: list[str] = []
        p = project()
        original = p._build_box_solids

        def spy(builder):
            built.append(builder.label)
            return original(builder)

        p._build_box_solids = spy  # type: ignore[method-assign]
        build = p.build()
        self.assertEqual(built, [], "geometry was built before anything asked")

        # Everything that identifies a piece is known without building it.
        deck = next(x for x in build.pieces if x.label == "Deck" and x.kind == "body")
        self.assertEqual(deck.size[0], 70.0)
        self.assertEqual(deck.position, (0.0, 0.0, 0.0))
        self.assertEqual(built, [])

        self.assertIsNotNone(deck.solid)
        self.assertEqual(built, ["Deck"], "asking for the solid builds it")

    def test_a_body_and_its_lid_share_one_build(self) -> None:
        """A box makes both from the same measurements; doing it twice would
        let them disagree — and would double the cost of every lidded box."""
        built: list[str] = []
        p = project()
        original = p._build_box_solids
        p._build_box_solids = lambda b: (built.append(b.label), original(b))[1]  # type: ignore[method-assign]

        build = p.build()
        for piece in build.pieces:
            if piece.label == "Deck":
                self.assertIsNotNone(piece.solid)
        self.assertEqual(built, ["Deck"], "the body and lid built separately")

    def test_a_broken_project_still_fails_when_it_is_built(self) -> None:
        """Validation stays eager: deferring it would move the error to
        whenever something happened to touch a solid."""
        p = Project("Bad", game_box_size=(300, 200, 80))
        box = p.box(BoxType.NO_LID, "Tray")
        box.compartment("Everything")  # fills, so nothing to size the box from

        with self.assertRaises(ValueError) as caught:
            p.build()
        self.assertIn("Tray", str(caught.exception))

    def test_compartments_that_overflow_are_caught_at_build(self) -> None:
        p = Project("Bad", game_box_size=(300, 200, 80))
        box = p.box(BoxType.NO_LID, "Tray", size=(40, 40, 20), position=(0, 0, 0))
        box.compartment("TooBig", size=(200, 200), depth=10)

        with self.assertRaises(ValueError) as caught:
            p.build()
        self.assertIn("do not fit", str(caught.exception))


class IncrementalExportTests(unittest.TestCase):
    """Only what changed is rebuilt, and everything that changed is."""

    def rebuilt(self, out: str, **kwargs) -> tuple[set[str], list[str]]:
        """Export into `out`; return which boxes were built, and what was written."""
        p = project(**kwargs)
        built: list[str] = []
        original = p._build_box_solids
        p._build_box_solids = lambda b: (built.append(b.label), original(b))[1]  # type: ignore[method-assign]
        result = p.export(out)
        return set(built), list(result.written)

    def test_an_unchanged_project_builds_nothing_at_all(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            self.rebuilt(out)
            built, written = self.rebuilt(out)
            self.assertEqual(built, set(), "an unchanged box was rebuilt")
            self.assertEqual(written, [])

    def test_a_changed_box_is_rebuilt_and_its_neighbour_is_not(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            self.rebuilt(out)
            built, written = self.rebuilt(out, cards=40)
            self.assertEqual(built, {"Deck"})
            # The layout guide draws the box at its new height, so it changes
            # too; no other *box* does.
            boxes = [w for w in written if w.endswith(".3mf")]
            self.assertTrue(boxes)
            self.assertTrue(all("Deck" in w for w in boxes), boxes)

    def test_a_lid_label_rebuilds_the_lid_and_not_the_body(self) -> None:
        """A body does not change when its lid's text does."""
        with tempfile.TemporaryDirectory() as out:
            self.rebuilt(out)
            _, written = self.rebuilt(out, lid_text="Something Else")
            self.assertTrue(written)
            self.assertTrue(all("_lid" in w for w in written), written)

    def test_moving_a_box_does_not_rebuild_it(self) -> None:
        """A 3MF holds its piece in its own frame, so where the box sits in
        the game box cannot change the file."""
        with tempfile.TemporaryDirectory() as out:
            project().export(out)

            moved = project()
            object.__setattr__(moved._by_label("Tray"), "position", (90.0, 10.0, 0.0))
            result = moved.export(out)
            self.assertEqual([w for w in result.written if "Tray" in w], [])

    def test_force_rebuilds_everything(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            self.rebuilt(out)
            p = project()
            built: list[str] = []
            original = p._build_box_solids
            p._build_box_solids = lambda b: (built.append(b.label), original(b))[1]  # type: ignore[method-assign]
            result = p.export(out, force=True)
            self.assertEqual(set(built), {"Deck", "Tray"})
            self.assertEqual(
                len([w for w in result.written if w.endswith(".3mf")]), 6
            )

    def test_editing_a_silhouette_rebuilds_the_box_that_uses_it(self) -> None:
        """An SVG's *contents* shape the box, not the path to it — named by
        path alone, editing the file changed nothing about the description."""
        import pathlib

        with tempfile.TemporaryDirectory() as out:
            svg = pathlib.Path(out) / "piece.svg"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<rect width="10" height="10"/></svg>'
            )

            def with_silhouette() -> Project:
                p = Project("Sil", game_box_size=(200, 200, 60), generate_spacers=False)
                box = p.box(BoxType.NO_LID, "Tray", size=(60, 60, 20), position=(0, 0, 0))
                box.compartment("Piece", size=(30, 30), depth=10, shape_file=str(svg))
                return p

            with_silhouette().export(out)
            self.assertEqual(with_silhouette().export(out).written, ())

            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<rect width="8" height="8"/></svg>'
            )
            self.assertTrue(with_silhouette().export(out).written)


class SelectiveExportTests(unittest.TestCase):
    """`only` exports one box without disturbing the rest."""

    def test_only_writes_the_named_box(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = project().export(out, only="Tray")
            self.assertTrue(result.written)
            self.assertTrue(all("Tray" in w for w in result.written), result.written)

    def test_only_leaves_the_others_alone_on_disk(self) -> None:
        """A partial export knows nothing about what it was not asked for, so
        it must not conclude those files are stale."""
        with tempfile.TemporaryDirectory() as out:
            project().export(out)
            before = sorted(p.name for p in (__import__("pathlib").Path(out) / "Inc" / "mmu").iterdir())
            project(cards=40).export(out, only="Tray")
            after = sorted(p.name for p in (__import__("pathlib").Path(out) / "Inc" / "mmu").iterdir())
            self.assertEqual(before, after)

    def test_an_unknown_box_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaises(ValueError) as caught:
                project().export(out, only="Nope")
        message = str(caught.exception)
        self.assertIn("Nope", message)
        self.assertIn("Deck", message, "the message should list what there is")


class SelectivePreviewTests(unittest.TestCase):
    """The same selection, for looking at one box while working on it."""

    def test_one_box_previews_alone(self) -> None:
        pieces = project().preview_pieces(only="Tray")
        self.assertEqual({p.label for p in pieces}, {"Tray"})

    def test_previewing_one_box_builds_only_that_box(self) -> None:
        p = project()
        built: list[str] = []
        original = p._build_box_solids
        p._build_box_solids = lambda b: (built.append(b.label), original(b))[1]  # type: ignore[method-assign]
        p.preview_pieces(only="Deck")
        self.assertEqual(built, ["Deck"])

    def test_lids_only_leaves_the_bodies_out(self) -> None:
        pieces = project().preview_pieces(only="Deck", lids_only=True)
        self.assertTrue(pieces)
        self.assertEqual({(p.label, p.kind) for p in pieces}, {("Deck", "lid")})

    def test_a_previewed_lid_carries_its_label(self) -> None:
        """A label is a coloured *insert*, a separate solid so the slicer can
        give it its own material. The preview dropped the inserts, so every
        lid previewed blank while the exported one carried its text — the
        divergence FR-046c exists to prevent."""
        plain = project(lid_text="").preview_pieces(only="Deck", lids_only=True)
        labelled = project(lid_text="Deck").preview_pieces(only="Deck", lids_only=True)
        self.assertGreater(len(labelled), len(plain))

    def test_lids_only_implies_show_lids(self) -> None:
        """Asking for lids and getting nothing would be a puzzling result."""
        self.assertTrue(project().preview_pieces(lids_only=True))

    def test_an_unknown_box_is_named(self) -> None:
        with self.assertRaises(ValueError):
            project().preview_pieces(only="Nope")


if __name__ == "__main__":
    unittest.main()
