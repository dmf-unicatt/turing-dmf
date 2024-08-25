#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

if [[ ! -e "patches" || ! -e "turing" ]]; then
    echo "This script must be run as patches/turing/apply_patches.sh from the top level directory of the repository"
    exit 1
fi

cd turing

# git submodules work with a detached HEAD. The following command returns 0 on detached HEAD, 1 if on branch
# The production environment will typically operate on a git submodule repo with detached HEAD,
# and patches must be applied in that case.
# Local development environment may have already manually applied patches, e.g. while testing a further patch
# to be added. In that case, we skip applying patching altogether, and it is the responsability of the developer
# to have all previous patches already applied.
HEAD_DETACHED=$(git branch --show-current | wc -l)
if [[ ${HEAD_DETACHED} -eq 1 ]]; then
    echo "Currently on a branch, assuming that it already contains the required patches."
else
    apply_patch () {
        echo "Applying patch $1"
        patch -p1 < ../patches/turing/$1
    }

    echo "On a detached HEAD, applying patches"
    apply_patch 0000_customize_footer.patch
    apply_patch 0001_show_elapsed_time_instead_of_countdown.patch
    apply_patch 0002_change_elapsed_time_via_textbox.patch
    apply_patch 0003_penalize_wrong_answer_after_correct_answer.patch
    apply_patch 0004_selenium_updates.patch
    apply_patch 0005_serve_static_files_with_whitenoise.patch
    apply_patch 0006_test_pk_for_postgres.patch
    apply_patch 0007_generalize_race_parameters.patch
    apply_patch 0008_default_n_k_blocco.patch
    apply_patch 0009_upload_journal.patch
    apply_patch 0010_update_requirements.patch
    apply_patch 0011_models_to_from_dict_fixes.patch
    apply_patch 0012_display_protocol_numbers.patch
fi
