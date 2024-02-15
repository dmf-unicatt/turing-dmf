# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.determine_journal_version."""

from mathrace_interaction.strip_mathrace_only_attributes_from_imported_turing import (
    strip_mathrace_only_attributes_from_imported_turing)


def test_strip_mathrace_only_attributes_from_imported_turing() -> None:
    """Test strip_mathrace_only_attributes_from_imported_turing."""
    imported_dict = {
        "a_turing_attribute": "a turing value",
        "a_turing_list": [
            {
                "turing_id": "the turing id",
                "mathrace_id": "the mathrace id"
            }
        ],
        "mathrace_only": {
            "a_mathrace_attribute": "a mathrace value"
        }
    }
    strip_mathrace_only_attributes_from_imported_turing(imported_dict)
    expected_stripped_dict = {
        "a_turing_attribute": "a turing value",
        "a_turing_list": [
            {
                "turing_id": "the turing id"
            }
        ]
    }
    assert imported_dict == expected_stripped_dict
