#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

CONTAINER_ID_FILE=".docker_container_id"
CONTAINER_ID=$(cat "${CONTAINER_ID_FILE}")

MATHRACE_COMPATIBILITY_DIR=$(realpath ../mathrace_compatibility)
TURING_DIR==$(realpath ../turing)

cd ${MATHRACE_COMPATIBILITY_DIR}/scripts
python3 mathrace_log_to_turing_json.py

cd ${MATHRACE_COMPATIBILITY_DIR}/tests/data
rm -rf journal_2020.converted.json journal_2021.converted.json journal_2022.converted.json
for JSON_FILE in *.converted.json; do
    docker cp ${JSON_FILE} ${CONTAINER_ID}:/root/turing/engine/test_gare/${JSON_FILE/.converted.json/.json}
done
for SCORE_FILE in *.expected.score; do
    docker cp ${SCORE_FILE} ${CONTAINER_ID}:/root/turing/engine/test_gare/${SCORE_FILE/.expected.score/.score}
done

docker exec ${CONTAINER_ID} /bin/bash -c "\
    export DISPLAY=$DISPLAY && \
    cd turing && \
    echo 'Run disfida tests first' && \
    python3 manage.py test engine.tests.LiveTests.test_json_folder && \
    echo 'Run all tests afterwards' && \
    python3 manage.py test \
"
