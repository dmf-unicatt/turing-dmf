# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""mathrace_interaction.typing module."""

import typing

RunEntrypointFixtureType: typing.TypeAlias = typing.Callable[[str, list[str]], tuple[str, str]]
RuntimeErrorContainsFixtureType: typing.TypeAlias = typing.Callable[[typing.Callable[[], typing.Any], str], None]
TuringDict: typing.TypeAlias = dict[str, typing.Any]
