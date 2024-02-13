#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

DJANGO_SECRET_KEY_FILE=".django_secret_key"
if [[ -f "${DJANGO_SECRET_KEY_FILE}" ]]; then
    echo "A django secret key already exists!"
    echo "If you want to destroy it and create a new one, please remove the ${DJANGO_SECRET_KEY_FILE} file"
    exit 1
else
    DJANGO_SECRET_KEY=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyz0123456789!@#$^&*-_=+' | head -c 50; echo)
    echo ${DJANGO_SECRET_KEY} > ${DJANGO_SECRET_KEY_FILE}
fi

POSTGRES_PASSWORD_FILE=".postgres_password"
if [[ -f "${POSTGRES_PASSWORD_FILE}" ]]; then
    echo "A postgres password already exists!"
    echo "If you want to destroy it and create a new one, please remove the ${POSTGRES_PASSWORD_FILE} file"
    exit 1
else
    POSTGRES_PASSWORD=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' | head -c 50; echo)
    echo ${POSTGRES_PASSWORD} > ${POSTGRES_PASSWORD_FILE}
fi
