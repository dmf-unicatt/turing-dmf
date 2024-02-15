# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Strip attributes marked as mathrace only from an imported turing dict."""

from mathrace_interaction.journal_reader import TuringDict


def strip_mathrace_only_attributes_from_imported_turing(imported_dict: TuringDict) -> None:
    """
    Strip attributes marked as mathrace only from an imported turing dict.

    The dictionary is modified in-place.

    Parameters
    ----------
    imported_dict
        The turing dictionary representing the race, imported from a mathrace journal.
    """
    if "mathrace_only" in imported_dict:
        del imported_dict["mathrace_only"]
    if "mathrace_id" in imported_dict:
        del imported_dict["mathrace_id"]
    for value in imported_dict.values():
        if isinstance(value, list):
            for value_entry in value:
                assert isinstance(value_entry, dict)
                strip_mathrace_only_attributes_from_imported_turing(value_entry)
