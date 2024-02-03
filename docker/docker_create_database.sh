#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

VOLUME_ID_FILE=".docker_volume_id"
if [[ ! -f "${VOLUME_ID_FILE}" ]]; then
    echo "The database volume does not exist!"
    echo "Please create it with docker_create_volume.sh"
    exit 1
else
    VOLUME_ID=$(cat "${VOLUME_ID_FILE}")
fi

docker run --rm -v ${VOLUME_ID}:/mnt/database turing-dmf:latest /bin/bash -c '\
    DATABASE=/mnt/database/db.sqlite3 && \
    if [[ -f "$DATABASE" ]]; then \
        echo "Database already exists. Not overwriting"; \
    else \
        touch $DATABASE && \
        cd turing && \
        python3 manage.py makemigrations && \
        python3 manage.py makemigrations engine && \
        python3 manage.py migrate && \
        DJANGO_SUPERUSER_EMAIL=admin@admin.it DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=admin python3 manage.py createsuperuser --no-input;
    fi \
'
