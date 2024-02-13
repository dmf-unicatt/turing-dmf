# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.journal_reader."""

import datetime
import pathlib

from mathrace_interaction.journal_reader import journal_reader


def test_journal_reader_success(data_journals: list[pathlib.Path]) -> None:
    """Test that journal_reader runs successfully on all journals in the data directory."""
    for journal in data_journals:
        journal_date = datetime.datetime(int(journal.parent.name), 1, 1, tzinfo=datetime.UTC)
        with journal_reader(open(journal), journal.name, journal_date) as journal_stream:
            journal_stream.read()
