# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Convert a mathrace journal file from a version to another."""

import argparse
import datetime
import io
import typing

from mathrace_interaction.journal_reader import journal_reader
from mathrace_interaction.journal_writer import journal_writer


def journal_version_converter(input_journal_stream: typing.TextIO, output_journal_version: str) -> str:
    """
    Convert a mathrace journal file from a version to another.

    Parameters
    ----------
    input_journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis.
        The I/O stream is typically generated by open().
    output_journal_version
        The version of the mathrace journal to be written.

    Returns
    -------
    :
        The content of a journal which is equivalent to the input one, and is also compatible with
        the required output version.
    """
    # Prepare a mock race name and race date, since they are actually not relevant
    race_name = "journal_version_converter"
    race_date = datetime.datetime.now()
    # Convert the input journal into a turing dictionary
    # We avoid using "with journal_reader(input_journal_stream) as journal_reader_stream" because
    # otherwise this function would close the input journal stream
    journal_reader_stream = journal_reader(input_journal_stream)
    imported_dict = journal_reader_stream.read(race_name, race_date)
    # Process the stream, stripping any unnecessary line
    with (
        io.StringIO("") as output_journal_stream,
        journal_writer(output_journal_stream, output_journal_version) as journal_writer_stream
    ):
        journal_writer_stream.write(imported_dict)
        return output_journal_stream.getvalue()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, required=True, help="Path of the input journal file")
    parser.add_argument("-o", "--output-file", type=str, required=True, help="Path of the output journal file")
    parser.add_argument("-v", "--journal-version", type=str, required=True, help="Version of the output journal file")
    args = parser.parse_args()
    with open(args.input_file) as input_journal_stream:
        output_journal = journal_version_converter(input_journal_stream, args.journal_version)
    with open(args.output_file, "w") as output_journal_stream:
        output_journal_stream.write(output_journal)
