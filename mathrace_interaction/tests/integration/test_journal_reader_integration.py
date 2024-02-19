# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test that the files produced by journal_reader can be imported into turing."""

import copy
import datetime
import json
import os
import typing

import engine.models
import jsondiff
import pytest

import mathrace_interaction
import mathrace_interaction.filter
import mathrace_interaction.typing


def assert_gara_model_equal_to_turing_dict(  # type: ignore[no-any-unimported]
    gara: engine.models.Gara, turing_dict: mathrace_interaction.typing.TuringDict
) -> None:
    """Assert that the Gara object is the same as a converted dict and, if not, print their difference."""
    # Serialize the internal Gara representation
    gara_dict = json.loads(json.dumps(gara, default=engine.models.Gara.serialize))
    # List attributes may be ordered differently in the two dictionaries
    turing_dict_copy = copy.deepcopy(turing_dict)
    for dict_ in (gara_dict, turing_dict_copy):
        dict_["eventi"] = sorted(dict_["eventi"], key=lambda e: (
            e["orario"], e["subclass"], e["squadra_id"], e["problema"]))
        dict_["soluzioni"] = sorted(dict_["soluzioni"], key=lambda e: e["problema"])
        dict_["squadre"] = sorted(dict_["squadre"], key=lambda e: e["num"])
    # Compute the difference
    diff = jsondiff.diff(gara_dict, turing_dict_copy, syntax="symmetric")
    assert diff == {}

@pytest.mark.django_db
def test_journal_reader_integration(journal: typing.TextIO, journal_name: str) -> None:
    """Test that journal_reader can import journals in the data directory."""
    journal_year, _ = journal_name.split(os.sep, maxsplit=1)
    journal_date = datetime.datetime(int(journal_year), 1, 1, tzinfo=datetime.UTC)
    with mathrace_interaction.journal_reader(journal) as journal_stream:
        turing_dict = journal_stream.read(journal_name, journal_date)
    mathrace_interaction.filter.strip_mathrace_only_attributes_from_imported_turing(turing_dict)
    # Need to make a copy of the input dictionary because engine.models.Gara.create_from_dict
    # has side effects that modify the input dictionary
    gara = engine.models.Gara.create_from_dict(copy.deepcopy(turing_dict))
    assert_gara_model_equal_to_turing_dict(gara, turing_dict)
