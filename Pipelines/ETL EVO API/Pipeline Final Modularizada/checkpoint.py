"""
Gerenciamento de checkpoints para suporte a carga incremental.
Checkpoint é isolado por endpoint + filial: checkpoint_{alias}_{branch}.json
"""

import json
import logging
from pipeline.config import DIR_CHECKPOINTS

log = logging.getLogger(__name__)


def _checkpoint_path(alias: str, branch: str) -> str:
    return f"{DIR_CHECKPOINTS}/checkpoint_{alias}_{branch}.json"


def load_checkpoint(alias: str, branch: str) -> dict:
    """
    Carrega o checkpoint da combinação alias + filial.

    Returns:
        Dict com 'last_run' se existir, caso contrário dict vazio.
    """
    path = _checkpoint_path(alias, branch)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            log.debug("Checkpoint carregado [%s/%s]: %s", branch, alias, data)
            return data
    except FileNotFoundError:
        log.debug("Nenhum checkpoint encontrado para '%s/%s'.", branch, alias)
        return {}


def save_checkpoint(alias: str, branch: str, date_end: str) -> None:
    """Persiste o timestamp da última execução bem-sucedida."""
    path = _checkpoint_path(alias, branch)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"last_run": date_end}, f, indent=2)
    log.info("Checkpoint salvo [%s/%s]: %s", branch, alias, date_end)
