# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.test_utils.get_journals_in_directory."""

import pathlib
import tempfile
import typing

from mathrace_interaction.test_utils.get_journals_in_directory import get_journals_in_directory

RuntimeErrorContainsFixtureType: typing.TypeAlias = typing.Callable[[typing.Callable[[], typing.Any], str], None]


def test_get_journals_in_directory_empty() -> None:
    """Test get_journals_in_directory on an empty directory."""
    with tempfile.TemporaryDirectory() as directory:
        assert len(get_journals_in_directory(pathlib.Path(directory))) == 0


def test_get_journals_in_directory_only_files() -> None:
    """Test get_journals_in_directory on a syntetic directory that only contains files."""
    with tempfile.TemporaryDirectory() as directory:
        directory_path = pathlib.Path(directory)
        pathlib.Path(directory_path / "file1.journal").touch()
        pathlib.Path(directory_path / "file2.journal").touch()
        pathlib.Path(directory_path / "file3.score").touch()
        assert len(get_journals_in_directory(pathlib.Path(directory))) == 2


def test_get_journals_in_directory_nested_directories() -> None:
    """Test get_journals_in_directory on a syntetic directory that contains nested directories."""
    with tempfile.TemporaryDirectory() as directory:
        directory_path = pathlib.Path(directory)
        (directory_path / "subdir1").mkdir()
        pathlib.Path(directory_path / "subdir1" / "file1.journal").touch()
        (directory_path / "subdir2").mkdir()
        pathlib.Path(directory_path / "subdir2" / "file2.journal").touch()
        pathlib.Path(directory_path / "file3.score").touch()
        assert len(get_journals_in_directory(pathlib.Path(directory))) == 2


def test_get_journals_in_directory_symbolic_link(runtime_error_contains: RuntimeErrorContainsFixtureType) -> None:
    """Test get_journals_in_directory on a syntetic directory that contains a symbolic link."""
    with tempfile.TemporaryDirectory() as directory:
        directory_path = pathlib.Path(directory)
        pathlib.Path(directory_path / "file1.journal").touch()
        pathlib.Path(directory_path / "file2.journal").symlink_to(pathlib.Path(directory_path / "file1.journal"))
        assert len(get_journals_in_directory(pathlib.Path(directory))) == 2
