# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""pytest configuration file for unit tests."""

import pathlib

import pytest


@pytest.fixture(scope="session")
def data_dir() -> pathlib.Path:
    """Return the data directory of mathrace-interaction."""
    return pathlib.Path(__file__).parent.parent.parent / "data"


@pytest.fixture(scope="session")
def data_journals(data_dir: pathlib.Path) -> list[pathlib.Path]:
    """Return all journals in the data directory."""
    data_journals_set = set()
    for entry in data_dir.rglob("*"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            if entry.suffix == ".journal":
                data_journals_set.add(entry)
        elif entry.is_dir():
            pass
        else:
            raise RuntimeError(f"Invalid {entry}")
    return list(sorted(data_journals_set))
