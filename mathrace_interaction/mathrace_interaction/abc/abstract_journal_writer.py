# Copyright (C) 2024-2025 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Abstract journal writer class."""

import abc
import datetime
import types
import typing

from mathrace_interaction.typing import TuringDict


class AbstractJournalWriter(abc.ABC):
    """
    An abstract class representing a writer of a mathrace journal.

    Parameters
    ----------
    journal_stream
        The I/O stream that writes the journal to be read by mathrace or simdis.
        The I/O stream is typically generated by open().

    Attributes
    ----------
    _journal_stream
        The I/O stream that writes the journal to be read by mathrace or simdis, provided as input.
    _last_event_datetime
        Time of the last processed event to ensure that events are correctly sorted.
    """

    # Race setup codes
    RACE_DEFINITION = ""  #: str: The race setup code associated to the race definition.
    QUESTION_DEFINITION = ""  #: str: The race setup code associated to the question definition.

    # Race event codes
    RACE_START = ""  #: str: The race event code associated to the start of the race.
    JOLLY_SELECTION = ""  #: str: The race event code associated to jolly selection by a team.
    ANSWER_SUBMISSION = ""  #: str: The race event code associated to answer submission by a team.
    RACE_END = ""  #: str: The race event code associated to the end of the race.

    def __init__(self, journal_stream: typing.TextIO) -> None:
        self._journal_stream = journal_stream
        self._last_event_datetime: datetime.datetime | None = None

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

    def write(self, turing_dict: TuringDict) -> None:
        """
        Write a turing dictionary to the mathrace journal.

        Parameters
        ----------
        turing_dict
            The turing dictionary representing the race.
        """
        # The first line contains the initialization of the file
        self._write_line("--- 001 inizializzazione simulatore")

        # The second section contains the definition of the race
        self._write_race_definition_section(turing_dict)

        # The third section contains the definition of the questions
        self._write_questions_definition_section(turing_dict)

        # The fourth section contains the definition of the teams
        self._write_teams_definition_section(turing_dict)

        # The fifth section contains all race events
        if turing_dict["inizio"] is not None:
            self._last_event_datetime = datetime.datetime.fromisoformat(turing_dict["inizio"])
            self._write_race_events_section(turing_dict)
        else:
            # If the race start date is missing, it means that the race has not started yet.
            # Hence, there must be no events yet.
            if len(turing_dict["eventi"]) > 0:
                raise RuntimeError(f"Race has not started, yet there are {len(turing_dict['eventi'])} events")

        # The final line contains the finalization of the file
        self._write_line("--- 999 fine simulatore")

    def _write_line(self, line: str) -> None:
        """Write one line to the journal stream."""
        stream = self._journal_stream
        assert stream is not None
        print(line, file=stream)

    @abc.abstractmethod
    def _write_race_definition_section(self, turing_dict: TuringDict) -> None:
        """Write the race definition section."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _write_questions_definition_section(self, turing_dict: TuringDict) -> None:
        """Write the questions definition section."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _write_teams_definition_section(self, turing_dict: TuringDict) -> None:
        """Write the teams definition section."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _write_race_events_section(self, turing_dict: TuringDict) -> None:
        """Write all race events."""
        pass  # pragma: no cover
