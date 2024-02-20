# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Reorder lists in an imported turing dict so that they are ordered consistently with turing."""

import argparse
import json

from mathrace_interaction.typing import TuringDict


def reorder_lists_in_imported_turing(imported_dict: TuringDict) -> None:
    """
    Reorder lists in an imported turing dict so that they are ordered consistently with turing.

    The most notable case in which the ordering in the journal file and in turing differs is the one when
    two race events happen at the same time.

    The dictionary is modified in-place.

    Parameters
    ----------
    imported_dict
        The turing dictionary representing the race, imported from a mathrace journal.
    """
    imported_dict["eventi"] = list(sorted(imported_dict["eventi"], key=lambda e: (
        e["orario"], e["subclass"], e["squadra_id"], e["problema"])))
    imported_dict["soluzioni"] = list(sorted(imported_dict["soluzioni"], key=lambda e: e["problema"]))
    imported_dict["squadre"] = list(sorted(imported_dict["squadre"], key=lambda e: e["num"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, required=True, help="Path of the input json file")
    parser.add_argument("-o", "--output-file", type=str, required=True, help="Path of the output json file")
    args = parser.parse_args()
    with open(args.input_file) as input_json_stream:
        imported_dict = json.load(input_json_stream)
    reorder_lists_in_imported_turing(imported_dict)
    with open(args.output_file, "w") as output_json_stream:
        output_json_stream.write(json.dumps(imported_dict, indent=4))
