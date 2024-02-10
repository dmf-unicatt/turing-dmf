# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test consistency of files in data."""

import pathlib

import pytest


def test_data_directory_exists(data_dir: pathlib.Path) -> None:
    """Test the presence of the data directory."""
    assert data_dir.exists()
    assert data_dir.is_dir()


@pytest.mark.parametrize("this_extension,other_extension", [(".journal", ".score"), (".score", ".journal")])
def test_data_both_journal_and_score_files_exist(
    data_dir: pathlib.Path, this_extension: str, other_extension: str
) -> None:
    """Test that every journal file has an associated score file, and viceversa."""
    found_files = 0
    for entry in data_dir.rglob(f"*{this_extension}"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            assert entry.with_suffix(other_extension).exists()
            found_files += 1
        elif entry.is_dir():
            pass
        else:
            raise RuntimeError(f"Invalid {entry}")
    assert found_files > 0


def test_data_contains_only_journal_and_score_files(data_dir: pathlib.Path) -> None:
    """Test that the data directory only contains journal and score files."""
    for entry in data_dir.rglob(f"*"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            assert entry.suffix in (".journal", ".score")
        elif entry.is_dir():
            pass
        else:
            raise RuntimeError(f"Invalid {entry}")


def test_data_journal_all_fixture(data_dir: pathlib.Path, data_journals_all: list[pathlib.Path]) -> None:
    """Test that the data_journals_all fixture actually contains all journal files."""
    data_journals_actual = set()
    for entry in data_dir.rglob(f"*"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            if entry.suffix == ".journal":
                data_journals_actual.add(entry)
        elif entry.is_dir():
            pass
        else:
            raise RuntimeError(f"Invalid {entry}")
    data_journals_difference = data_journals_actual.symmetric_difference(data_journals_all)
    assert len(data_journals_difference) == 0, f"Unlisted journals found {data_journals_difference}"
