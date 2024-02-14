# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""pytest configuration file for functional tests."""

import pathlib

import pytest

_data_dir = pathlib.Path(__file__).parent.parent.parent / "data"

def generate_journals() -> list[pathlib.Path]:
    """Return all journals in the data directory."""
    journals_set = set()
    for entry in _data_dir.rglob("*"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            if entry.suffix == ".journal":
                journals_set.add(entry)
        elif entry.is_dir():
            pass
        else:
            raise RuntimeError(f"Invalid {entry}")
    return list(sorted(journals_set))

_journals = generate_journals()


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize tests with journal fixture over journals in the data directory."""
    _journals_as_str = [str(journal.relative_to(_data_dir)) for journal in _journals]
    if "journal" in metafunc.fixturenames:
        metafunc.parametrize("journal", _journals, ids=_journals_as_str)


@pytest.fixture
def data_dir() -> pathlib.Path:
    """Return the data directory of mathrace-interaction."""
    return _data_dir


@pytest.fixture
def journals() -> list[pathlib.Path]:
    """Return all journals in the data directory, as a fixture."""
    return _journals
