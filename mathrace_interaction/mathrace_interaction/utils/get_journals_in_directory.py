# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Return all journals in a specific directory."""

import pathlib


def get_journals_in_directory(directory: pathlib.Path) -> dict[str, pathlib.Path]:
    """Return all journals in a specific directory."""
    journals_set = set()
    for entry in directory.rglob("*"):
        assert entry.is_file() or entry.is_dir()
        if entry.is_file():
            if entry.suffix == ".journal":
                journals_set.add(entry)
        elif entry.is_dir():
            pass
        else:  # pragma: no cover
            raise RuntimeError(f"Invalid {entry}")
    return {str(journal.relative_to(directory)): journal for journal in sorted(journals_set)}
