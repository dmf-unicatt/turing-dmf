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


def convert(mathrace_log_filename: str, turing_json_filename: str):
    with open(mathrace_log_filename) as mathrace_log_file:
        mathrace_log = [line.strip("\n") for line in mathrace_log_file.readlines()]

    turing_dict = dict()

    # Race name
    race_name = pathlib.Path(mathrace_log_filename).name.replace(".extracted.log", "")
    turing_dict["nome"] = race_name

    # Race year
    race_year = int(race_name.replace("journal_", ""))
    race_start = datetime.datetime(race_year, 1, 1)
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

    # From the second line, determine the participating teams
    race_def_ints = race_def.split(" ")
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
    turing_dict["fixed_bonus"] = "20,15,10,8,6,5,4,3,2,1"

    # Switch between different editions to complete the values in the second line
    if len(race_def_ints) == 5:
        # log format pre 2012 did not have the following information. Assume default values
        turing_dict["super_mega_bonus"] = "0,0,0,0,0,0"
        turing_dict["n_blocco"] = None
        assert race_def_ints[4] == "1"
        turing_dict["durata"] = 120
    else:
        assert len(race_def_ints) == 10
        superbonus_cardinality = int(race_def_ints[4])
        assert superbonus_cardinality == 6
        turing_dict["super_mega_bonus"] = "100,60,40,30,20,10"
        turing_dict["n_blocco"] = int(race_def_ints[5])
        assert race_def_ints[6] == "1"
        assert race_def_ints[7] == "1"
        turing_dict["durata"] = int(race_def_ints[8])
        assert turing_dict["durata"] == 120
        assert race_def_ints[9] == "100"

    # mathrace does not use the following race parameters
    turing_dict["k_blocco"] = None
    turing_dict["cutoff"] = None

    # Next lines starting with --- 004 contain the definition of the initial score for each question
    questions = list()
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
            "problema": q + 1, "nome": f"Problema {q + 1}", "risposta": "1", "punteggio": question_def_ints[1]})
    turing_dict["soluzioni"] = questions

    # Next line should mark the start of the race
    assert mathrace_log[line] in ("0 002 inizio gara", "0 200 inizio gara")
    line += 1

    # Loop over events during the race
    events = list()
    manual_bonuses = list()
    while True:
        timestamp, event_type, event_content = mathrace_log[line].split(" ", 2)
        line += 1
        if event_type in ("010", "011", "110", "120"):
            if " PROT" in event_content:
                event_content, _ = event_content.split(" PROT")
            else:
                assert " squadra" in event_content
                event_content, _ = event_content.split(" squadra")
            event_content_ints = event_content.split(" ")
            event_content_dict = {
                "orario": (race_start + datetime.timedelta(seconds=int(timestamp))).isoformat(),
                "squadra_id" : event_content_ints[0], "problema" : event_content_ints[1]}
            if event_type in ("010", "120"):
                # jolly was chosen
                event_content_dict.update({"subclass": "Jolly"})
                assert len(event_content_ints) == 2
            elif event_type in ("011", "110"):
                # answer was submitted
                assert len(event_content_ints) == 3
                event_content_dict.update({"subclass": "Consegna", "risposta": event_content_ints[2]})
            else:
                raise RuntimeError(f"Invalid event type {event_type} at time {timestamp}")
            events.append(event_content_dict)
        elif event_type in ("021", "022", "101", "121", "901"):
            # rendering update
            continue
        elif event_type in ("130", ):
            # manual addition of bonus to fix registration errors: we do not handle those cases
            manual_bonuses.append(event_content)
        elif event_type in ("029", "210"):
            # race ending event
            break
        else:
            raise RuntimeError(f"Invalid event type {event_type} at time {timestamp}")
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
