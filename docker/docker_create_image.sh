#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

# Do not run any further if we are not connected to the internet
wget -q --spider https://www.google.com

SECRET_KEY_FILE=".docker_secret_key"
SECRET_KEY=$(cat "${SECRET_KEY_FILE}")

docker build --pull --build-arg SECRET_KEY=${SECRET_KEY} -t turing-dmf:latest -f Dockerfile ..
