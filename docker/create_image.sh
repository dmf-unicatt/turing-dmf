#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

# Do not run any further if we are not connected to the internet
wget -q --spider https://www.google.com

# Read in secrets
DJANGO_SECRET_KEY_FILE=".django_secret_key"
DJANGO_SECRET_KEY=$(cat "${DJANGO_SECRET_KEY_FILE}")

POSTGRES_PASSWORD_FILE=".postgres_password"
POSTGRES_PASSWORD=$(cat "${POSTGRES_PASSWORD_FILE}")

# Build image
docker build --pull --build-arg DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} --build-arg POSTGRES_PASSWORD=${POSTGRES_PASSWORD} -t turing-dmf:latest -f Dockerfile ..
