# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Determine the version of a mathrace journal."""

import typing


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

        The version is the name of the revision in simdis, available from
        https://svn.dmf.unicatt.it/svn/projects/simdis

        Only versions after the 2013 edition are available. Earlier versions are not applicable because
        of backward incompatible regulation changes. All versions ignore lines starting with # and consider
        them as comments.

        The following versions are available:

        * r5539 (2013-01-18 01:21:11 +0100): initial version.

          This version uses the following race setup codes:
          ° --- 001: file begin
          ° --- 003: race definition
          ° --- 004: question definition
          ° --- 999: file end

          This version uses the following race event codes:
          ° 0 002: race start
          ° timestamp 010: jolly selection by a team
          ° timestamp 011: answer submission by a team
          ° timestamp 021: jolly timeout
          ° timestamp 022: timer update
          ° timestamp 027: race suspended
          ° timestamp 028: race resumed
          ° timestamp 029: race end
          ° timestamp 091: manual addition of a bonus

        * r11167 (2015-03-08 20:41:09 +0100): this version introduced some code changes in race events.

          All race event codes were changed as follows:
          ° 0 200: race start was changed from 002 to 200
          ° timestamp 101: timer update was changed from 022 to 101
          ° timestamp 110: answer submission by a team was changed from 011 to 110
          ° timestamp 120: jolly selection by a team was changed from 010 to 120
          ° timestamp 121: jolly timeout was changed from 021 to 121
          ° timestamp 130: manual addition of a bonus was changed from 091 to 130
          ° timestamp 201: race suspended was changed from 027 to 201
          ° timestamp 202: race resumed was changed from 028 to 202
          ° timestamp 210: race end was changed from 029 to 210

        * r11184 (2015-03-10 09:04:16 +0100): this version introduced protocol numbers in
          race events 110 and 120

        * r11189 (2015-03-10 12:01:10 +0100): this version added a further timer event.

          The following event setup codes were added:
          ° timestamp 901: timer update for the second timer.

        * r17497 (2019-05-29 00:55:27 +0200): this version added support for non-default k.

          The following race setup codes were changed:
          ° --- 003: race definition appends the value of k to the one of n with the notation n.k

        * r17505 (2019-05-30 21:37:33 +0200): this version added team definition as a race code.

          The following race setup codes were added:
          ° --- 005: team definition

        * r17548 (2019-06-07 21:45:05 +0200): this version added and alternative race definition.

          The following race setup codes were added:
          ° --- 002: alternative race definition

        * r20642 (2021-06-05 01:31:45 +0200): this version added bonus and superbonus race codes.

          The following race setup codes were added:
          ° --- 011: bonus definition
          ° --- 012: superbonus definition

        * r20644 (2021-06-08 01:36:41 +0200): this version prints human readable timestamps
          of the form hh:mm:ss.msec instead of number of elapsed seconds.

          This change affects all race event codes.

        * r25013 (2024-02-13 00:10:49 +0100): this version added an extra field to the question definition.
          The field currently stores a 0000 placeholder, but in future may store the exact answer to the question.

          The following race setup codes were changed:
          ° --- 004: question definition
    """
    journal = [line.strip("\n") for line in journal_stream.readlines()]

    # Since all versions after the fallback one use the event code 200 for the race start,
    # a journal containing the code 002 is a fallback journal
    if _has_line_matching_condition(journal, lambda line: line == "0 002 inizio gara"):
        if _has_line_matching_condition(journal, lambda line: line == "0 200 inizio gara"):
            raise RuntimeError("More than one race start event detected, with different event codes")
        return "r5539"

    # List all non-fallback versions
    possible_versions = [
        "r11167", "r11184", "r11189", "r17497", "r17505", "r17548", "r20642", "r20644", "r25013"
    ]

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
