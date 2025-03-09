#!/bin/bash
# Copyright (C) 2024-2025 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

if [[ ! -e "patches" || ! -e "turing" ]]; then
    echo "This script must be run as patches/turing/reset_submodule.sh from the top level directory of the repository"
    exit 1
fi

cd turing
git reset --hard
git clean -xdf

cd ..
git submodule update --recursive
