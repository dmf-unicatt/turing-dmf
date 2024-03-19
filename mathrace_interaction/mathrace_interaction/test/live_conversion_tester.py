# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tester for mathrace_interaction.live_journal_to_live_turing.LiveJournal."""

import abc
import datetime
import json
import pathlib
import tempfile
import types
import typing

import jsondiff

from mathrace_interaction.filter import LiveJournal, strip_mathrace_only_attributes_from_imported_turing
from mathrace_interaction.journal_reader import journal_reader
from mathrace_interaction.live_journal_to_live_turing import _clean_up_turing_dictionary, live_journal_to_live_turing
from mathrace_interaction.typing import TuringDict


class LiveConversionTester(abc.ABC):
    """
    Abstract tester for live conversion.

    Parameters
    ----------
    journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis.
        The I/O stream is typically generated by open().
    race_name
        Name of the race.
    race_date
        Date of the race.
    num_reads
        Maximum number of reads from the live journal.
    turing_models
        The python module containing the turing models Gara, Consegna and Jolly.

    Attributes
    ----------
    _journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis, provided as input.
    _race_name
        Name of the race, provided as input.
    _race_date
        Date of the race, provided as input.
    _num_reads
        Maximum number of reads from the live journal, provided as input.
    _live_journal
        LiveJournal instance built from the input arguments journal_stream and num_reads.
    _turing_models
        The python module containing the turing models Gara, Consegna and Jolly, provided as input.
    _time_counter
        Time counter as in LiveJournal
    """

    def __init__(
        self, journal_stream: typing.TextIO, race_name: str, race_date: datetime.datetime,
        num_reads: int, turing_models: types.ModuleType
    ) -> None:
        # Assign input arguments
        self._journal_stream = journal_stream
        self._race_name = race_name
        self._race_date = race_date
        self._num_reads = num_reads
        self._turing_models = turing_models
        # Construct live journal and a failure in the middle of the run
        self._live_journal = LiveJournal(journal_stream, num_reads)
        self._time_counter_failure = num_reads // 2
        # Time counter as in LiveJournal
        self._time_counter = 0

    def run(self) -> TuringDict:
        """Run a test session, and return the final turing dictionary."""
        # Convert the provided journal into a turing dictionary, and strip away all events
        with journal_reader(self._journal_stream) as journal_to_turing:
            turing_dict = journal_to_turing.read(self._race_name, self._race_date)
        strip_mathrace_only_attributes_from_imported_turing(turing_dict)
        turing_dict["eventi"].clear()
        # Register a new race in turing
        Gara = getattr(self._turing_models, "Gara")  # noqa: N806
        turing_race = Gara.create_from_dict(turing_dict)
        turing_race.save()
        # Run test
        with tempfile.TemporaryDirectory() as output_directory:
            output_directory_path = pathlib.Path(output_directory)
            output_subdirectory_path = {
                "journal": output_directory_path / "live_journal_files",
                "json": output_directory_path / "live_turing_json_files"
            }
            while self._live_journal.can_read():
                self._run(turing_race.pk, output_directory_path)
                time_counter = self._time_counter
                # Ensure that the expected journal and json files have been written at every intermediate time
                for extension in ("journal", "json"):
                    written_files = [f for f in output_subdirectory_path[extension].glob(f"*.{extension}")]
                    assert len(written_files) == time_counter + 1  # + 1 because of latest file
                    assert {f.name for f in written_files} == {
                        f"{t}.{extension}" for t in range(time_counter)}.union({f"latest.{extension}"})
                # Ensure that the json file contains the turing dictionary associated to the corresponding journal
                # for every intermediate file
                for t in range(time_counter):
                    with journal_reader(
                        open(output_subdirectory_path["journal"] / f"{t}.journal")
                    ) as journal_to_turing:
                        turing_dict = journal_to_turing.read(self._race_name, self._race_date)
                        _clean_up_turing_dictionary(turing_dict)
                    if (output_subdirectory_path["journal"] / f"{t}.journal.needs_to_clear_events").exists():
                        turing_dict["eventi"].clear()
                    with open(output_subdirectory_path["json"] / f"{t}.json") as turing_json_file:
                        expected_turing_dict = json.load(turing_json_file)
                    _clean_up_turing_dictionary(turing_dict)
                    assert turing_dict == expected_turing_dict, (
                        "Dictionaries are different: "
                        f'{jsondiff.diff(turing_dict, expected_turing_dict, syntax="symmetric")}')
                # Ensure that the live turing Gara object contains the same data as the json at the final time
                # (we can't do the same check for intermediate times because we do not save intermediate states
                # of turing_race)
                with open(output_subdirectory_path["json"] / f"{time_counter - 1}.json") as turing_json_file:
                    expected_turing_dict = json.load(turing_json_file)
                _clean_up_turing_dictionary(expected_turing_dict)
                turing_race_dict = turing_race.to_dict()
                _clean_up_turing_dictionary(turing_race_dict)
                assert turing_race_dict == expected_turing_dict, (
                        "Dictionaries are different: "
                        f'{jsondiff.diff(turing_race_dict, expected_turing_dict, syntax="symmetric")}')
                # The next run should not be modifying files which have already been written. To ensure that
                # no modification actually occurs mark the files as read-only
                for extension in ("journal", "json"):
                    for t in range(time_counter):
                        (output_subdirectory_path[extension] / f"{t}.{extension}").chmod(0o444)

        # Return the content of the Gara object
        turing_race_dict = turing_race.to_dict()
        _clean_up_turing_dictionary(turing_race_dict)
        return turing_race_dict  # type: ignore[no-any-return]

    @abc.abstractmethod
    def _run(self, turing_race_id: int, output_directory_path: pathlib.Path) -> None:
        """Run a single iteration of the test session."""
        pass  # pragma: no cover

    def _open(self) -> typing.TextIO:
        """Open a journal file, or fail."""
        self._time_counter += 1
        return self._live_journal.open()


class LiveJournalToLiveTuringTester(LiveConversionTester):
    """Tester for mathrace_interaction.live_journal_to_live_turing."""

    def _run(self, turing_race_id: int, output_directory_path: pathlib.Path) -> None:
        """Run a single iteration of the test session."""
        live_journal_to_live_turing(
            self._open, self._turing_models, turing_race_id, 0.0, output_directory_path,
            self._termination_condition)

    def _termination_condition(self, time_counter: int, race_ended: bool) -> bool:
        """Termination condition for live_journal_to_live_turing."""
        if time_counter == self._time_counter_failure:
            print(f"\tTerminating because of mock failure at {self._time_counter_failure}")
            return True
        elif race_ended:
            print("\tTerminating because race ended")
            return True
        else:
            return False
