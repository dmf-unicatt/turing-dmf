# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.journal_reader and mathrace_interaction.journal_writer on journals in data."""

import datetime
import os
import typing

from mathrace_interaction.journal_reader import journal_reader


def test_journal_reader_writer_on_data(journal: typing.TextIO, journal_name: str) -> None:
    """Test that journal_reader runs successfully on all journals in the data directory."""
    journal_date = datetime.datetime(int(journal_name.split(os.sep)[0]), 1, 1, tzinfo=datetime.UTC)
    with journal_reader(journal) as journal_stream:
        journal_stream.read(journal_name, journal_date)
