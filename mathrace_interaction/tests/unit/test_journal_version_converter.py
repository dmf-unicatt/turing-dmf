# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.journal_version_converter."""

import io
import tempfile
import typing

import pytest

from mathrace_interaction.journal_version_converter import journal_version_converter
from mathrace_interaction.strip_comments_and_unhandled_events_from_journal import (
    strip_comments_and_unhandled_events_from_journal)

RunEntrypointFixtureType: typing.TypeAlias = typing.Callable[[str, list[str]], tuple[str, str]]


def test_journal_version_converter_identity(journal: io.StringIO, journal_version: str) -> None:
    """Test that journal_version_converter is the identity operator when applied on the current version."""
    # The call to journal_version_converter consumes and closes the journal stream, which would then
    # be unavailable for the subsequent call to strip_comments_and_unhandled_events_from_journal.
    # It is simpler to create a two copies of journal, one for each call.
    converted_journal = journal_version_converter(io.StringIO(journal.getvalue()), journal_version).strip("\n")
    expected_journal = strip_comments_and_unhandled_events_from_journal(io.StringIO(journal.getvalue())).strip("\n")
    assert converted_journal == expected_journal


def test_journal_version_converter_other(
    journal: io.StringIO, journal_version: str, other_journal: io.StringIO, other_journal_version: str
) -> None:
    """Test that journal_version_converter when applied on a different version."""
    converted_journal = journal_version_converter(
        io.StringIO(journal.getvalue()), other_journal_version).strip("\n")
    expected_journal = strip_comments_and_unhandled_events_from_journal(
        io.StringIO(other_journal.getvalue())).strip("\n")
    stripped_journal = strip_comments_and_unhandled_events_from_journal(
        io.StringIO(journal.getvalue())).strip("\n")
    assert converted_journal == expected_journal
    if (
        journal_version == other_journal_version or
        (journal_version == "r11184" and other_journal_version == "r11189") or
        (journal_version == "r11189" and other_journal_version == "r11184")
    ):
        # The two versions coincides, so each of the journals generated in this call must be the same.
        # Note that for the goals of this function r11184 and r11189 are the same version, because
        # the only change in r11189 is the introduction of a second timer, but timer events are discared by
        # strip_comments_and_unhandled_events_from_journal
        assert converted_journal == stripped_journal
    else:
        # Ensure that the conversion did use a different journal version, rather than its original one
        assert converted_journal != stripped_journal


@pytest.mark.parametrize(
    "input_file_option,journal_version_option,output_file_option", [
        ("-i", "-v", "-o"),
        ("--input-file", "--journal-version", "--output-file")
    ]
)
def test_journal_version_converter_entrypoint(
    run_entrypoint: RunEntrypointFixtureType, journal: io.StringIO, journal_version: str,
    input_file_option: str, journal_version_option: str, output_file_option: str
) -> None:
    """Test running journal_version_converter as entrypoint."""
    with tempfile.NamedTemporaryFile() as input_journal_file, tempfile.NamedTemporaryFile() as output_journal_file:
        with open(input_journal_file.name, "w") as input_journal_stream:
            input_journal_stream.write(journal.read())
            journal.seek(0)
            expected_journal = strip_comments_and_unhandled_events_from_journal(journal).strip("\n")
        stdout, stderr = run_entrypoint(
            "mathrace_interaction.journal_version_converter", [
                input_file_option, input_journal_file.name, journal_version_option, journal_version,
                output_file_option, output_journal_file.name
            ]
        )
        assert stdout == ""
        assert stderr == ""
        with open(output_journal_file.name) as output_journal_stream:
            stripped_journal = output_journal_stream.read().strip("\n")
        assert expected_journal == stripped_journal
        # The same journal stream is shared on the parametrization on input_file_option: since the stream
        # was consumed reset it to the beginning before passing to the next parametrized item
        journal.seek(0)