# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""pytest configuration file for unit tests."""

import pathlib

import pytest


@pytest.fixture
def data_dir() -> pathlib.Path:
    """Return the data directory of mathrace-compatibility."""
    return pathlib.Path(__file__).parent.parent.parent / "data"


@pytest.fixture
def data_journals_basic(data_dir: pathlib.Path) -> list[pathlib.Path]:
    """Return a subset of the journals in the data directory."""
    return [
        # disfida
        data_dir / "2013" / "disfida.journal",
        data_dir / "2014" / "disfida.journal",
        data_dir / "2015" / "disfida.journal",
        data_dir / "2016" / "disfida.journal",
        data_dir / "2017" / "disfida.journal",
        data_dir / "2018" / "disfida.journal",
        data_dir / "2019" / "disfida.journal",
        data_dir / "2020" / "disfida.journal",
        data_dir / "2022" / "disfida.journal",
        data_dir / "2023" / "disfida.journal",
        # kangourou: different total duration, score keeps increasing to the end of the race
        data_dir / "2014" / "kangourou.journal",
        data_dir / "2015" / "kangourou.journal",
        data_dir / "2016" / "kangourou.journal",
        # cesenatico: alternative race definition and/or guest teams
        data_dir / "2019" / "cesenatico_finale_femminile_formato_journal.journal",
        data_dir / "2019" / "cesenatico_finale_formato_extracted.journal",
        data_dir / "2019" / "cesenatico_finale_formato_journal.journal",
        # cesenatico: standard race definition, no guest teams, but with bonus/superbonus specification
        data_dir / "2022" / "cesenatico_finale.journal",
        data_dir / "2022" / "cesenatico_finale_femminile.journal",
        data_dir / "2022" / "cesenatico_pubblico.journal",
        # qualificazione femminale: standard race definition, no guest teams, but with team names
        data_dir / "2019" / "cesenatico_finale_formato_extracted_nomi_squadra.journal",
        data_dir / "2023" / "qualificazione_femminile_1.journal",
        data_dir / "2023" / "qualificazione_femminile_2.journal",
        data_dir / "2023" / "qualificazione_femminile_3.journal",
        # local tests: different timestamp format
        data_dir / "2024" / "february_9_short_run.journal",
    ]


@pytest.fixture
def data_journals_all(data_dir: pathlib.Path, data_journals_basic: list[pathlib.Path]) -> pathlib.Path:
    """Return all journals in the data directory."""
    return [
        *data_journals_basic,
        # cesenatico: alternative race definition and/or guest teams
        data_dir / "2019" / "cesenatico_semifinale_A.journal",
        data_dir / "2019" / "cesenatico_semifinale_B.journal",
        data_dir / "2019" / "cesenatico_semifinale_C.journal",
        data_dir / "2019" / "cesenatico_semifinale_D.journal",
        # cesenatico: standard race definition, no guest teams, no bonus/superbonus specification
        data_dir / "2019" / "cesenatico_finale_femminile_formato_extracted.journal",
        data_dir / "2020" / "cesenatico_finale.journal",
        data_dir / "2020" / "cesenatico_finale_femminile.journal",
        data_dir / "2020" / "cesenatico_semifinale_A.journal",
        data_dir / "2020" / "cesenatico_semifinale_B.journal",
        data_dir / "2020" / "cesenatico_semifinale_C.journal",
        data_dir / "2020" / "cesenatico_semifinale_D.journal",
        data_dir / "2021" / "cesenatico_finale.journal",
        data_dir / "2021" / "cesenatico_finale_femminile.journal",
        data_dir / "2021" / "cesenatico_semifinale_A.journal",
        data_dir / "2021" / "cesenatico_semifinale_B.journal",
        data_dir / "2021" / "cesenatico_semifinale_C.journal",
        data_dir / "2021" / "cesenatico_semifinale_D.journal",
        data_dir / "2021" / "cesenatico_semifinale_E.journal",
        data_dir / "2021" / "cesenatico_semifinale_F.journal",
        # cesenatico: standard race definition, no guest teams, but with bonus/superbonus specification
        data_dir / "2022" / "cesenatico_semifinale_A.journal",
        data_dir / "2022" / "cesenatico_semifinale_B.journal",
        data_dir / "2022" / "cesenatico_semifinale_C.journal",
        data_dir / "2022" / "cesenatico_semifinale_D.journal",
        data_dir / "2022" / "qualificazione_arezzo_cagliari_taranto_trento.journal",
        data_dir / "2022" / "qualificazione_brindisi_catania_forli_cesena_sassari.journal",
        data_dir / "2022" / "qualificazione_campobasso_collevaldelsa_pisa_napoli.journal",
        data_dir / "2022" / "qualificazione_femminile_1.journal",
        data_dir / "2022" / "qualificazione_femminile_2.journal",
        data_dir / "2022" / "qualificazione_femminile_3.journal",
        data_dir / "2022" / "qualificazione_firenze.journal",
        data_dir / "2022" / "qualificazione_foggia_lucca_nuoro_tricase.journal",
        data_dir / "2022" / "qualificazione_genova.journal",
        data_dir / "2022" / "qualificazione_milano.journal",
        data_dir / "2022" / "qualificazione_narni.journal",
        data_dir / "2022" / "qualificazione_parma.journal",
        data_dir / "2022" / "qualificazione_pordenone_udine.journal",
        data_dir / "2022" / "qualificazione_reggio_emilia.journal",
        data_dir / "2022" / "qualificazione_roma.journal",
        data_dir / "2022" / "qualificazione_torino.journal",
        data_dir / "2022" / "qualificazione_trieste.journal",
        data_dir / "2022" / "qualificazione_velletri.journal",
        data_dir / "2022" / "qualificazione_vicenza.journal",
    ]
