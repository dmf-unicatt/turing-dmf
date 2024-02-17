# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Remove all comments and events not handled by turing from a mathrace journal file."""

import argparse
import typing

from mathrace_interaction.journal_reader import AbstractJournalReader
from mathrace_interaction.utils.journal_event_filterer import journal_event_filterer


def strip_comments_and_unhandled_events_from_journal(journal_stream: typing.TextIO) -> str:
    """
    Remove all comments and events not handled by turing from a mathrace journal file.

    Parameters
    ----------
    journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis.
        The I/O stream is typically generated by open().

    Returns
    -------
    :
        A string representing the stripped journal.
    """
    return journal_event_filterer(journal_stream, _is_handled_event)


def _is_handled_event(timestamp: str, event_type: str, journal_reader_class: type[AbstractJournalReader]) -> bool:
    """Determine if a line is associated to an handled event."""
    blacklist = [
        journal_reader_class.JOLLY_TIMEOUT, journal_reader_class.TIMER_UPDATE, journal_reader_class.MANUAL_BONUS,
        journal_reader_class.RACE_SUSPENDED, journal_reader_class.RACE_RESUMED,
    ]
    if hasattr(journal_reader_class, "TIMER_UPDATE_OTHER_TIMER"):
        blacklist.append(journal_reader_class.TIMER_UPDATE_OTHER_TIMER)
    return event_type not in blacklist


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, required=True, help="Path of the input journal file")
    parser.add_argument("-o", "--output-file", type=str, required=True, help="Path of the output journal file")
    args = parser.parse_args()
    with open(args.input_file) as input_journal_stream:
        output_journal = strip_comments_and_unhandled_events_from_journal(input_journal_stream)
    with open(args.output_file, "w") as output_journal_stream:
        output_journal_stream.write(output_journal)