# Copyright (C) 2024-2025 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Determine the version of a mathrace journal."""

import argparse
import typing

from mathrace_interaction.list_journal_versions import list_journal_versions


def determine_journal_version(journal_stream: typing.TextIO) -> str:
    """
    Determine the version of a mathrace journal.

    Parameters
    ----------
    journal_stream
        The I/O stream that reads the journal generated by mathrace or simdis.
        The I/O stream is typically generated by open().

    Returns
    -------
    :
        A string representing the earliest compatible version.
    """
    journal = [line.strip("\n") for line in journal_stream.readlines()]

    # The stream was fully consumed by the previous line: reset it back to the beginning in case
    # the caller wants to use the same stream elsewhere.
    journal_stream.seek(0)

    # Raise an error on the trivial case in which the journal is empty
    if "".join(journal) == "":
        raise RuntimeError("The provided journal is empty")

    # If the file has no race start event, than the only way we can differentiate from one format
    # to the other is using race setup codes.
    if (
        not _has_line_matching_condition(journal, lambda line: "002 inizio gara" in line) and
        not _has_line_matching_condition(journal, lambda line: "200 inizio gara" in line)
    ):
        if not all(line.startswith("---") or line.startswith("#") for line in journal):
            raise RuntimeError("The file contains race events, but not race start was detected")

    # Since all versions after the fallback one use the event code 200 for the race start,
    # a journal containing the code 002 is a fallback journal. Note that the condition for checking
    # event code 002 operates on the entire line, since event code 002 certainly uses integer timestamps.
    # Instead, event code 200 may operate on either integer timestamps or human readable ones, hence
    # we only check if the line contains the string "200 inizio gara", neglecting the timestamp prefix.
    if _has_line_matching_condition(journal, lambda line: line == "0 002 inizio gara"):
        if _has_line_matching_condition(journal, lambda line: "200 inizio gara" in line):
            raise RuntimeError("More than one race start event detected, with different event codes")
        return "r5539"

    # List all non-fallback versions
    possible_versions = list_journal_versions()
    possible_versions.remove("r5539")

    # r11184 introduced protocol numbers for events 110 and 120. If protocol numbers are present,
    # the file cannot be compatible with previous version r11167
    if _has_line_matching_condition(journal, lambda line: ("110" in line or "120" in line) and "PROT:" in line):
        _remove_from_list_if_present(possible_versions, "r11167")

    # r11189 introduced a further timer event 901. If the timer event is present, the file cannot
    # be compatible with previous version r11167
    if _has_line_matching_condition(journal, lambda line: "901 avanzamento estrapolato orologio" in line):
        _remove_from_list_if_present(possible_versions, "r11167")
        _remove_from_list_if_present(possible_versions, "r11184")

    # r17497 introduced the notation n.k in the setup code 003. If the setup code 003 contains a dot,
    # the file cannot be compatible with previous versions r11167, r11184 and r11189
    if _has_line_matching_condition(journal, lambda line: "--- 003" in line and "." in line):
        _remove_from_list_if_present(possible_versions, "r11167")
        _remove_from_list_if_present(possible_versions, "r11184")
        _remove_from_list_if_present(possible_versions, "r11189")

    # r17505 introduced setup code 005. If setup code 005 is present, the file cannot be compatible with
    # previous versions r11167, r11184, r11189 and r17497
    if _has_line_matching_condition(journal, lambda line: "--- 005" in line):
        _remove_from_list_if_present(possible_versions, "r11167")
        _remove_from_list_if_present(possible_versions, "r11184")
        _remove_from_list_if_present(possible_versions, "r11189")
        _remove_from_list_if_present(possible_versions, "r17497")

    # r17548 introduced setup code 002. If setup code 002 is present, the file cannot be compatible with
    # previous versions r11167, r11184, r11189, r17497 and r17505
    if _has_line_matching_condition(journal, lambda line: "--- 002" in line):
        _remove_from_list_if_present(possible_versions, "r11167")
        _remove_from_list_if_present(possible_versions, "r11184")
        _remove_from_list_if_present(possible_versions, "r11189")
        _remove_from_list_if_present(possible_versions, "r17497")
        _remove_from_list_if_present(possible_versions, "r17505")

    # r20642 introduced setup codes 011 and 012. If either of them is present, the file cannot be compatible
    # with previous versions r11167, r11184, r11189, r17497, r17505 and r17548
    if _has_line_matching_condition(journal, lambda line: "--- 011" in line or "--- 012" in line):
        _remove_from_list_if_present(possible_versions, "r11167")
        _remove_from_list_if_present(possible_versions, "r11184")
        _remove_from_list_if_present(possible_versions, "r11189")
        _remove_from_list_if_present(possible_versions, "r17497")
        _remove_from_list_if_present(possible_versions, "r17505")
        _remove_from_list_if_present(possible_versions, "r17548")

    # r20644 uses human readable timestamps. If the timestamp contains a colon, the file cannot be
    # compatible with previous versions r11167, r11184, r11189, r17497, r17505, r17548 and r20642
    if _has_line_matching_condition(journal, lambda line: not line.startswith("---") and ":" in line.split(" ")[0]):
        _remove_from_list_if_present(possible_versions, "r11167")
        _remove_from_list_if_present(possible_versions, "r11184")
        _remove_from_list_if_present(possible_versions, "r11189")
        _remove_from_list_if_present(possible_versions, "r17497")
        _remove_from_list_if_present(possible_versions, "r17505")
        _remove_from_list_if_present(possible_versions, "r17548")
        _remove_from_list_if_present(possible_versions, "r20642")

    # r25013 added an extra field to question definition, with a placeholder answer
    # compatible with previous versions r11167, r11184, r11189, r17497, r17505, r17548, r20642 and r20644
    if _has_line_matching_condition(journal, lambda line: line.startswith("--- 004") and "0000" in line):
        _remove_from_list_if_present(possible_versions, "r11167")
        _remove_from_list_if_present(possible_versions, "r11184")
        _remove_from_list_if_present(possible_versions, "r11189")
        _remove_from_list_if_present(possible_versions, "r17497")
        _remove_from_list_if_present(possible_versions, "r17505")
        _remove_from_list_if_present(possible_versions, "r17548")
        _remove_from_list_if_present(possible_versions, "r20642")
        _remove_from_list_if_present(possible_versions, "r20644")

    # If more than one versions are left, return the earliest one, i.e. the one with the highest
    # backward compatibility
    return possible_versions[0]


def _has_line_matching_condition(journal: list[str], condition: typing.Callable[[str], bool]) -> bool:
    """Determine if there is at least a line matching the provided condition."""
    for line in journal:
        if condition(line):
            return True
    return False


def _remove_from_list_if_present(list_: list[str], entry: str) -> None:
    """Remove an element from a list if the list actually contains it."""
    if entry in list_:
        list_.remove(entry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, required=True, help="Path of the input journal file")
    args = parser.parse_args()
    with open(args.input_file) as journal_stream:
        version = determine_journal_version(journal_stream)
    print(version)
