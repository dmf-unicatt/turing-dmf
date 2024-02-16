# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test fixtures defined in conftest.py."""

import datetime
import io
import sys
import typing

import _pytest
import pytest

from mathrace_interaction.turing_dict_type_alias import TuringDict

RuntimeErrorContainsFixtureType: typing.TypeAlias = typing.Callable[[typing.Callable[[], typing.Any], str], None]
RunEntrypointFixtureType: typing.TypeAlias = typing.Callable[[str, list[str]], tuple[str, str]]


def counter_checker(counter_variable: str, expected_value: int) -> typing.Callable[[], None]:
    """Ensure that a variable contains the expected value."""
    def _() -> None:
        """Ensure that a variable contains the expected value (internal implementation)."""
        assert getattr(sys.modules[__name__], counter_variable) == expected_value

    return _


def fixture_checker(
    counter_variable: str, expected_value: int
) -> typing.Callable[[_pytest.fixtures.SubRequest], None]:
    """Return a class fixture to check the counter at the end of the parametrization."""
    @pytest.fixture(scope="class")
    def _(request: _pytest.fixtures.SubRequest) -> None:
        """Return a class fixture to check the counter at the end of the parametrization (internal implementation)."""
        request.addfinalizer(counter_checker(counter_variable, expected_value))

    return _

journal_counter = 0
journal_version_counter = 0
journal_and_journal_version_counter = 0

journal_checker = fixture_checker("journal_counter", 10)
journal_version_checker = fixture_checker("journal_version_counter", 10)
journal_and_journal_version_checker = fixture_checker("journal_and_journal_version_counter", 10)


def raise_runtime_error(error_text: str) -> None:
    """Raise a runtime error with the provided text."""
    raise RuntimeError(error_text)


@pytest.mark.usefixtures("journal_checker")
class TestJournalChecker:
    """
    Check the number of elements in the journal parametrization.

    The test is inside a class to ensure that journal_checker is run only once after the last parametrization entry.
    """

    def test_journal_fixture(self, journal: io.StringIO) -> None:
        """Check the number of elements in the journal parametrization."""
        global journal_counter
        journal_counter += 1


@pytest.mark.usefixtures("journal_version_checker")
class TestJournalVersionChecker:
    """
    Check the number of elements in the journal version parametrization.

    The rationale for using a class is the same as in TestJournalChecker.
    """

    def test_journal_version_fixture(self, journal_version: str) -> None:
        """Check the number of elements in the journal version parametrization."""
        global journal_version_counter
        journal_version_counter += 1


@pytest.mark.usefixtures("journal_and_journal_version_checker")
class TestJournalAndJournalVersionChecker:
    """
    Check the number of elements in the (journal, journal version) parametrization.

    The rationale for using a class is the same as in TestJournalChecker.
    """

    def test_journal_version_fixture(self, journal: io.StringIO, journal_version: str) -> None:
        """Check the number of elements in the (journal, journal version) parametrization."""
        global journal_and_journal_version_counter
        journal_and_journal_version_counter += 1


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
