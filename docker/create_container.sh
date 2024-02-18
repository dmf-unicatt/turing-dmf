#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

VOLUME_ID_FILE=".volume_id"
VOLUME_ID=$(cat "${VOLUME_ID_FILE}")

NETWORK_ID_FILE=".network_id"
if [[ ! -f "${NETWORK_ID_FILE}" ]]; then
    # Ensure that docker's network has been customized, otherwise the docker IP address conflicts
    # with internal IPs on DMF network.
    NETWORK_ID=$(docker network create --subnet=10.200.1.0/24 turing-dmf-network-$(date +%s))
    echo ${NETWORK_ID} > ${NETWORK_ID_FILE}
else
    NETWORK_ID=$(cat "${NETWORK_ID_FILE}")
fi

CONTAINER_ID_FILE=".container_id"
if [[ -f "${CONTAINER_ID_FILE}" ]]; then
    echo "A container already exists!"
    echo "If you want to start it, please run ./start.sh"
    exit 1
else
    # Start docker container on a fixed IP address. The corresponding mac address is generated following
    # https://maclookup.app/faq/how-do-i-identify-the-mac-address-of-a-docker-container-interface
    CONTAINER_ID=$(docker create --net ${NETWORK_ID} --ip 10.200.1.23 --mac-address 02:42:0a:c8:01:17 -p 80:80 -v /tmp/shared:/tmp/shared -v ${VOLUME_ID}:/mnt -e DOCKERHOSTNAME=$(cat /etc/hostname) ghcr.io/dmf-unicatt/turing-dmf:latest)
    echo ${CONTAINER_ID} > ${CONTAINER_ID_FILE}
fi
