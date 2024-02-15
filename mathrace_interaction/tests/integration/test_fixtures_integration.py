# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test fixtures defined in conftest.py."""

import pathlib

import pytest


@pytest.mark.requires_all_journals
def test_journals_fixture(data_dir: pathlib.Path, journals: list[pathlib.Path]) -> None:
    """Test that the journals fixture actually contains all journal files."""
    journals_actual = set()
    for entry in data_dir.rglob("*"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            if entry.suffix == ".journal":
                journals_actual.add(entry)
        elif entry.is_dir():
            pass
        else:
            raise RuntimeError(f"Invalid {entry}")
    journals_difference = journals_actual.symmetric_difference(journals)
    assert len(journals_difference) == 0, f"Unlisted journals found {journals_difference}"
