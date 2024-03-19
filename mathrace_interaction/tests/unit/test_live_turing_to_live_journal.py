# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.live_turing_to_live_journal."""

import datetime
import io
import pathlib
import tempfile

import pytest

import mathrace_interaction
import mathrace_interaction.test
import mathrace_interaction.test.mock_models
import mathrace_interaction.typing


@pytest.mark.parametrize("num_reads", [2, 4, 6])
def test_live_turing_to_live_journal(
    journal: io.StringIO, race_name: str, race_date: datetime.datetime, num_reads: int,
    turing_dict: mathrace_interaction.typing.TuringDict
) -> None:
    """Test test_live_turing_to_live_journal with a fixed number of reads."""
    journal_copy = io.StringIO(journal.read())
    journal.seek(0)
    tester = mathrace_interaction.test.LiveTuringToLiveJournalTester(
        journal_copy, race_name, race_date, num_reads, mathrace_interaction.test.mock_models)
    final_dict = tester.run()
    assert final_dict == turing_dict


def test_live_turing_to_live_journal_not_started(
    turing_dict: mathrace_interaction.typing.TuringDict,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test that test_live_turing_to_live_journal raises an error when the turing race has not been started yet."""
    with tempfile.TemporaryDirectory() as output_directory:
        Gara = mathrace_interaction.test.mock_models.Gara  # noqa: N806
        turing_dict["inizio"] = None
        turing_race = Gara.create_from_dict(turing_dict)
        turing_race.save()
        runtime_error_contains(
            lambda: mathrace_interaction.live_turing_to_live_journal(
                mathrace_interaction.test.mock_models, turing_race.pk, "", 0.0,
                pathlib.Path(output_directory), lambda time_counter: False),
            f"Please start race {turing_race.pk} from the turing web interface")
