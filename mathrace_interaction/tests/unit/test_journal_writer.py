# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.journal_writer."""

import datetime
import io
import json
import tempfile

import pytest

import mathrace_interaction
import mathrace_interaction.filter
import mathrace_interaction.typing


def test_journal_writer(
    turing_dict: mathrace_interaction.typing.TuringDict, journal: io.StringIO, journal_version: str
) -> None:
    """Test that journal_writer correctly exports sample journals."""
    with (
        io.StringIO("") as exported_journal,
        mathrace_interaction.journal_writer(exported_journal, journal_version) as journal_stream
    ):
        journal_stream.write(turing_dict)
        assert mathrace_interaction.filter.strip_comments_and_unhandled_events_from_journal(
            journal) == exported_journal.getvalue().strip("\n")


@pytest.mark.parametrize(
    "input_file_option,journal_version_option,output_file_option", [
        ("-i", "-v", "-o"),
        ("--input-file", "--journal-version", "--output-file")
    ]
)
def test_journal_writer_entrypoint(
    turing_dict: mathrace_interaction.typing.TuringDict,
    run_entrypoint: mathrace_interaction.typing.RunEntrypointFixtureType,
    race_name: str, race_date: datetime.datetime, journal: io.StringIO, journal_version: str,
    input_file_option: str, journal_version_option: str, output_file_option: str
) -> None:
    """Test running journal_writer as entrypoint."""
    with tempfile.NamedTemporaryFile() as json_file, tempfile.NamedTemporaryFile() as journal_file:
        with open(json_file.name, "w") as json_stream:
            json_stream.write(json.dumps(turing_dict))
        stdout, stderr = run_entrypoint(
            "mathrace_interaction.journal_writer", [
                input_file_option, json_file.name, journal_version_option, journal_version,
                output_file_option, journal_file.name
            ]
        )
        assert stdout == ""
        assert stderr == ""
        with open(journal_file.name) as journal_stream:
            exported_journal = journal_stream.read()
        assert mathrace_interaction.filter.strip_comments_and_unhandled_events_from_journal(
            journal) == exported_journal.strip("\n")
        # The same journal stream is shared on the parametrization on command line options: since the stream
        # was consumed reset it to the beginning before passing to the next parametrized item
        journal.seek(0)


def test_journal_writer_wrong_num_questions(
    turing_dict: mathrace_interaction.typing.TuringDict,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test that journal_reader raises an error when turing is inconsistent on the number of questions."""
    turing_dict["num_problemi"] = str(int(turing_dict["num_problemi"]) + 1)
    with (
        io.StringIO("") as exported_journal,
        mathrace_interaction.journal_writer(exported_journal, "r5539") as journal_stream
    ):
        runtime_error_contains(
            lambda: journal_stream.write(turing_dict), "Inconsistent data in turing dictionary: 8 != 7")


def test_journal_writer_wrong_race_event(
    turing_dict: mathrace_interaction.typing.TuringDict,
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test that journal_reader raises an error when an unhandled event code is encountered."""
    turing_dict["eventi"].append({"subclass": "UnhandledEvent"})
    with (
        io.StringIO("") as exported_journal,
        mathrace_interaction.journal_writer(exported_journal, "r5539") as journal_stream
    ):
        runtime_error_contains(
            lambda: journal_stream.write(turing_dict), "Unhandled event type UnhandledEvent")


def test_journal_writer_wrong_version(
    runtime_error_contains: mathrace_interaction.typing.RuntimeErrorContainsFixtureType
) -> None:
    """Test that journal_reader raises an error when requesting a wrong version."""
    with io.StringIO("") as exported_journal:
        runtime_error_contains(
            lambda: mathrace_interaction.journal_writer(exported_journal, "r0"),
            "r0 is not among the available versions")
