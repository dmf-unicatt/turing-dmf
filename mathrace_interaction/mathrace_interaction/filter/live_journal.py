# Copyright (C) 2024-2025 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Reader of a journal which gets updated between one read and the next."""

import io
import typing


class LiveJournal:
    """
    Reader of a journal which gets updated between one read and the next.

    Parameters
    ----------
    journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis.
        The I/O stream is typically generated by open().
    max_open_calls
        Maximum number of calls that that open() function will receive.

    Attributes
    ----------
    _journal
        The content of the journal generated by mathrace or simdis.
    _up_to_line
        A list of integers which contains at the i-th position the index of the final line that will
        be included in the i-th call to open. The list has size max_open_calls.
    _counter
        Counter of the number of times the open function was called.
    """

    def __init__(self, journal_stream: typing.TextIO, max_open_calls: int) -> None:
        # Read journal stream
        journal = [line.strip("\n") for line in journal_stream]
        journal_stream.seek(0)
        # Determine the first line that does not start with ---, and the final line --- 999
        race_begin_line = None
        file_end_line = None
        for (line_counter, line) in enumerate(journal):
            if not line.startswith("---") and not line.startswith("#") and race_begin_line is None:
                race_begin_line = line_counter
            elif line.startswith("--- 999"):
                assert file_end_line is None
                file_end_line = line_counter
        assert race_begin_line is not None
        assert file_end_line is not None
        # Assign attributes
        self._journal = journal
        if max_open_calls > 1:
            self._up_to_line = [
                race_begin_line + int(i / (max_open_calls - 1) * (file_end_line - race_begin_line))
                for i in range(max_open_calls)]
        else:
            self._up_to_line = [file_end_line]
        self._counter = 0

    def open(self) -> typing.TextIO:
        """
        Open the journal and increase the counter.

        Returns
        -------
        :
            A stream into part of the journal, up to the line corresponding to the current value of
            the internal counter.
        """
        if self.can_read():
            up_to_line = self._journal[:self._up_to_line[self._counter]]
            up_to_line.append("--- 999 fine simulatore")
            self._counter += 1
            return io.StringIO("\n".join(up_to_line))
        else:
            raise RuntimeError("Journal was fully read already")

    def can_read(self) -> bool:
        """Return if the journal can still be read, or if was fully read already."""
        return self._counter < len(self._up_to_line)
