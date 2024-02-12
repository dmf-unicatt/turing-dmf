#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

# Installed postgres version
POSTGRES_VERSION=15

# Get the value of docker build args from the settings file
POSTGRES_DATABASE_NAME=$(sed -n -e "s/^RDS_DB_NAME=//p" /root/turing/Turing/settings.ini)
if [[ "${POSTGRES_DATABASE_NAME}" != *"-db" ]]; then
    echo "Expected database name ${POSTGRES_DATABASE_NAME} to end with -db"
    exit 1
fi
POSTGRES_PASSWORD=$(sed -n -e "s/^RDS_PASSWORD=//p" /root/turing/Turing/settings.ini)

# Hardcode values of docker create args
POSTGRES_CLUSTER_NAME=${POSTGRES_DATABASE_NAME/-db/-cluster}
if [[ "${POSTGRES_CLUSTER_NAME}" != *"-cluster" ]]; then
    echo "Expected cluster name ${POSTGRES_CLUSTER_NAME} to end with -cluster"
    exit 1
fi
POSTGRES_CLUSTER_DATA_DIRECTORY=/mnt/postgres_data_directory

# Create a new postgres cluster with data directory that matches the volume mounted in docker_create_container.sh,
# if not already done previously
# Note that the marker file .postgres_cluster_created cannot be put in ${POSTGRES_CLUSTER_DATA_DIRECTORY},
# because the cluster needs to be re-created in every container. This is safe upon container destruction because
# postgres data direcory will not be cleared out when creating the cluster in a new container.
POSTGRES_CLUSTER_CREATED_FILE=/root/turing/.postgres_cluster_created
if [[ ! -f ${POSTGRES_CLUSTER_CREATED_FILE} ]]; then
    echo "Creating a new postgres cluster"
    pg_dropcluster ${POSTGRES_VERSION} main
    pg_createcluster ${POSTGRES_VERSION} --datadir=${POSTGRES_CLUSTER_DATA_DIRECTORY} ${POSTGRES_CLUSTER_NAME} -- -E UTF8 --locale=C.utf8 --lc-messages=C
    cp /etc/postgresql/${POSTGRES_VERSION}/${POSTGRES_CLUSTER_NAME}/*.conf ${POSTGRES_CLUSTER_DATA_DIRECTORY}/
    touch ${POSTGRES_CLUSTER_CREATED_FILE}
else
    echo "Reusing existing postgres cluster"
fi

# Start postgresql service
echo "Starting postgresql service"
service postgresql start

# Initialize an empty postgres database, if not already done previously
POSTGRES_DATABASE_INITIALIZED_FILE=${POSTGRES_CLUSTER_DATA_DIRECTORY}/.postgres_database_initialized
if [[ ! -f ${POSTGRES_DATABASE_INITIALIZED_FILE} ]]; then
    echo "Initializing an empty postgres database"
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD}';"
    sudo -u postgres createdb ${POSTGRES_DATABASE_NAME}
    touch ${POSTGRES_DATABASE_INITIALIZED_FILE}
else
    echo "Reusing existing postgres database"
fi

# Ask turing to initialize the django database, if not already done previously
DJANGO_DATABASE_MIGRATED_FILE=${POSTGRES_CLUSTER_DATA_DIRECTORY}/.django_database_migrated
if [[ ! -f ${DJANGO_DATABASE_MIGRATED_FILE} ]]; then
    echo "Initializing django database"
    cd /root/turing
    python3 manage.py makemigrations
    python3 manage.py makemigrations engine
    python3 manage.py migrate
    touch ${DJANGO_DATABASE_MIGRATED_FILE}
else
    echo "Not initializing again django database"
fi

# Add a default administration user to the django database, if not already done previously
DJANGO_ADMIN_INITIALIZED_FILE=${POSTGRES_CLUSTER_DATA_DIRECTORY}/.django_admin_initialized
if [[ ! -f ${DJANGO_ADMIN_INITIALIZED_FILE} ]]; then
    export DJANGO_SUPERUSER_USERNAME=admin
    export DJANGO_SUPERUSER_PASSWORD=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$^&*-_=+' | head -c 10; echo)
    export DJANGO_SUPERUSER_EMAIL="admin@admin.it"
    echo "Initialize the default django administrator user with username ${DJANGO_SUPERUSER_USERNAME} and password ${DJANGO_SUPERUSER_PASSWORD}"
    cd /root/turing
    python3 manage.py createsuperuser --no-input
    touch ${DJANGO_ADMIN_INITIALIZED_FILE}
else
    echo "Not initializing again default django administrator"
fi

# Start the server
echo "Starting the server"
cd /root/turing
python3 manage.py runserver 0.0.0.0:8080
