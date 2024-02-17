# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Remove all comments and events not handled by turing from a mathrace journal file."""

import argparse
import sys
import typing

from mathrace_interaction.determine_journal_version import determine_journal_version
from mathrace_interaction.journal_reader import AbstractJournalReader


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
    # Determine the version of the mathrace journal
    version = determine_journal_version(journal_stream)
    # The previous call has consumed the stream: reset it back to the beginning
    journal_stream.seek(0)
    # Determine the journal reader class corresponding to the detected version
    journal_reader_class = getattr(
        sys.modules["mathrace_interaction.journal_reader"], f"JournalReader{version.capitalize()}")
    # Process the stream, stripping any unnecessary line
    return "\n".join([
        line.strip("\n") for line in journal_stream.readlines()
        if not _is_comment(line) and not _is_unhandled_event(line, journal_reader_class)
    ])


def _is_comment(line: str) -> bool:
    """Determine if a line is a comment."""
    return line.startswith("#")


def _is_unhandled_event(line: str, journal_reader_class: type[AbstractJournalReader]) -> bool:
    """Determine if a line is associated to an unhandled event."""
    if line.startswith("---"):
        # Race setup is not a race event, so it surely is not an unhandled event
        return False
    else:
        _, event_type, _ = line.split(" ", maxsplit=2)
        blacklist = [
            journal_reader_class.JOLLY_TIMEOUT, journal_reader_class.TIMER_UPDATE, journal_reader_class.MANUAL_BONUS,
            journal_reader_class.RACE_SUSPENDED, journal_reader_class.RACE_RESUMED,
        ]
        if hasattr(journal_reader_class, "TIMER_UPDATE_OTHER_TIMER"):
            blacklist.append(journal_reader_class.TIMER_UPDATE_OTHER_TIMER)
        return event_type in blacklist


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, required=True, help="Path of the input journal file")
    parser.add_argument("-o", "--output-file", type=str, required=True, help="Path of the output journal file")
    args = parser.parse_args()
    with open(args.input_file) as input_journal_stream:
        output_journal = strip_comments_and_unhandled_events_from_journal(input_journal_stream)
    with open(args.output_file, "w") as output_journal_stream:
        output_journal_stream.write(output_journal)