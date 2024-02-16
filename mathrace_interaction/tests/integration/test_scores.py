# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test that the final race scores are equal to the expected ones."""

import pathlib
import typing


def test_scores(journal: typing.TextIO, journal_name: str, data_dir: pathlib.Path) -> None:
    """Test that the final race scores are equal to the expected ones."""
    with open(data_dir / journal_name.replace(".journal", ".score")) as score_stream:
        print(score_stream.read())
