# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.determine_journal_version."""

import io

from mathrace_interaction.determine_journal_version import determine_journal_version


def test_determine_journal_version(journal: io.StringIO, journal_version: str) -> None:
    """Test that test_determine_journal_version correctly recognizes the version of sample journals."""
    assert determine_journal_version(journal) == journal_version
