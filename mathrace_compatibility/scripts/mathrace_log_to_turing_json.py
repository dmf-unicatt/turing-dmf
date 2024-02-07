# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Convert a mathrace log to a turing json file."""

import datetime
import json
import pathlib
import sys


def convert(mathrace_log_filename: str, turing_json_filename: str) -> None:
    """Convert a race from mathrace log format to turing json format."""
    with open(mathrace_log_filename) as mathrace_log_file:
        mathrace_log = [line.strip("\n") for line in mathrace_log_file.readlines()]

    turing_dict: dict[str, int | str | list[dict[str, int | str]] | None] = dict()

    # Race name
    race_name = pathlib.Path(mathrace_log_filename).name.replace(".extracted.log", "")
    turing_dict["nome"] = race_name

    # Race year
    race_year = int(race_name.replace("journal_", ""))
    race_start = datetime.datetime(race_year, 1, 1, tzinfo=datetime.timezone.utc)
    turing_dict["inizio"] = race_start.isoformat()

    # Line counter
    line = 0

    # The first line must contain the initialization of the race
    assert mathrace_log[line] == "--- 001 inizializzazione simulatore"
    line += 1

    # The second line contains basic info about the race definition
    race_def = mathrace_log[line]
    line += 1
    assert race_def.startswith("--- 003 ")
    race_def = race_def[8:]
    assert "squadre: " in race_def
    assert "quesiti: " in race_def
    if " -- squadre:" in race_def:
        race_def, _ = race_def.split(" -- squadre:")
    else:
        race_def, _ = race_def.split(" squadre:")
    race_def_ints = race_def.split(" ")
    assert len(race_def_ints) == 10

    # From the second line, determine the participating teams
    num_teams = int(race_def_ints[0])
    turing_dict["squadre"] = [{"nome": f"Squadra {t + 1}", "num": t + 1, "ospite": False} for t in range(num_teams)]

    # From the second line, determine the number of questions
    num_questions = int(race_def_ints[1])
    turing_dict["num_problemi"] = num_questions

    # From the second line, determine the initial score
    initial_score = int(race_def_ints[2])
    assert initial_score == num_questions * 10, "turing does not seem to allow to change the initial score"

    # From the second line, determine the bonus cardinality
    bonus_cardinality = int(race_def_ints[3])
    assert bonus_cardinality == 10
    if mathrace_log[line].startswith("--- 011 "):
        fixed_bonus_def = mathrace_log[line]
        line += 1
        fixed_bonus_def = fixed_bonus_def[8:]
        assert "definizione dei" in fixed_bonus_def
        fixed_bonus_def, _ = fixed_bonus_def.split("definizione dei")
        fixed_bonus_def_ints = fixed_bonus_def.split(" ")
        turing_dict["fixed_bonus"] = ",".join(fixed_bonus_def_ints[1:bonus_cardinality+1])
    else:
        turing_dict["fixed_bonus"] = "20,15,10,8,6,5,4,3,2,1"

    # From the second line, determine superbonus cardinality
    superbonus_cardinality = int(race_def_ints[4])
    assert superbonus_cardinality == 6
    if mathrace_log[line].startswith("--- 012 "):
        super_mega_bonus_def = mathrace_log[line]
        line += 1
        super_mega_bonus_def = super_mega_bonus_def[8:]
        assert "definizione dei" in super_mega_bonus_def
        super_mega_bonus_def, _ = super_mega_bonus_def.split("definizione dei")
        super_mega_bonus_def_ints = super_mega_bonus_def.split(" ")
        turing_dict["super_mega_bonus"] = ",".join(super_mega_bonus_def_ints[1:superbonus_cardinality+1])
    else:
        turing_dict["super_mega_bonus"] = "100,60,40,30,20,10"

    # From the second line, determine the value of n
    turing_dict["n_blocco"] = int(race_def_ints[5])

    # From the second line, determine the total time of the race
    durata = int(race_def_ints[8])
    assert durata in (120, 135)
    turing_dict["durata"] = durata

    # Three further items in the second line are ignored
    assert race_def_ints[6] == "1"
    assert race_def_ints[7] == "1"
    assert int(race_def_ints[9]) == durata - 20

    # mathrace does not use the following race parameters
    turing_dict["k_blocco"] = 1
    turing_dict["cutoff"] = None

    # Next lines starting with --- 004 contain the definition of the initial score for each question
    questions: list[dict[str, int | str]] = list()
    for q in range(num_questions):
        question_def = mathrace_log[line]
        line += 1
        assert question_def.startswith("--- 004 ")
        question_def = question_def[8:]
        assert "quesito " in question_def
        question_def, _ = question_def.split(" quesito")
        question_def_ints = question_def.split(" ")
        assert len(question_def_ints) == 2
        assert question_def_ints[0] == str(q + 1)
        questions.append({
            "problema": q + 1, "nome": f"Problema {q + 1}", "risposta": "1", "punteggio": int(question_def_ints[1])})
    turing_dict["soluzioni"] = questions

    # Next line should mark the start of the race
    assert mathrace_log[line] in ("0 002 inizio gara", "0 200 inizio gara")
    line += 1

    # Loop over events during the race
    events: list[dict[str, int | str]] = list()
    manual_bonuses = list()
    timestamp_offset = None
    while True:
        timestamp_str, event_type, event_content = mathrace_log[line].split(" ", 2)
        line += 1
        if event_type in ("010", "011", "110", "120"):
            if timestamp_offset is not None:
                timestamp = int(timestamp_str) + timestamp_offset
            else:
                # allow jolly to be selected before the offset is computed, since
                # setting it with a slightly wrong timestamp does not affect the overall
                # score of the race
                assert event_type in ("010", "120")
                timestamp = int(timestamp_str)
            if " PROT" in event_content:
                event_content, _ = event_content.split(" PROT")
            else:
                assert " squadra" in event_content
                event_content, _ = event_content.split(" squadra")
            event_content_ints = event_content.split(" ")
            event_content_dict: dict[str, int | str] = {
                "orario": (race_start + datetime.timedelta(seconds=timestamp)).isoformat(),
                "squadra_id" : int(event_content_ints[0]), "problema" : int(event_content_ints[1])}
            if event_type in ("010", "120"):
                # jolly was chosen
                event_content_dict.update({"subclass": "Jolly"})
                assert len(event_content_ints) == 2
            elif event_type in ("011", "110"):
                # answer was submitted
                assert len(event_content_ints) == 3
                event_content_dict.update({"subclass": "Consegna", "risposta": int(event_content_ints[2])})
            else:
                raise RuntimeError(f"Invalid event type {event_type} at time {timestamp_str}")
            events.append(event_content_dict)
        elif event_type in ("021", "121"):
            # jolly deadline
            continue
        elif event_type in ("022", "101", "901"):
            # timer update
            if timestamp_offset is None:
                assert event_content.startswith("aggiorna punteggio esercizi")
                timestamp_offset = 60 - int(timestamp_str)
            else:
                # assume that the offset is constant throughout the race
                continue
        elif event_type in ("130", ):
            # manual addition of bonus to fix registration errors: we do not handle those cases
            manual_bonuses.append(event_content)
        elif event_type in ("029", "210"):
            # race ending event
            break
        else:
            raise RuntimeError(f"Invalid event type {event_type} at time {timestamp_str}")
    turing_dict["eventi"] = events

    # Save dictionary to json file (and text file, in case of non empty manual bonus)
    with open(turing_json_filename, "w") as turing_json_file:
        turing_json_file.write(json.dumps(turing_dict, indent=4))
    if len(manual_bonuses) > 0:
        with open(turing_json_filename.replace(".json", ".manual_bonuses.txt"), "w") as manual_bonuses_file:
            manual_bonuses_file.write("\n".join(manual_bonuses))

if __name__ == "__main__":  # pragma: no cover
    assert len(sys.argv) in (1, 3)

    if len(sys.argv) == 1:
        for mathrace_log_file in sorted(pathlib.Path("../tests/data").glob("journal_*.extracted.log")):
            mathrace_log_filename = str(mathrace_log_file)
            turing_json_filename = mathrace_log_filename.replace(".extracted.log", ".converted.json")
            print(f"Converting {mathrace_log_filename}")
            convert(mathrace_log_filename, turing_json_filename)
    elif len(sys.argv) == 1:
        convert(sys.argv[1], sys.argv[2])
