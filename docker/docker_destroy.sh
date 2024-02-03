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
    echo "The container is still running!"
    echo "Please stop it first with docker_stop.sh"
    exit 1
else
    docker network rm turing_docker_network
    docker rm ${CONTAINER_ID}
    rm ${CONTAINER_ID_FILE}
fi
