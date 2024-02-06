#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

apply_patch () {
    # Apply a patch, but only if it was not applied before
    if ! patch -R -p1 -s -f --dry-run < ../patches/$1 1> /dev/null 2>&1; then
        patch -p1 < ../patches/$1
    fi
}

cd turing
apply_patch 0000_customize_footer.patch
apply_patch 0001_show_elapsed_time_instead_of_countdown.patch
apply_patch 0002_change_elapsed_time_via_textbox.patch
apply_patch 0003_penalize_wrong_answer_after_correct_answer.patch
