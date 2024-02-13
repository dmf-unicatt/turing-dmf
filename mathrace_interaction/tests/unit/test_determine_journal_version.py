# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test mathrace_interaction.determine_journal_version."""

import pathlib

import pytest

from mathrace_interaction.determine_journal_version import determine_journal_version


@pytest.fixture
def expected_journal_versions_all(data_dir: pathlib.Path) -> dict[pathlib.Path, str]:
    """Return the expected journal versions for all journals in the data directory."""
    return {
        # r5539
        data_dir / "2013" / "disfida.journal": "r5539",
        data_dir / "2014" / "disfida.journal": "r5539",
        # r11167
        # ... untested ...
        # r11184
        data_dir / "2014" / "kangourou.journal": "r11167",
        data_dir / "2015" / "kangourou.journal": "r11184",
        data_dir / "2016" / "disfida.journal": "r11184",
        data_dir / "2016" / "kangourou.journal": "r11184",
        data_dir / "2017" / "disfida.journal": "r11184",
        data_dir / "2018" / "disfida.journal": "r11184",
        data_dir / "2019" / "cesenatico_finale_femminile_formato_extracted.journal": "r11184",
        data_dir / "2019" / "disfida.journal": "r11184",
        data_dir / "2020" / "cesenatico_finale.journal": "r11184",
        data_dir / "2020" / "cesenatico_finale_femminile.journal": "r11184",
        data_dir / "2020" / "cesenatico_semifinale_A.journal": "r11184",
        data_dir / "2020" / "cesenatico_semifinale_B.journal": "r11184",
        data_dir / "2020" / "cesenatico_semifinale_C.journal": "r11184",
        data_dir / "2020" / "cesenatico_semifinale_D.journal": "r11184",
        data_dir / "2021" / "cesenatico_finale.journal": "r11184",
        data_dir / "2021" / "cesenatico_finale_femminile.journal": "r11184",
        data_dir / "2021" / "cesenatico_semifinale_A.journal": "r11184",
        data_dir / "2021" / "cesenatico_semifinale_B.journal": "r11184",
        data_dir / "2021" / "cesenatico_semifinale_C.journal": "r11184",
        data_dir / "2021" / "cesenatico_semifinale_D.journal": "r11184",
        data_dir / "2021" / "cesenatico_semifinale_E.journal": "r11184",
        data_dir / "2021" / "cesenatico_semifinale_F.journal": "r11184",
        data_dir / "2023" / "disfida_legacy_format.journal": "r11184",
        # r11189
        data_dir / "2015" / "disfida.journal": "r11189",
        # r17497
        data_dir / "2019" / "cesenatico_finale_formato_extracted.journal": "r17497",
        # r17505
        data_dir / "2019" / "cesenatico_finale_formato_extracted_nomi_squadra.journal": "r17505",
        # r17548
        data_dir / "2019" / "cesenatico_finale_femminile_formato_journal.journal": "r17548",
        data_dir / "2019" / "cesenatico_finale_formato_journal.journal": "r17548",
        data_dir / "2019" / "cesenatico_semifinale_A.journal": "r17548",
        data_dir / "2019" / "cesenatico_semifinale_B.journal": "r17548",
        data_dir / "2019" / "cesenatico_semifinale_C.journal": "r17548",
        data_dir / "2019" / "cesenatico_semifinale_D.journal": "r17548",
        # r20642
        data_dir / "2020" / "disfida.journal": "r20642",
        data_dir / "2022" / "cesenatico_finale.journal": "r20642",
        data_dir / "2022" / "cesenatico_finale_femminile.journal": "r20642",
        data_dir / "2022" / "cesenatico_pubblico.journal": "r20642",
        data_dir / "2022" / "cesenatico_semifinale_A.journal": "r20642",
        data_dir / "2022" / "cesenatico_semifinale_B.journal": "r20642",
        data_dir / "2022" / "cesenatico_semifinale_C.journal": "r20642",
        data_dir / "2022" / "cesenatico_semifinale_D.journal": "r20642",
        data_dir / "2022" / "qualificazione_arezzo_cagliari_taranto_trento.journal": "r20642",
        data_dir / "2022" / "qualificazione_brindisi_catania_forli_cesena_sassari.journal": "r20642",
        data_dir / "2022" / "qualificazione_campobasso_collevaldelsa_pisa_napoli.journal": "r20642",
        data_dir / "2022" / "qualificazione_femminile_1.journal": "r20642",
        data_dir / "2022" / "qualificazione_femminile_2.journal": "r20642",
        data_dir / "2022" / "qualificazione_femminile_3.journal": "r20642",
        data_dir / "2022" / "qualificazione_firenze.journal": "r20642",
        data_dir / "2022" / "qualificazione_foggia_lucca_nuoro_tricase.journal": "r20642",
        data_dir / "2022" / "qualificazione_genova.journal": "r20642",
        data_dir / "2022" / "qualificazione_milano.journal": "r20642",
        data_dir / "2022" / "qualificazione_narni.journal": "r20642",
        data_dir / "2022" / "qualificazione_parma.journal": "r20642",
        data_dir / "2022" / "qualificazione_pordenone_udine.journal": "r20642",
        data_dir / "2022" / "qualificazione_reggio_emilia.journal": "r20642",
        data_dir / "2022" / "qualificazione_roma.journal": "r20642",
        data_dir / "2022" / "qualificazione_torino.journal": "r20642",
        data_dir / "2022" / "qualificazione_trieste.journal": "r20642",
        data_dir / "2022" / "qualificazione_velletri.journal": "r20642",
        data_dir / "2022" / "qualificazione_vicenza.journal": "r20642",
        data_dir / "2022" / "disfida.journal": "r20642",
        data_dir / "2023" / "qualificazione_femminile_1.journal": "r20642",
        data_dir / "2023" / "qualificazione_femminile_2.journal": "r20642",
        data_dir / "2023" / "qualificazione_femminile_3.journal": "r20642",
        # r20644
        data_dir / "2023" / "disfida_new_format.journal": "r20644",
        data_dir / "2024" / "february_9_short_run.journal": "r20644",
    }


def test_expected_journal_versions_all_fixture(
    data_journals_all: list[pathlib.Path], expected_journal_versions_all: dict[pathlib.Path, str]
) -> None:
    """Test that the expected_journal_versions_all fixture actually contains all journal files."""
    data_journals_difference = set(data_journals_all).symmetric_difference(expected_journal_versions_all.keys())
    assert len(data_journals_difference) == 0, f"Unlisted journals found {data_journals_difference}"


def test_determine_journal_version(
    data_journals_all: list[pathlib.Path], expected_journal_versions_all: dict[pathlib.Path, str]
) -> None:
    """Test determine_journal_version with all journals in the data directory."""
    for journal in data_journals_all:
        with open(journal) as journal_stream:
            actual_version = determine_journal_version(journal_stream)
        expected_version = expected_journal_versions_all[journal]
        assert actual_version == expected_version, (
            f"{journal} version was determined as {actual_version}, but the expected version was {expected_version}")
