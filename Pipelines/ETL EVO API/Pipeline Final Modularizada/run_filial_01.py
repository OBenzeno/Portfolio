"""
Orquestrador provisório para execução automática da filial_01.

Executa a pipeline completa (full) para todos os endpoints da filial_01
sem interação do usuário — compatível com Task Scheduler do Windows.

filial_02 desabilitada: token pendente de correção.
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

BRANCH    = "filial_01"
ENDPOINTS = ["members", "sales", "debtors"]
OPERACAO  = "full"


def main() -> None:
    log.info("=" * 60)
    log.info("Iniciando pipeline — %s | operação: %s", BRANCH, OPERACAO)
    log.info("=" * 60)

    init_db()

    falhas = []

    for alias in ENDPOINTS:
        log.info("─" * 60)
        try:
            run(alias, BRANCH, operacao=OPERACAO)
        except SystemExit:
            log.error("Falha em [%s/%s]. Continuando para o próximo.", BRANCH, alias)
            falhas.append(alias)
        except Exception as e:
            log.exception("Erro inesperado em [%s/%s]: %s", BRANCH, alias, e)
            falhas.append(alias)

    log.info("=" * 60)
    log.info("Merge de CSVs por endpoint...")
    for alias in ENDPOINTS:
        merge_branches(alias, [BRANCH])

    log.info("=" * 60)
    if falhas:
        log.warning("Pipeline finalizada com falhas: %s", falhas)
    else:
        log.info("Pipeline finalizada sem falhas.")


if __name__ == "__main__":
    main()
