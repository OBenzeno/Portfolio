"""
Executa o ETL para filiais e endpoints configurados.

Modos:
    Automático — percorre todas as combinações filial × endpoint sem interrupção,
                 com handler SIGINT para cancelamento granular.
    Manual     — seleção interativa de filial e endpoint via menu questionary,
                 com handler SIGINT para encerramento imediato.

Operações:
    full         — Extract → Transform → Load CSV → Load DB
    extract_only — Extract → Transform → Load CSV  (sem ingestão no banco)
    db_only      — Lê CSVs existentes e carrega direto no banco
"""

import os
import sys

# Garante que o diretório pai esteja no sys.path
# permitindo rodar diretamente de dentro da pasta pipeline/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import signal
import logging
import questionary
from pipeline.logger import setup_logging
from pipeline.config import BRANCHES, ENDPOINT_ALIASES, DIR_CHECKPOINTS
from pipeline.main import run
from pipeline.etl.load import merge_branches
from pipeline.etl.load_db import init_db

setup_logging()
log = logging.getLogger(__name__)


# ==============================================================================
#  Seleção de modo e operação
# ==============================================================================

def _selecionar_modo() -> str:
    """Retorna 'Automático' ou 'Manual'."""
    return questionary.select(
        "Selecione o modo de execução:",
        choices=["Automático", "Manual"],
    ).ask()


def _selecionar_operacao() -> str:
    """Retorna 'full', 'extract_only' ou 'db_only'."""
    escolha = questionary.select(
        "Selecione a operação:",
        choices=[
            "Extração + Carga DB",
            "Extração apenas",
            "Carga DB apenas",
        ],
    ).ask()
    return {
        "Extração + Carga DB": "full",
        "Extração apenas":     "extract_only",
        "Carga DB apenas":     "db_only",
    }[escolha]


# ==============================================================================
#  Modo automático
# ==============================================================================

def _executar_automatico(
    branches: list[str],
    endpoints: list[str],
    operacao: str,
) -> None:
    """
    Percorre todas as combinações filial × endpoint automaticamente.
    Suporta cancelamento granular via SIGINT (Ctrl+C).
    Ao final, mescla CSVs por endpoint (exceto em modo db_only).
    """
    total       = len(branches) * len(endpoints)
    concluido   = 0
    falhas      = []
    _concluidos = []

    _cancel_current = False
    _cancel_branch  = False
    _cancel_all     = False
    _last_branch    = ""
    _last_alias     = ""

    def _sigint_handler(sig, frame):
        nonlocal _cancel_current, _cancel_branch, _cancel_all
        escolha = questionary.select(
            "Pipeline interrompida. O que deseja fazer?",
            choices=[
                "Cancelar endpoint atual",
                "Cancelar filial atual",
                "Cancelar toda a pipeline",
                "Continuar",
            ]
        ).ask()
        if escolha == "Cancelar endpoint atual":
            _cancel_current = True
            raise KeyboardInterrupt
        elif escolha == "Cancelar filial atual":
            _cancel_branch = True
            raise KeyboardInterrupt
        elif escolha == "Cancelar toda a pipeline":
            _cancel_all = True
            raise KeyboardInterrupt
        # "Continuar" → retorna sem raise

    signal.signal(signal.SIGINT, _sigint_handler)

    for branch in branches:
        _cancel_branch = False
        for alias in endpoints:
            _cancel_current = False
            _last_branch    = branch
            _last_alias     = alias
            log.info("─" * 60)
            try:
                run(alias, branch, operacao=operacao)
                concluido += 1
                _concluidos.append((alias, branch))
            except KeyboardInterrupt:
                pass
            except SystemExit:
                log.error("Falha em [%s/%s]. Continuando para o próximo.", branch, alias)
                falhas.append((branch, alias))
            except Exception as e:
                log.exception("Erro inesperado em [%s/%s]: %s", branch, alias, e)
                falhas.append((branch, alias))

            if _cancel_current:
                log.warning("Endpoint [%s/%s] cancelado pelo usuário.", branch, alias)
                falhas.append((branch, alias))
            if _cancel_branch:
                log.warning("Filial [%s] cancelada pelo usuário.", branch)
                falhas.append((branch, alias))
                break
            if _cancel_all:
                log.warning("Pipeline cancelada pelo usuário.")
                break

        if _cancel_all:
            break

    # Gestão de checkpoints ao cancelar
    if _cancel_all:
        _opcao_ckpt = questionary.select(
            "Deseja manter os checkpoints salvos?",
            choices=[
                "Manter todos",
                f"Deletar apenas o atual  [{_last_branch}/{_last_alias}]",
                "Deletar todos da sessão atual",
            ]
        ).ask()

        if _opcao_ckpt and _opcao_ckpt.startswith("Deletar apenas"):
            ckpt = os.path.join(DIR_CHECKPOINTS, f"checkpoint_{_last_alias}_{_last_branch}.json")
            if os.path.exists(ckpt):
                os.remove(ckpt)
                log.info("Checkpoint [%s/%s] removido.", _last_branch, _last_alias)
            else:
                log.info("Nenhum checkpoint encontrado para [%s/%s].", _last_branch, _last_alias)

        elif _opcao_ckpt == "Deletar todos da sessão atual":
            removidos = 0
            for _alias, _branch in _concluidos:
                ckpt = os.path.join(DIR_CHECKPOINTS, f"checkpoint_{_alias}_{_branch}.json")
                if os.path.exists(ckpt):
                    os.remove(ckpt)
                    removidos += 1
            log.info("%s checkpoint(s) da sessão removido(s).", removidos)

    log.info("=" * 60)
    if _cancel_all or operacao == "db_only":
        if _cancel_all:
            log.warning("Merge ignorado: pipeline cancelada pelo usuário.")
        else:
            log.info("Merge ignorado: operação db_only não gera novos CSVs.")
    else:
        log.info("Iniciando merge por endpoint...")
        for alias in endpoints:
            merge_branches(alias, branches)

    log.info("=" * 60)
    log.info("Pipeline finalizada: %s/%s combinações concluídas.", concluido, total)

    if falhas:
        log.warning("Falhas registradas:")
        for branch, alias in falhas:
            log.warning("  → [%s/%s]", branch, alias)
    else:
        log.info("Todas as combinações concluídas sem falhas.")


