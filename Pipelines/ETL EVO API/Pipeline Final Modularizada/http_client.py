"""
Cliente HTTP com retry automático e backoff exponencial.
"""

import time
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout, ConnectionError, HTTPError, ChunkedEncodingError

from pipeline.config import MAX_RETRIES, RETRY_CODES, TIMEOUT

log = logging.getLogger(__name__)


def sleep_backoff(attempt: int) -> None:
    """Espera exponencial: 2s, 4s, 8s, 16s..."""
    wait = 2 ** attempt
    log.warning("Aguardando %ss antes de tentar novamente...", wait)
    time.sleep(wait)


def get_with_retry(
    url: str,
    auth: HTTPBasicAuth,
    params: dict | None = None,
    endpoint_label: str = "",
) -> requests.Response | None:
    """
    Executa GET com retry e backoff exponencial.

    Args:
        url: URL completa do endpoint.
        auth: Credenciais HTTPBasicAuth da filial.
        params: Query params da requisição.
        endpoint_label: Rótulo para logs (ex: '/api/sales').

    Returns:
        Response com status 200, ou None em caso de falha definitiva.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, auth=auth, params=params, timeout=TIMEOUT)

            if response.status_code == 200:
                return response

            if response.status_code == 401:
                log.error("Erro 401 — credenciais inválidas.")
                return None

            if response.status_code == 404:
                log.warning("Erro 404 — recurso não encontrado: %s", endpoint_label)
                return None

            if response.status_code in RETRY_CODES:
                log.warning("Código %s recebido.", response.status_code)
                if attempt < MAX_RETRIES - 1:
                    sleep_backoff(attempt)
                continue

            log.error("Erro HTTP %s: %s", response.status_code, response.text[:300])
            return None

        except Timeout:
            log.warning("Timeout na requisição.")
            if attempt < MAX_RETRIES - 1:
                sleep_backoff(attempt)

        except ConnectionError as e:
            log.warning("Erro de conexão: %s", e)
            if attempt < MAX_RETRIES - 1:
                sleep_backoff(attempt)

        except ChunkedEncodingError:
            log.warning("Resposta encerrada prematuramente (ChunkedEncodingError).")
            if attempt < MAX_RETRIES - 1:
                sleep_backoff(attempt)

        except HTTPError as e:
            log.exception("HTTPError: %s", e)
            return None

    log.warning("Falha definitiva após %s tentativas.", MAX_RETRIES)
    return None
