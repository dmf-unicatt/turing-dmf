#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

if [[ -z "$1" ]]; then
    COMMAND="/bin/bash"
else
    COMMAND="$1"
fi

CONTAINER_ID_FILE=".docker_container_id"
CONTAINER_ID=$(cat "${CONTAINER_ID_FILE}")
docker exec -it ${CONTAINER_ID} $COMMAND
