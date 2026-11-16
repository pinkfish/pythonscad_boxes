# AGENTS.md

Guidance for coding agents and contributors working in `pythonscad_boxes`.

## Git & Pull Request Policy

- **Always push to a branch and pull the changes into `main` via a Pull Request.** Never commit directly to `main` or push directly to `main`.
- Workflow for every change:
  1. Create a descriptive branch from an up-to-date `main` (e.g., `feat/...`, `fix/...`, `docs/...`, `test/...`).
  2. Make and verify your edits on that branch (lint, type-check, relevant tests, and regenerated STLs/docs if geometry or docs changed).
  3. Commit and push the branch to `origin`:
     ```sh
     git push -u origin <branch-name>
     ```
  4. Open a Pull Request targeting `main` and merge/pull the changes into `main`, deleting the feature branch afterward:
     ```sh
     gh pr create --base main --head <branch-name>
     gh pr merge --merge --admin --delete-branch
     ```

## Quality Checks & Commands

Run checks inside `.venv` before opening or merging a Pull Request:

```sh
# Lint & static type checking (blocking in CI)
.venv/bin/ruff check pyboxbuilder/ boxes/
.venv/bin/mypy pyboxbuilder/

# Fast CI base test suite
PYTHONPATH=".:tests" .venv/bin/pytest tests/test_pyboxbuilder/ --base-only --ignore=tests/test_pyboxbuilder/render -k "not export" -q

# Full test suite (with coarse export resolution)
PYBOXBUILDER_EXPORT_FN=12 .venv/bin/pytest tests/test_pyboxbuilder/ -n auto -q

# Regenerate box STLs/docs & build Sphinx HTML when geometry or docs change
.venv/bin/python scripts/generate_box_docs.py
.venv/bin/sphinx-build -b html docs docs/_build/html
```
