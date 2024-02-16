# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test fixtures defined in conftest.py."""

import datetime
import sys
import typing

import _pytest
import pytest

from mathrace_interaction.turing_dict_type_alias import TuringDict

RuntimeErrorContainsFixtureType: typing.TypeAlias = typing.Callable[[typing.Callable[[], typing.Any], str], None]
RunEntrypointFixtureType: typing.TypeAlias = typing.Callable[[str, list[str]], tuple[str, str]]


def counter_incrementer(counter_variable: str) -> None:
    """Increment the counter store in a global variable."""
    current_value = getattr(sys.modules[__name__], counter_variable)
    setattr(sys.modules[__name__], counter_variable, current_value + 1)


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
journal_and_other_journal_counter = 0
journal_version_and_other_journal_version_counter = 0
journal_and_journal_version_and_other_journal_and_other_journal_version_counter = 0

journal_checker = fixture_checker("journal_counter", 10)
journal_version_checker = fixture_checker("journal_version_counter", 10)
journal_and_journal_version_checker = fixture_checker("journal_and_journal_version_counter", 10)
journal_and_other_journal_checker = fixture_checker("journal_and_other_journal_counter", 100)
journal_version_and_other_journal_version_checker = fixture_checker(
    "journal_version_and_other_journal_version_counter", 100)
journal_and_journal_version_and_other_journal_and_other_journal_version_checker = fixture_checker(
    "journal_and_journal_version_and_other_journal_and_other_journal_version_counter", 100)


def raise_runtime_error(error_text: str) -> None:
    """Raise a runtime error with the provided text."""
    raise RuntimeError(error_text)


def generate_journal_fixture_test(fixture_names: str) -> type:
    """Check the number of elements in a parametrization added as a fixture by pytest_generate_tests."""
    fixture_prefix = fixture_names.replace(",", "_and_")

    @pytest.mark.usefixtures(fixture_prefix + "_checker")
    class TestChecker:
        """
        Check the number of elements in a parametrization (internal implementation).

        The test is inside a class to ensure that the check is run only once after the last parametrization entry.
        """

        @pytest.mark.usefixtures(*fixture_names.split(","))
        def test_parametrized_fixture(self) -> None:
            """Check the number of elements in the provided parametrization."""
            counter_incrementer(fixture_prefix + "_counter")

    return TestChecker


class TestJournalChecker(generate_journal_fixture_test("journal")):  # type: ignore[misc]
    """Check the number of elements in the journal parametrization."""

class TestJournalVersionChecker(generate_journal_fixture_test("journal_version")):  # type: ignore[misc]
    """Check the number of elements in the journal_version parametrization."""


class TestJournalAndJournalVersionChecker(
    generate_journal_fixture_test("journal,journal_version")  # type: ignore[misc]
):
    """Check the number of elements in the (journal, journal_version) parametrization."""


class TestJournalAndOtherJournalChecker(
    generate_journal_fixture_test("journal,other_journal")  # type: ignore[misc]
):
    """Check the number of elements in the (journal, other_journal) parametrization."""


class TestJournalVersionAndOtherJournalVersionChecker(
    generate_journal_fixture_test("journal_version,other_journal_version")  # type: ignore[misc]
):
    """Check the number of elements in the (journal_version, other_journal_version) parametrization."""


class TestJournalAndJournalVersionAndOtherJournalAndOtherJournalVersionChecker(
    generate_journal_fixture_test("journal,journal_version,other_journal,other_journal_version")  # type: ignore[misc]
):
    """Check the number of elements in the 4-way journal and other_journal parametrization."""


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
