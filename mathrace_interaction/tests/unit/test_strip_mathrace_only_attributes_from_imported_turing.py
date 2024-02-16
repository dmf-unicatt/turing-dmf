# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.determine_journal_version."""

import json
import tempfile
import typing

import pytest

from mathrace_interaction.strip_mathrace_only_attributes_from_imported_turing import (
    strip_mathrace_only_attributes_from_imported_turing)
from mathrace_interaction.turing_dict_type_alias import TuringDict

RunEntrypointFixtureType: typing.TypeAlias = typing.Callable[[str, list[str]], tuple[str, str]]


@pytest.fixture
def imported_dict() -> TuringDict:
    """Return a dictionary that mimicks the output of journal_read due to the presence of some mathrace attributes."""
    return {
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


@pytest.fixture
def expected_stripped_dict() -> TuringDict:
    """Return the expected dictionary after stripping mathrace attributes from imported_dict."""
    return {
        "a_turing_attribute": "a turing value",
        "a_turing_list": [
            {
                "turing_id": "the turing id"
            }
        ]
    }


def test_strip_mathrace_only_attributes_from_imported_turing(
    imported_dict: TuringDict, expected_stripped_dict: TuringDict
) -> None:
    """Test strip_mathrace_only_attributes_from_imported_turing."""
    strip_mathrace_only_attributes_from_imported_turing(imported_dict)
    assert imported_dict == expected_stripped_dict


@pytest.mark.parametrize("input_file_option,output_file_option", [("-i", "-o"), ("--input-file", "--output-file")])
def test_strip_mathrace_only_attributes_from_imported_turing_entrypoint(
    imported_dict: TuringDict, expected_stripped_dict: TuringDict, run_entrypoint: RunEntrypointFixtureType,
    input_file_option: str, output_file_option: str
) -> None:
    """Test running strip_mathrace_only_attributes_from_imported_turing as entrypoint."""
    with tempfile.NamedTemporaryFile() as input_json_file, tempfile.NamedTemporaryFile() as output_json_file:
        with open(input_json_file.name, "w") as input_json_stream:
            input_json_stream.write(json.dumps(imported_dict))
        stdout, stderr = run_entrypoint(
            "mathrace_interaction.strip_mathrace_only_attributes_from_imported_turing", [
                input_file_option, input_json_file.name, output_file_option, output_json_file.name
            ]
        )
        assert stdout == ""
        assert stderr == ""
        with open(output_json_file.name) as output_json_stream:
            imported_dict = json.load(output_json_stream)
        assert imported_dict == expected_stripped_dict
