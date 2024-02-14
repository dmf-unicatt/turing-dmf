# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.journal_reader."""

import datetime
import io

from mathrace_interaction.journal_reader import journal_reader, TuringDict


def strip_mathrace_only_attributes(imported_dict: TuringDict) -> None:
    """Strip attributes marked as mathrace only in order to be able to perform a comparison with a turing dict."""
    if "mathrace_only" in imported_dict:
        del imported_dict["mathrace_only"]
    if "mathrace_id" in imported_dict:
        del imported_dict["mathrace_id"]
    for value in imported_dict.values():
        if isinstance(value, list):
            for value_entry in value:
                assert isinstance(value_entry, dict)
                strip_mathrace_only_attributes(value_entry)


def test_journal_reader(
    journal: io.StringIO, race_name: str, race_date: datetime.datetime, turing_dict: TuringDict
) -> None:
    """Test that journal_reader correctly imports sample journals."""
    with journal_reader(journal, race_name, race_date) as journal_stream:
        imported_dict = journal_stream.read()
    strip_mathrace_only_attributes(imported_dict)
    assert imported_dict == turing_dict
