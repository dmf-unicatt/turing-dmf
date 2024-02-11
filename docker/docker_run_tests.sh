#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

CONTAINER_ID_FILE=".docker_container_id"
CONTAINER_ID=$(cat "${CONTAINER_ID_FILE}")

docker exec ${CONTAINER_ID} /bin/bash -c "\
    export DISPLAY=$DISPLAY && \
    cd turing && \
    python3 manage.py test \
"
