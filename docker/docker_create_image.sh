#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

# Do not run any further if we are not connected to the internet
wget -q --spider https://www.google.com

docker build --pull -t turing-dmf:latest -f Dockerfile ..