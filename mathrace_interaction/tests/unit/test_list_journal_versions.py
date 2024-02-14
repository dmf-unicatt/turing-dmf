# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.list_journal_versions."""

from mathrace_interaction.list_journal_versions import list_journal_versions


def test_list_journal_versions() -> None:
    """Test the cardinality of versions returned by list_journal_versions."""
    versions = list_journal_versions()
    assert len(versions) == 10
