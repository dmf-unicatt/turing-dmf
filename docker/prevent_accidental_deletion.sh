#!/bin/bash
# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

chattr +i .container_id
chattr +i .network_id
chattr +i .network_properties/*
chattr +i .volume_id
