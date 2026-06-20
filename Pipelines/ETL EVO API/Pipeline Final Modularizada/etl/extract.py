"""
Estágio de extração: paginação sobre a API com tratamento de interrupção graceful.
"""

import json
import time
import logging
from typing import Any
from requests.auth import HTTPBasicAuth

from pipeline.config import MAX_RETRIES, REQUEST_DELAY, DIR_PARTIAL
from pipeline.http_client import get_with_retry

log = logging.getLogger(__name__)


def _save_partial(data: list, alias: str, branch: str) -> None:
    """Persiste dados parciais em caso de interrupção."""
    tmp_file = f"{DIR_PARTIAL}/{alias}_{branch}_partial_{int(time.time())}.json"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    log.info("Dados parciais salvos em '%s'.", tmp_file)


def extract(
    api_url: str,
    auth: HTTPBasicAuth,
    params: dict,
    endpoint_cfg: dict,
    alias: str,
    branch: str,
    endpoint_label: str = "",
) -> list[Any]:
    """
    Realiza extração paginada da API.

    Args:
        api_url: URL base do endpoint.
        auth: Credenciais HTTPBasicAuth da filial.
        params: Parâmetros iniciais da requisição (take, skip, datas, etc.).
        endpoint_cfg: Configuração do endpoint (responseKey, etc.).
        alias: Nome do endpoint.
        branch: Identificador da filial (usado no arquivo parcial e logs).
        endpoint_label: Rótulo para logs.

    Returns:
        Lista com todos os registros coletados.
    """
    all_data: list = []
    pagina         = 1
    tentativas     = 0
    response_key   = endpoint_cfg.get("responseKey")

    try:
        while True:
            log.debug(
                "[%s/%s] Página %s | offset %s | acumulado %s",
                branch, alias, pagina, params.get("skip"), len(all_data),
            )

            response = get_with_retry(
                api_url, auth=auth, params=params, endpoint_label=endpoint_label
            )

            if response is None:
                tentativas += 1
                log.warning(
                    "[%s/%s] Retry %s/%s em %s",
                    branch, alias, tentativas, MAX_RETRIES, endpoint_label,
                )
                if tentativas >= MAX_RETRIES:
                    log.error("Máximo de tentativas atingido. Encerrando extração.")
                    break
                continue

            tentativas = 0
            data       = response.json()

            if isinstance(data, list):
                api_data = data
            elif isinstance(data, dict) and response_key:
                api_data = data.get(response_key, [])
            else:
                api_data = data.get("data", []) if isinstance(data, dict) else []

            if not api_data:
                log.info("[%s/%s] Página vazia — paginação concluída.", branch, alias)
                break

            all_data.extend(api_data)
            log.info(
                "[%s/%s] Progresso: %s registros (%s páginas).",
                branch, alias, len(all_data), pagina,
            )

            if len(api_data) < params["take"]:
                log.info("[%s/%s] Última página atingida.", branch, alias)
                break

            params["skip"] += params["take"]
            pagina += 1
            time.sleep(REQUEST_DELAY)

    except KeyboardInterrupt:
        log.warning("Execução interrompida pelo usuário [%s/%s].", branch, alias)
        if all_data:
            _save_partial(all_data, alias, branch)
        log.warning("Checkpoint não atualizado.")
        raise  # propaga para o handler do run_all_branches.py

    log.info("[%s/%s] Extração finalizada: %s registros.", branch, alias, len(all_data))
    return all_data
