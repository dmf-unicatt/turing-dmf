# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Abstract journal reader class."""

import abc
import datetime
import types
import typing

from mathrace_interaction.typing import TuringDict


class AbstractJournalReader(abc.ABC):
    """
    An abstract class representing a reader of a mathrace journal.

    Parameters
    ----------
    journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis.
        The I/O stream is typically generated by open().

    Attributes
    ----------
    _journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis, provided as input.
    """

    # Race setup codes
    RACE_DEFINITION = ""  #: str: The race setup code associated to the race definition
    QUESTION_DEFINITION = ""  #: str: The race setup code associated to the question definition

    # Race event codes
    RACE_START = ""  #: str: The race event code associated to the start of the race
    JOLLY_SELECTION = ""  #: str: The race event code associated to jolly selection by a team
    ANSWER_SUBMISSION = ""  #: str: The race event code associated to answer submission by a team
    JOLLY_TIMEOUT = ""  #: str: The race event code associated to jolly timeout
    TIMER_UPDATE = ""  #: str: The race event code associated to a timer update
    RACE_SUSPENDED = ""  #: str: The race event code associated to a race suspension
    RACE_RESUMED = ""  #: str: The race event code associated to a race resumption
    RACE_END = ""  #: str: The race event code associated to the end of the race
    MANUAL_BONUS = ""  #: str: The race event code associated to the manual addition of a bonus

    def __init__(self, journal_stream: typing.TextIO) -> None:
        self._journal_stream = journal_stream

    def __enter__(self) -> typing.Self:
        """Enter the journal I/O stream context."""
        return self

    def __exit__(
        self, exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: types.TracebackType | None
    ) -> None:
        """Exit the journal I/O stream context."""
        self._journal_stream.__exit__(exception_type, exception_value, traceback)

    def read(self, race_name: str, race_date: datetime.datetime) -> TuringDict:
        """
        Read the mathrace journal, and convert it into a dictionary compatible with turing.

        Parameters
        ----------
        race_name
            Name of the race.
        race_date
            Date of the race.

        Returns
        -------
        :
            The turing dictionary representing the race.
        """
        # Prepare a dictionary to store the output
        turing_dict: TuringDict = dict()

        # Prepare a further dictionary for fields which are collected by mathrace, but not read in by turing
        turing_dict["mathrace_only"] = dict()

        # Set name and date
        turing_dict["nome"] = race_name
        turing_dict["inizio"] = race_date.isoformat()

        # The first line must contain the initialization of the file
        first_line = self._read_line()
        if first_line != "--- 001 inizializzazione simulatore":
            raise RuntimeError(f"Invalid first line {first_line}")
        del first_line

        # The second section contains the definition of the race
        self._read_race_definition_section(turing_dict)

        # The third section contains the definition of the questions
        self._read_questions_definition_section(turing_dict)

        # The fourth section contains the definition of the teams
        self._read_teams_definition_section(turing_dict)

        # The fifth section contains all race events
        self._read_race_events_section(turing_dict)

        # The final line must contain the finalization of the file
        final_line = self._read_line()
        if final_line != "--- 999 fine simulatore":
            raise RuntimeError(f"Invalid final line {final_line}")
        del final_line

        # There must be no further lines in the stream
        try:
            extra_line = self._read_line()
        except StopIteration:
            pass
        else:
            raise RuntimeError(f"Journal contains extra line {extra_line} after race end")

        # Return the populated dictionary
        return turing_dict

    def _read_line(self) -> str:
        """Read one line from the journal stream."""
        line, _, _ = self._read_line_with_positions()
        return line

    def _read_line_with_positions(self) -> tuple[str, int, int]:
        """Read one line from the journal stream, returning the stream positions before and after the operation."""
        stream = self._journal_stream
        assert stream is not None
        before = stream.tell()
        line = "#"  # mock line to start the while loop
        while line.startswith("#"):
            line = stream.readline()
        if len(line) == 0:
            raise StopIteration()
        else:
            return line.strip("\n"), before, stream.tell()

    def _reset_stream_to_position(self, position: int) -> None:
        """Reset stream to a specific position."""
        stream = self._journal_stream
        assert stream is not None
        stream.seek(position)

    @abc.abstractmethod
    def _read_race_definition_section(self, turing_dict: TuringDict) -> None:
        """Read the race definition section."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _read_questions_definition_section(self, turing_dict: TuringDict) -> None:
        """Read the questions definition section."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _read_teams_definition_section(self, turing_dict: TuringDict) -> None:
        """Read the teams definition section."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _read_race_events_section(self, turing_dict: TuringDict) -> None:
        """Read all race events."""
        pass  # pragma: no cover
