#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

CONTAINER_ID_FILE=".docker_container_id"
CONTAINER_ID=$(cat "${CONTAINER_ID_FILE}")
if [ "$( docker container inspect -f '{{.State.Running}}' ${CONTAINER_ID} )" == "true" ]; then
    echo "The container is already running!"
    echo "If you want to attach a terminal to it, please run docker_terminal.sh"
    exit 1
else
    docker start ${CONTAINER_ID}
    # Entrypoint outputs are not reported to stdout, but logged: fetch them and print them to stdout, after waiting
    # a reasonable amount of time for the entrypoint to be done
    sleep 5 && docker logs --since "6s" --timestamps ${CONTAINER_ID}
fi
