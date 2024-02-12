#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

# Outputs of previous steeps
VOLUME_ID_FILE=".docker_volume_id"
VOLUME_ID=$(cat "${VOLUME_ID_FILE}")

POSTGRES_PASSWORD_FILE=".docker_postgres_password"
POSTGRES_PASSWORD=$(cat "${POSTGRES_PASSWORD_FILE}")

# Determine if the script was already run
POSTGRES_INITIALIZED_FILE=".docker_postgres_initialized"
if [[ -f "${POSTGRES_INITIALIZED_FILE}" ]]; then
    POSTGRES_INITIALIZED=$(cat "${POSTGRES_INITIALIZED_FILE}")
    if [[ ${POSTGRES_INITIALIZED} == ${VOLUME_ID} ]]; then
        echo "The database in volume ${VOLUME_ID} was already initialized!"
        exit 1
    fi
fi

# Write out the postgresql data as of debian:12
POSTGRES_DATA_DIRECTORY_FILE=".docker_postgres_data_directory"
POSTGRES_DATA_DIRECTORY="/var/lib/postgresql/15/main"
echo ${POSTGRES_DATA_DIRECTORY} > ${POSTGRES_DATA_DIRECTORY_FILE}

# Use a clean container to create the default postgresql data, since turing-dmf:latest cannot be used
# because it already expects the database to exist
docker run --rm -v ${VOLUME_ID}:${POSTGRES_DATA_DIRECTORY} -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} debian:12 /bin/bash -c "\
    apt update -y -q && \
    apt install -y -qq postgresql sudo && \
    service postgresql start && \
    echo \$(sudo -u postgres psql -c \"SHOW data_directory;\") && \
    sudo -u postgres psql -c \"ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD}';\" && \
    sudo -u postgres createdb turing-dmf-db
"

# Once the database has been created, ask turing to initialize it
docker run --rm -v ${VOLUME_ID}:${POSTGRES_DATA_DIRECTORY} turing-dmf:latest /bin/bash -c "\
    service postgresql start && \
    cd turing && \
    python3 manage.py makemigrations && \
    python3 manage.py makemigrations engine && \
    python3 manage.py migrate && \
    DJANGO_SUPERUSER_EMAIL=admin@admin.it DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=admin python3 manage.py createsuperuser --no-input;
"

# Mark the database in this volume as initialized
echo ${VOLUME_ID} > ${POSTGRES_INITIALIZED_FILE}
