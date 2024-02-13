#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

EXEC_OR_RUN=$1
if [[ -z "${EXEC_OR_RUN}" ]]; then
    EXEC_OR_RUN="run"
fi
if [[ "${EXEC_OR_RUN}" != "exec" && "${EXEC_OR_RUN}" != "run" ]]; then
    echo "Invalid run type ${EXEC_OR_RUN}"
    exit 1
fi

DATABASE_TYPE=$2
if [[ -z "${DATABASE_TYPE}" ]]; then
    DATABASE_TYPE="PostgreSQL"
fi
if [[ "${DATABASE_TYPE}" != "PostgreSQL" && "${DATABASE_TYPE}" != "SQLite3" ]]; then
    echo "Invalid database type ${DATABASE_TYPE}"
    exit 1
fi

if [[ "${DATABASE_TYPE}" == "PostgreSQL" ]]; then
    DATABASE_SETUP="\
        POSTGRES_DATABASE_NAME=\$(sed -n -e \"s/^RDS_DB_NAME=//p\" /root/turing/Turing/settings.ini) && \
        sudo -u postgres dropdb --if-exists test_\${POSTGRES_DATABASE_NAME} \
    "
elif [[ "${DATABASE_TYPE}" == "SQLite3" ]]; then
    DATABASE_SETUP="\
        sed -i \"s/RDS_DB_NAME/DISABLED_RDS_DB_NAME/\" /root/turing/Turing/settings.ini \
    "
fi

RUN_TEST_EXEC="\
    export DISPLAY=${DISPLAY} && \
    cd turing && \
    python3 manage.py test --noinput \
"

if [[ "${EXEC_OR_RUN}" == "exec" ]]; then
    if [[ "${DATABASE_TYPE}" == "PostgreSQL" ]]; then
        CONTAINER_ID_FILE=".container_id"
        CONTAINER_ID=$(cat "${CONTAINER_ID_FILE}")
        docker exec ${CONTAINER_ID} /bin/bash -c "${DATABASE_SETUP} && ${RUN_TEST_EXEC}"
    elif [[ "${DATABASE_TYPE}" == "SQLite3" ]]; then
        echo "Cannot use docker exec and change the database type to SQLite3, because it would alter the existing container"
        exit 1
    fi
elif [[ "${EXEC_OR_RUN}" == "run" ]]; then
    docker run --rm turing-dmf:latest /bin/bash -c "${DATABASE_SETUP} && ${RUN_TEST_EXEC}"
fi
