# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test that the files produced by journal_reader can be imported into turing."""

import datetime
import os
import typing

import engine.models
import jsondiff
import pytest

import mathrace_interaction
import mathrace_interaction.filter
import mathrace_interaction.typing


@pytest.mark.django_db
def test_journal_reader_integration(journal: typing.TextIO, journal_name: str) -> None:
    """Test that journal_reader can import journals in the data directory."""
    journal_year, _ = journal_name.split(os.sep, maxsplit=1)
    journal_date = datetime.datetime(int(journal_year), 1, 1, tzinfo=datetime.UTC)
    with mathrace_interaction.journal_reader(journal) as journal_stream:
        turing_dict = journal_stream.read(journal_name, journal_date)
    mathrace_interaction.filter.strip_mathrace_only_attributes_from_imported_turing(turing_dict)
    mathrace_interaction.filter.reorder_lists_in_imported_turing(turing_dict)
    gara = engine.models.Gara.create_from_dict(turing_dict)
    diff = jsondiff.diff(gara.to_dict(), turing_dict, syntax="symmetric")
    assert diff == {}
