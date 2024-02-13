# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""pytest configuration file for integration tests."""

import pathlib

import _pytest
import pytest

_data_dir = pathlib.Path(__file__).parent.parent.parent / "data"

# Integration testing with chrome driver takes several seconds for each journal file.
# To keep the total runtime of tests under control, run tests by default on a subset of the available files.
# Classify journals as either part of basic testing (key equal to True),
# or only part of full testing (key equal to False)
_data_journals_is_basic_testing = {
    # disfida: different formats across the years
    _data_dir / "2013" / "disfida.journal": True,
    _data_dir / "2014" / "disfida.journal": True,
    _data_dir / "2015" / "disfida.journal": True,
    _data_dir / "2016" / "disfida.journal": True,
    _data_dir / "2017" / "disfida.journal": True,
    _data_dir / "2018" / "disfida.journal": True,
    _data_dir / "2019" / "disfida.journal": True,
    _data_dir / "2020" / "disfida.journal": True,
    _data_dir / "2022" / "disfida.journal": True,
    _data_dir / "2023" / "disfida_legacy_format.journal": True,
    _data_dir / "2023" / "disfida_new_format.journal": True,
    # kangourou: different total duration, score keeps increasing to the end of the race
    _data_dir / "2014" / "kangourou.journal": True,
    _data_dir / "2015" / "kangourou.journal": True,
    _data_dir / "2016" / "kangourou.journal": True,
    # cesenatico: alternative race definition and/or guest teams
    _data_dir / "2019" / "cesenatico_finale_femminile_formato_journal.journal": True,
    _data_dir / "2019" / "cesenatico_finale_formato_extracted.journal": True,
    _data_dir / "2019" / "cesenatico_finale_formato_journal.journal": True,
    _data_dir / "2019" / "cesenatico_semifinale_A.journal": False,
    _data_dir / "2019" / "cesenatico_semifinale_B.journal": False,
    _data_dir / "2019" / "cesenatico_semifinale_C.journal": False,
    _data_dir / "2019" / "cesenatico_semifinale_D.journal": False,
    # cesenatico: standard race definition, no guest teams, but with bonus/superbonus specification
    _data_dir / "2022" / "cesenatico_finale.journal": True,
    _data_dir / "2022" / "cesenatico_finale_femminile.journal": True,
    _data_dir / "2022" / "cesenatico_pubblico.journal": True,
    _data_dir / "2022" / "cesenatico_semifinale_A.journal": False,
    _data_dir / "2022" / "cesenatico_semifinale_B.journal": False,
    _data_dir / "2022" / "cesenatico_semifinale_C.journal": False,
    _data_dir / "2022" / "cesenatico_semifinale_D.journal": False,
    # cesenatico: standard race definition, no guest teams, no bonus/superbonus specification
    _data_dir / "2019" / "cesenatico_finale_femminile_formato_extracted.journal": False,
    _data_dir / "2020" / "cesenatico_finale.journal": False,
    _data_dir / "2020" / "cesenatico_finale_femminile.journal": False,
    _data_dir / "2020" / "cesenatico_semifinale_A.journal": False,
    _data_dir / "2020" / "cesenatico_semifinale_B.journal": False,
    _data_dir / "2020" / "cesenatico_semifinale_C.journal": False,
    _data_dir / "2020" / "cesenatico_semifinale_D.journal": False,
    _data_dir / "2021" / "cesenatico_finale.journal": False,
    _data_dir / "2021" / "cesenatico_finale_femminile.journal": False,
    _data_dir / "2021" / "cesenatico_semifinale_A.journal": False,
    _data_dir / "2021" / "cesenatico_semifinale_B.journal": False,
    _data_dir / "2021" / "cesenatico_semifinale_C.journal": False,
    _data_dir / "2021" / "cesenatico_semifinale_D.journal": False,
    _data_dir / "2021" / "cesenatico_semifinale_E.journal": False,
    _data_dir / "2021" / "cesenatico_semifinale_F.journal": False,
    # qualificazione: standard race definition, no guest teams, but with bonus/superbonus specification
    _data_dir / "2022" / "qualificazione_arezzo_cagliari_taranto_trento.journal": False,
    _data_dir / "2022" / "qualificazione_brindisi_catania_forli_cesena_sassari.journal": False,
    _data_dir / "2022" / "qualificazione_campobasso_collevaldelsa_pisa_napoli.journal": False,
    _data_dir / "2022" / "qualificazione_femminile_1.journal": False,
    _data_dir / "2022" / "qualificazione_femminile_2.journal": False,
    _data_dir / "2022" / "qualificazione_femminile_3.journal": False,
    _data_dir / "2022" / "qualificazione_firenze.journal": False,
    _data_dir / "2022" / "qualificazione_foggia_lucca_nuoro_tricase.journal": False,
    _data_dir / "2022" / "qualificazione_genova.journal": False,
    _data_dir / "2022" / "qualificazione_milano.journal": False,
    _data_dir / "2022" / "qualificazione_narni.journal": False,
    _data_dir / "2022" / "qualificazione_parma.journal": False,
    _data_dir / "2022" / "qualificazione_pordenone_udine.journal": False,
    _data_dir / "2022" / "qualificazione_reggio_emilia.journal": False,
    _data_dir / "2022" / "qualificazione_roma.journal": False,
    _data_dir / "2022" / "qualificazione_torino.journal": False,
    _data_dir / "2022" / "qualificazione_trieste.journal": False,
    _data_dir / "2022" / "qualificazione_velletri.journal": False,
    _data_dir / "2022" / "qualificazione_vicenza.journal": False,
    # qualificazione femminale: standard race definition, no guest teams, but with team names
    _data_dir / "2019" / "cesenatico_finale_formato_extracted_nomi_squadra.journal": True,
    _data_dir / "2023" / "qualificazione_femminile_1.journal": True,
    _data_dir / "2023" / "qualificazione_femminile_2.journal": True,
    _data_dir / "2023" / "qualificazione_femminile_3.journal": True,
    # additional tests: different timestamp format
    _data_dir / "2024" / "february_9_short_run.journal": True,
}


def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    """Add options to run tests on all journal files, rather than only the basic subset."""
    parser.addoption("--all-journals", action="store_true", help="Run tests on all journal files")


def pytest_configure(config: pytest.Config) -> None:
    """Add a marker to be associated to the value of the command line option --all-journals."""
    config.addinivalue_line("markers", "requires_all_journals: mark test as requiring all journals")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Apply skip associated to the value of the command line option --all-journals."""
    if not config.getoption("--all-journals"):
        skip_requires_all_journals_tests = pytest.mark.skip(reason="need --all-journals option to run")
        for item in items:
            if "requires_all_journals" in item.keywords:
                item.add_marker(skip_requires_all_journals_tests)


@pytest.fixture(scope="session")
def data_dir() -> pathlib.Path:
    """Return the data directory of mathrace-interaction."""
    return _data_dir


@pytest.fixture(scope="session")
def data_journals(request: _pytest.fixtures.SubRequest) -> list[pathlib.Path]:
    """
    Return journals files in the data directory on which tests should be run.

    By default, only a subset of the journal files will be returned.
    All journal files are return if calling pytest with the --all-journals option.
    """
    if request.config.option.all_journals:
        return list(_data_journals_is_basic_testing.keys())
    else:
        return [journal for (journal, is_basic_testing) in _data_journals_is_basic_testing.items() if is_basic_testing]
