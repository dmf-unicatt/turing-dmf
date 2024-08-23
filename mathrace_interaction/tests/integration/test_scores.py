# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test that the final race scores are equal to the expected ones."""

import datetime
import json
import os
import pathlib
import typing

import engine.models
import pytest_django.live_server_helper

import mathrace_interaction
import mathrace_interaction.filter
import mathrace_interaction.network
import mathrace_interaction.typing


def test_journal_scores(
    journal: typing.TextIO, journal_name: str, data_dir: pathlib.Path,
    live_server: pytest_django.live_server_helper.LiveServer,
    read_score_file: mathrace_interaction.typing.ReadScoreFileFixtureType
) -> None:
    """Test that the final race scores are equal to the expected ones (journal files)."""
    # Import the journal into turing via journal_reader
    journal_year, _ = journal_name.split(os.sep, maxsplit=1)
    journal_date = datetime.datetime(int(journal_year), 1, 1, tzinfo=datetime.UTC)
    with mathrace_interaction.journal_reader(journal) as journal_stream:
        turing_dict = journal_stream.read(journal_name, journal_date)
    mathrace_interaction.filter.strip_mathrace_only_attributes_from_imported_turing(turing_dict)
    mathrace_interaction.filter.strip_trailing_zero_bonus_superbonus_from_imported_turing(turing_dict)
    gara = engine.models.Gara.create_from_dict(turing_dict)
    # Open a browser and get the computed scores
    browser = mathrace_interaction.network.TuringClassificationSelenium(live_server.url, gara.pk, 10)
    browser.go_to_classification_page("squadre", {})
    browser.lock()
    actual = browser.get_teams_score()
    # Compare the computed scores to the expected ones
    expected = read_score_file(data_dir, journal_name)
    assert actual == expected


def test_json_scores(
    json_name: str, data_dir: pathlib.Path, live_server: pytest_django.live_server_helper.LiveServer,
    read_score_file: mathrace_interaction.typing.ReadScoreFileFixtureType
) -> None:
    """Test that the final race scores are equal to the expected ones (json files)."""
    # Import the json file into turing
    with open(data_dir / json_name) as json_stream:
        turing_dict = json.load(json_stream)
    gara = engine.models.Gara.create_from_dict(turing_dict)
    # Open a browser and get the computed scores
    browser = mathrace_interaction.network.TuringClassificationSelenium(live_server.url, gara.pk, 10)
    browser.go_to_classification_page("squadre", {})
    browser.lock()
    actual = browser.get_teams_score()
    # Compare the computed scores to the expected ones
    expected = read_score_file(data_dir, json_name)
    assert actual == expected
