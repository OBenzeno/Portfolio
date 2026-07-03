"""
Orquestrador principal da pipeline ETL — todas as filiais.

Executa a pipeline completa (full) para todas as filiais e endpoints,
sem interação do usuário — compatível com Task Scheduler do Windows.

Ordem de carga por filial: members → sales → debtors (respeita dependências de FK).
Filiais processadas em sequência para evitar conflitos de FK entre elas.
"""

import os
import sys
import logging
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.logger import setup_logging
from pipeline.main import run
from pipeline.etl.load_db import init_db
from pipeline.etl.load import merge_branches

setup_logging()
log = logging.getLogger(__name__)

BRANCHES  = ["filial_01", "filial_02"]
ENDPOINTS = ["members", "sales", "debtors"]
OPERACAO  = "full"


def main() -> None:
    log.info("=" * 60)
    log.info("Iniciando pipeline — %s filiais | operação: %s", len(BRANCHES), OPERACAO)
    log.info("=" * 60)

    init_db()

    falhas = []

    for branch in BRANCHES:
        log.info("=" * 60)
        log.info("Filial: %s", branch)
        log.info("=" * 60)

        for alias in ENDPOINTS:
            log.info("─" * 60)
            try:
                run(alias, branch, operacao=OPERACAO)
            except SystemExit:
                log.error("Falha em [%s/%s]. Continuando para o próximo.", branch, alias)
                falhas.append(f"{branch}/{alias}")
            except Exception as e:
                log.exception("Erro inesperado em [%s/%s]: %s", branch, alias, e)
                falhas.append(f"{branch}/{alias}")

    log.info("=" * 60)
    log.info("Merge de CSVs por endpoint...")
    for alias in ENDPOINTS:
        merge_branches(alias, BRANCHES)

    log.info("=" * 60)
    if falhas:
        log.warning("Pipeline finalizada com falhas: %s", falhas)
    else:
        log.info("Pipeline finalizada sem falhas.")


if __name__ == "__main__":
    main()
