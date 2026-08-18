# SPDX-License-Identifier: Apache-2.0
#
# Printable output is produced here and only here. It is manual on purpose:
# an export builds at 256 facets per circle (FR-046) because that geometry is
# what gets printed, and a full insert at that precision takes minutes. Tests
# and previews never go near it.
#
#   make export                 # every insert, only what changed
#   make export-emberleaf       # one insert
#   make export FORCE=1         # rebuild everything
#   make show-emberleaf         # preview it instead
#   make test lint types        # the checks CI runs
#
# Two layers of skipping, and they do different jobs. Make's own timestamps
# skip an insert whose *script* has not been edited — that costs nothing at
# all, not even importing it. Inside a run, the export skips each box whose
# *description* has not changed (FR-031), which is what catches an edit that
# touched only one box out of twenty.

PYTHON  ?= python3
OUT     ?= output
BOXES   ?= boxes
PYBOX   := $(PYTHON) -m pyboxbuilder.cli

# Rebuild everything: FORCE=1 make export
ifdef FORCE
FORCE_FLAG := --force
endif

# Every boxes/<name>/<name>.py, and a stamp per insert recording its last build.
SCRIPTS := $(wildcard $(BOXES)/*/*.py)
INSERTS := $(sort $(foreach s,$(SCRIPTS),$(if $(filter $(notdir $(basename $(s))),$(notdir $(patsubst %/,%,$(dir $(s))))),$(notdir $(basename $(s))))))
STAMPS  := $(foreach i,$(INSERTS),$(OUT)/.stamp-$(i))

.PHONY: all export list show clean clean-stamps test lint types check help

help:
	@echo "Inserts: $(INSERTS)"
	@echo
	@echo "  make export              every insert, rebuilding only what changed"
	@echo "  make export-<insert>     just that one"
	@echo "  make export FORCE=1      rebuild everything"
	@echo "  make show-<insert>       preview instead of exporting"
	@echo "  make list                every insert's boxes"
	@echo "  make check               test, lint and types"

all: export

export: $(STAMPS)

# One rule per insert, generated: a stamp depends on that insert's own sources
# — its script and any SVG silhouettes beside it — so an untouched insert is
# not even imported. The export inside still decides per box, since a script
# can change without every box changing.
#
# Written out with `eval` rather than as a pattern rule because a pattern rule
# allows `%` once, and the path repeats the insert's name: boxes/earth/earth.py.
#
# Only the .py files are prerequisites. An insert's SVG silhouettes are *not*,
# because make cannot carry a filename with a space in it and several of them
# have one ("black leader.svg"). They do not need to be: an SVG's contents are
# part of the description a box is fingerprinted on (FR-031), so editing one
# re-exports the boxes that use it — from `make export-<insert>`, which skips
# make's timestamp check, or from `make clean-stamps export`.
define insert_rule
$(OUT)/.stamp-$(1): $$(wildcard $(BOXES)/$(1)/*.py)
	@mkdir -p $$(OUT)
	$$(PYBOX) export $(BOXES)/$(1)/$(1).py --out $$(OUT) $$(FORCE_FLAG)
	@touch $$@
endef

$(foreach insert,$(INSERTS),$(eval $(call insert_rule,$(insert))))

# `make export-emberleaf`, and the same without the timestamp check.
export-%:
	@mkdir -p $(OUT)
	$(PYBOX) export $(BOXES)/$*/$*.py --out $(OUT) $(FORCE_FLAG)
	@touch $(OUT)/.stamp-$*

show-%:
	$(PYTHON) $(BOXES)/$*/$*.py $(ARGS)

list:
	@$(PYBOX) list --all --examples $(BOXES)

# Removing the stamps re-runs every insert; the exports inside still skip the
# boxes that did not change, which is usually what you want. `make clean`
# throws the files away too.
clean-stamps:
	rm -f $(OUT)/.stamp-*

clean:
	rm -rf $(OUT)

test:
	PYTHONPATH=. PYBOXBUILDER_EXPORT_FN=12 $(PYTHON) -m pytest tests/test_pyboxbuilder/ -q

lint:
	PYTHONPATH=. $(PYTHON) -m ruff check pyboxbuilder/ boxes/

types:
	PYTHONPATH=. $(PYTHON) -m mypy pyboxbuilder/

check: test lint types
