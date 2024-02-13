# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test fixtures defined in conftest.py."""

import pathlib

import pytest


@pytest.mark.requires_all_journals
def test_data_journal_fixture(data_dir: pathlib.Path, data_journals: list[pathlib.Path]) -> None:
    """Test that the data_journals fixture actually contains all journal files."""
    data_journals_actual = set()
    for entry in data_dir.rglob("*"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            if entry.suffix == ".journal":
                data_journals_actual.add(entry)
        elif entry.is_dir():
            pass
        else:
            raise RuntimeError(f"Invalid {entry}")
    data_journals_difference = data_journals_actual.symmetric_difference(data_journals)
    assert len(data_journals_difference) == 0, f"Unlisted journals found {data_journals_difference}"
