#!/bin/bash
# Copyright (C) 2024-2025 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

: ${1?"Usage: $0 name.patch"}
PATCH_NAME="$1"

set -e

if [[ ! -e "patches" || ! -e "turing" ]]; then
    echo "This script must be run as patches/turing/refresh_patch.sh from the top level directory of the repository"
    exit 1
fi

cd turing
git add .
git diff --cached > ../patches/turing/${PATCH_NAME}

cd ..
patches/turing/reset_submodule.sh
