#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

SECRET_KEY_FILE=".docker_secret_key"
if [[ -f "${SECRET_KEY_FILE}" ]]; then
    echo "A secret key already exists!"
    echo "If you want to destroy it and create a new one, please remove the ${SECRET_KEY_FILE} file"
    exit 1
else
    SECRET_KEY=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)' | head -c 50; echo)
    echo ${SECRET_KEY} > ${SECRET_KEY_FILE}
fi