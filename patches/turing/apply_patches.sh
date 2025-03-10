#!/bin/bash
# Copyright (C) 2024-2025 by the Turing @ DMF authors
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
    echo "If this is not the case you may want to return to the detached HEAD state with"
    echo "    patches/turing/reset_submodule.sh"
else
    echo "On a detached HEAD, applying patches"

    echo "Determining git configuration"
    if git config user.name && git config user.email; then
        GIT_CONFIGURED="yes"
    else
        GIT_CONFIGURED="no"
    fi

    if [[ $GIT_CONFIGURED == "yes" ]]; then
        echo "Creating new git branch"
        git checkout -b patch-$(date '+%Y%m%d-%H%M%S')
    fi

    TMP_DIR=$(mktemp -d)
    apply_patch () {
        echo "Applying $1"
        (
            set -o pipefail  # otherwise tee would swallow the exit status of patch
            patch --no-backup-if-mismatch --strip 1 < ../patches/turing/$1 | tee $TMP_DIR/out-$1
        )
        if grep -q "offset" "$TMP_DIR/out-$1"; then
            echo "Patch $1 requires offset, which is not allowed. Exiting with error."
            echo "You can refresh the patch by running"
            echo "    patches/turing/refresh_patch.sh $1"
            return 1
        fi
        if grep -q "fuzz" "$TMP_DIR/out-$1"; then
            echo "Patch $1 requires fuzz, which is not allowed. Exiting with error."
            echo "You can refresh the patch by running"
            echo "    patches/turing/refresh_patch.sh $1"
            return 1
        fi
        if [[ $GIT_CONFIGURED == "yes" ]]; then
            git add .
            git commit -m "Apply $1"
        fi
    }

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
    apply_patch 0012_events_str_local_time_zone.patch
    apply_patch 0013_display_protocol_numbers.patch
    apply_patch 0014_manual_bonus.patch
    apply_patch 0015_classification_time_from_server_and_querystring.patch
    apply_patch 0016_improve_admin_panel.patch
    apply_patch 0017_clarify_insertion_form_error.patch
    apply_patch 0018_suspend_reset_delete_button.patch
    apply_patch 0019_users_and_upload_in_race_creation_edit.patch
    apply_patch 0020_logging_datetime_ip.patch
    apply_patch 0021_logout_django_5.patch
    apply_patch 0022_drop_favicon.patch
    apply_patch 0023_new_classification_type_final_proclamation.patch
    apply_patch 0024_team_selection_insertion_form.patch
    apply_patch 0025_offset_star.patch
    apply_patch 0026_unica_position_range.patch
    apply_patch 0027_unica_correct_answers_bottom.patch
    echo "All patches have been applied successfully"
fi
