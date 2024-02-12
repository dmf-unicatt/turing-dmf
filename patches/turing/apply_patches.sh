#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

if [[ ! -e "patches" || ! -e "turing" ]]; then
    echo "This script must be run as 'bash patches/turing/apply_patches.sh' from the top level directory of the repository"
    exit 1
fi

apply_patch () {
    # Apply a patch, but only if it was not applied before
    if ! patch -R -p1 -s -f --dry-run < ../patches/turing/$1 1> /dev/null 2>&1; then
        patch -p1 < ../patches/turing/$1
    fi
}

cd turing
apply_patch 0000_customize_footer.patch
apply_patch 0001_show_elapsed_time_instead_of_countdown.patch
apply_patch 0002_change_elapsed_time_via_textbox.patch
apply_patch 0003_penalize_wrong_answer_after_correct_answer.patch
apply_patch 0004_selenium_updates.patch
apply_patch 0005_serve_static_files_with_whitenoise.patch
apply_patch 0007_test_pk_for_postgres.patch
