# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test fixtures defined in conftest.py."""

import datetime
import typing

import _pytest
import pytest

from mathrace_interaction.turing_dict_type_alias import TuringDict

RuntimeErrorContainsFixtureType: typing.TypeAlias = typing.Callable[[typing.Callable[[], typing.Any], str], None]
RunEntrypointFixtureType: typing.TypeAlias = typing.Callable[[str, list[str]], tuple[str, str]]


def raise_runtime_error(error_text: str) -> None:
    """Raise a runtime error with the provided text."""
    raise RuntimeError(error_text)


def test_race_name_fixture(race_name: str) -> None:
    """Test the race_name fixture."""
    assert race_name == "sample_journal"


def test_race_date_fixture(race_date: datetime.datetime) -> None:
    """Test the race_name fixture."""
    assert race_date.isoformat() == "2000-01-01T00:00:00+00:00"


def test_turing_dict_fixture(turing_dict: TuringDict, race_name: str, race_date: datetime.datetime) -> None:
    """Test the turing_dict fixture."""
    assert turing_dict["nome"] == race_name
    assert turing_dict["inizio"] == race_date.isoformat()


def test_runtime_error_contains_with_correct_error(runtime_error_contains: RuntimeErrorContainsFixtureType) -> None:
    """Test the runtime_error_contains fixture when the function to be called actually raises the correct error."""
    runtime_error_contains(
        lambda: raise_runtime_error("test_runtime_error_contains_with_error raised"),
        "test_runtime_error_contains_with_error raised")


def test_runtime_error_contains_with_wrong_error(runtime_error_contains: RuntimeErrorContainsFixtureType) -> None:
    """Test the runtime_error_contains fixture when the function to be called actually raises the wrong error."""
    with pytest.raises(AssertionError) as excinfo:
        runtime_error_contains(
            lambda: raise_runtime_error("test_runtime_error_contains_with_wrong_error raised"),
            "test_runtime_error_contains_with_wrong_error NOT raised")
    assertion_error_text = str(excinfo.value)
    assert assertion_error_text == (
        "assert 'test_runtime_error_contains_with_wrong_error NOT raised' in "
        "'test_runtime_error_contains_with_wrong_error raised'")


def test_runtime_error_contains_without_error(runtime_error_contains: RuntimeErrorContainsFixtureType) -> None:
    """Test the runtime_error_contains fixture when the function to be called raises no error."""
    with pytest.raises(_pytest.outcomes.Failed) as excinfo:
        runtime_error_contains(lambda: None, "test_runtime_error_contains_without_error raised")
    pytest_error_text = str(excinfo.value)
    assert pytest_error_text == "DID NOT RAISE <class 'RuntimeError'>"


def test_run_entrypoint_with_hello_world(run_entrypoint: RunEntrypointFixtureType) -> None:
    """Test the run_entrypoint by running python3 -m __hello__."""
    stdout, stderr = run_entrypoint("__hello__", [])
    assert "Hello world!" in stdout
    assert stderr == ""


def test_run_entrypoint_with_base64_correct_flag(run_entrypoint: RunEntrypointFixtureType) -> None:
    """Test the run_entrypoint by running python3 -m base64 -t."""
    stdout, stderr = run_entrypoint("base64", ["-t"])
    assert "Aladdin:open sesame" in stdout
    assert stderr == ""


def test_run_entrypoint_with_base64_wrong_flag(
    run_entrypoint: RunEntrypointFixtureType, runtime_error_contains: RuntimeErrorContainsFixtureType
) -> None:
    """Test the run_entrypoint by running python3 -m base64 with a wrong flag."""
    runtime_error_contains(
        lambda: run_entrypoint("base64", ["-t", "--wrong-flag2"]),
        "Running base64 with arguments ['-t', '--wrong-flag2'] failed with exit code 2, stdout , "
        "stderr option --wrong-flag2 not recognized")
