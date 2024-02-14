# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.determine_journal_version."""

import io
import typing

from mathrace_interaction.determine_journal_version import determine_journal_version

RuntimeErrorContainsFixtureType: typing.TypeAlias = typing.Callable[[typing.Callable[[], typing.Any], str], None]


def test_determine_journal_version(journal: io.StringIO, journal_version: str) -> None:
    """Test that test_determine_journal_version correctly recognizes the version of sample journals."""
    assert determine_journal_version(journal) == journal_version


def test_determine_journal_version_error_on_mixed_race_start_codes(
    runtime_error_contains: RuntimeErrorContainsFixtureType
) -> None:
    """Test that test_determine_journal_version raises an error when multiple race start codes are present."""
    wrong_journal = io.StringIO("""\
0 002 inizio gara
0 200 inizio gara
""")
    runtime_error_contains(
        lambda: determine_journal_version(wrong_journal),
        "More than one race start event detected, with different event codes")
