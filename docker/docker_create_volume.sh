#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

VOLUME_ID_FILE=".docker_volume_id"
if [[ -f "${VOLUME_ID_FILE}" ]]; then
    echo "A database volume already exists!"
    echo "If you want to destroy it and create a new one, please run docker_destroy_volume.sh"
    exit 1
else
    VOLUME_ID=$(docker volume create turing-database-$(date +%s))
    echo ${VOLUME_ID} > ${VOLUME_ID_FILE}
    echo "You can now create a container by running docker_create_cointainer.sh"
fi
