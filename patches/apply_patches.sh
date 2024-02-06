# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
cd turing
git checkout -- .
patch -p1 < ../patches/0000_customize_footer.patch
patch -p1 < ../patches/0001_show_elapsed_time_instead_of_countdown.patch
patch -p1 < ../patches/0002_change_elapsed_time_via_textbox.patch
patch -p1 < ../patches/0003_penalize_wrong_answer_after_correct_answer.patch