# ==============================================================================
#  Modo manual
# ==============================================================================

def _executar_manual(
    branches: list[str],
    endpoints: list[str],
    operacao: str,
) -> None:
    """
    Seleção interativa de filial e endpoint via menu.
    Repete até o usuário escolher sair ou pressionar Ctrl+C.
    """
    _encerrar = False

    def _sigint_handler(sig, frame):
        nonlocal _encerrar
        confirmar = questionary.confirm(
            "Deseja encerrar o modo manual?", default=True
        ).ask()
        if confirmar:
            _encerrar = True
            raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _sigint_handler)

    while not _encerrar:
        try:
            branch = questionary.select(
                "Selecione a filial:",
                choices=branches + ["← Sair"],
            ).ask()

            if branch == "← Sair" or branch is None:
                log.info("Modo manual encerrado pelo usuário.")
                break

            alias = questionary.select(
                f"Selecione o endpoint para [{branch}]:",
                choices=endpoints + ["← Voltar"],
            ).ask()

            if alias == "← Voltar" or alias is None:
                continue

            log.info("─" * 60)
            try:
                run(alias, branch, operacao=operacao)
            except SystemExit:
                log.error("Falha em [%s/%s].", branch, alias)
            except Exception as e:
                log.exception("Erro inesperado em [%s/%s]: %s", branch, alias, e)

            continuar = questionary.confirm("Executar outra combinação?", default=True).ask()
            if not continuar:
                log.info("Modo manual encerrado pelo usuário.")
                break

        except KeyboardInterrupt:
            if _encerrar:
                log.info("Modo manual encerrado via Ctrl+C.")
            break


# ==============================================================================
#  Orquestrador principal
# ==============================================================================

def run_all() -> None:
    branches  = list(BRANCHES.keys())
    endpoints = [alias for alias, url in ENDPOINT_ALIASES.items() if url]

    log.info("Filiais disponíveis: %s", branches)
    log.info("Endpoints disponíveis: %s", endpoints)

    modo = _selecionar_modo()
    if modo is None:
        log.info("Execução cancelada.")
        return

    operacao = _selecionar_operacao()
    if operacao is None:
        log.info("Execução cancelada.")
        return

    if operacao in ("full", "db_only"):
        init_db()

    if modo == "Manual":
        _executar_manual(branches, endpoints, operacao)
    else:
        log.info("Iniciando pipeline automática.")
        _executar_automatico(branches, endpoints, operacao)


if __name__ == "__main__":
    run_all()
