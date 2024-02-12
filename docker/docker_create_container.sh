#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

VOLUME_ID_FILE=".docker_volume_id"
VOLUME_ID=$(cat "${VOLUME_ID_FILE}")

CONTAINER_ID_FILE=".docker_container_id"
if [[ -f "${CONTAINER_ID_FILE}" ]]; then
    echo "A container already exists!"
    echo "If you want to start it, please run docker_start.sh"
    echo "If you want to destroy it and create a new one, please run docker_destroy_container.sh"
    exit 1
else
    # Ensure that docker's network has been customized, otherwise the docker IP address conflicts
    # with internal IPs on DMF network.
    docker network create --subnet=10.200.1.0/24 turing-dmf-network
    # Start docker container on a fixed IP address. The corresponding mac address is generated following
    # https://maclookup.app/faq/how-do-i-identify-the-mac-address-of-a-docker-container-interface
    CONTAINER_ID=$(docker create --net turing-dmf-network --ip 10.200.1.23 --mac-address 02:42:0a:c8:01:17 -p 8080:8080 -v /tmp/shared-turing-dmf:/tmp/shared-turing-dmf -v ${VOLUME_ID}:/mnt/postgres_data_directory -e DOCKERHOSTNAME=$(cat /etc/hostname) turing-dmf:latest)
    echo ${CONTAINER_ID} > ${CONTAINER_ID_FILE}
fi
