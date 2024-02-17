# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.utils.convert_timestamp_to_number_of_seconds."""

from mathrace_interaction.utils.convert_timestamp_to_number_of_seconds import convert_timestamp_to_number_of_seconds


def test_convert_timestamp_to_number_of_seconds() -> None:
    """Test convert_timestamp_to_number_of_seconds in a few cases."""
    assert convert_timestamp_to_number_of_seconds("1") == 1
    assert convert_timestamp_to_number_of_seconds("1:2") == 62
    assert convert_timestamp_to_number_of_seconds("1:2:3") == 3723
    assert convert_timestamp_to_number_of_seconds("1:2:3.45678") == 3723  # decimals are discarded
