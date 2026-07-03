"""
Orquestrador da pipeline ETL — unidade atômica: um endpoint × uma filial.

Fluxo (operacao='full'):
    1. Validação do alias e da filial
    2. Carregamento de configuração (endpoint_config.json)
    3. Criação de diretórios de saída
    4. Checkpoint → datas de extração
    5. Extract → Transform → Load CSV → Load DB
    6. Atualização do checkpoint

operacao='extract_only': steps 1–8 (sem Load DB e sem checkpoint)
operacao='db_only':       steps 1–3 + leitura dos CSVs limpos + Load DB
"""

import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# Garante que o diretório pai esteja no sys.path
# permitindo rodar diretamente de dentro da pasta pipeline/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.logger import setup_logging
from pipeline.config import (
    ENDPOINT_ALIASES,
    BRANCHES,
    BRANCHES_AUTH,
    OUTPUT_DIRS,
    DEFAULT_DATE_START,
    DIR_CLEAN,
    DIR_EXP,
)
from pipeline.checkpoint import load_checkpoint, save_checkpoint
from pipeline.etl.extract import extract
from pipeline.etl.transform import transform
from pipeline.etl.load import save_raw, load
from pipeline.etl.load_db import load_db, init_db

setup_logging()
log = logging.getLogger(__name__)


def _build_params(endpoint_cfg: dict, date_start: str | None, date_end: str) -> dict:
    params = {
        "idBranch": endpoint_cfg.get("idBranch"),
        "take":     endpoint_cfg["take"],
        "skip":     endpoint_cfg["skip"],
    }
    params = {k: v for k, v in params.items() if v is not None}

    if date_start and endpoint_cfg.get("dateStartKey"):
        params[endpoint_cfg["dateStartKey"]] = date_start

    if date_end and endpoint_cfg.get("dateEndKey"):
        params[endpoint_cfg["dateEndKey"]] = date_end

    return params


def _load_from_csv(alias: str, branch: str) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """
    Lê o CSV limpo existente para carga direta no banco (operacao='db_only').

    Returns:
        (df_principal, dfs_explodidos) — dfs_explodidos contém 'saleitens'
        apenas para o alias 'sales', se o arquivo existir.
    """
    arquivo_clean = os.path.join(DIR_CLEAN, f"{alias}_{branch}.csv")
    if not os.path.exists(arquivo_clean):
        log.error("[%s/%s] CSV limpo não encontrado: '%s'.", branch, alias, arquivo_clean)
        raise SystemExit(1)

    df = pd.read_csv(arquivo_clean, sep=";", encoding="utf-8-sig")
    log.info("[%s/%s] CSV carregado: %s linhas.", branch, alias, len(df))

    dfs_explodidos: dict[str, pd.DataFrame] = {}

    if alias == "members":
        arquivo_contacts = os.path.join(DIR_EXP, f"members_contacts_{branch}.csv")
        if os.path.exists(arquivo_contacts):
            dfs_explodidos["contacts"] = pd.read_csv(
                arquivo_contacts, sep=";", encoding="utf-8-sig"
            )
            log.info(
                "[%s/members] contacts carregado: %s linhas.",
                branch, len(dfs_explodidos["contacts"]),
            )
        else:
            log.warning("[%s/members] CSV de contacts não encontrado. phone/email serão nulos.", branch)

    elif alias == "sales":
        arquivo_saleitens = os.path.join(DIR_EXP, f"sales_saleitens_{branch}.csv")
        if os.path.exists(arquivo_saleitens):
            dfs_explodidos["saleitens"] = pd.read_csv(
                arquivo_saleitens, sep=";", encoding="utf-8-sig"
            )
            log.info(
                "[%s/sales] saleitens carregado: %s linhas.",
                branch, len(dfs_explodidos["saleitens"]),
            )
        else:
            log.warning("[%s/sales] CSV de saleitens não encontrado. Campos de itens serão nulos.", branch)

    return df, dfs_explodidos


def run(alias: str, branch: str, operacao: str = "full") -> None:
    """
    Executa o ETL para um endpoint e uma filial.

    Args:
        alias:    Chave do endpoint (ex: 'sales').
        branch:   Identificador da filial (ex: 'filial_01').
        operacao: Modo de operação:
                    'full'         — extração + transform + CSV + DB
                    'extract_only' — extração + transform + CSV (sem DB)
                    'db_only'      — lê CSVs existentes e carrega no DB
    """
    # ── 1. Validação ───────────────────────────────────────────────────────────
    if alias not in ENDPOINT_ALIASES or not ENDPOINT_ALIASES[alias]:
        log.error("Alias '%s' não reconhecido ou URL não configurada no .env.", alias)
        raise SystemExit(1)

    if branch not in BRANCHES_AUTH:
        log.error("Filial '%s' não encontrada em branches.json.", branch)
        raise SystemExit(1)

    branch_nome = BRANCHES[branch].get("nome", branch)
    log.info("Iniciando [%s | %s | operacao=%s]", branch_nome, alias, operacao)

    # ── 2. Configuração do endpoint ────────────────────────────────────────────
    _cfg_path = os.path.join(os.path.dirname(__file__), "config", "endpoint_config.json")
    with open(_cfg_path, "r", encoding="utf-8") as f:
        endpoint_cfg: dict = json.load(f)[alias]

    branch_override = endpoint_cfg.pop("branches", {}).get(branch, {})
    endpoint_cfg    = {**endpoint_cfg, **branch_override}

    # ── 3. Diretórios de saída ─────────────────────────────────────────────────
    for d in OUTPUT_DIRS:
        os.makedirs(d, exist_ok=True)

    # ── db_only: lê CSVs existentes e carrega no banco ─────────────────────────
    if operacao == "db_only":
        df, dfs_explodidos = _load_from_csv(alias, branch)
        load_db(alias, df, dfs_explodidos=dfs_explodidos)
        log.info("[%s/%s] Carga DB concluída (db_only).", branch, alias)
        return

    # ── 4. Checkpoint e datas ──────────────────────────────────────────────────
    api_url        = ENDPOINT_ALIASES[alias]
    assert api_url is not None
    auth           = BRANCHES_AUTH[branch]
    endpoint_label = "/" + "/".join(api_url.split("/")[3:])

    checkpoint     = load_checkpoint(alias, branch)
    date_end       = datetime.now(ZoneInfo("America/Fortaleza")).strftime("%Y-%m-%dT%H:%M:%S")
    date_start     = checkpoint.get("last_run") or DEFAULT_DATE_START
    is_incremental = checkpoint.get("last_run") is not None

    if is_incremental:
        log.info("[%s/%s] Carga incremental: de %s até %s", branch, alias, date_start, date_end)
    else:
        log.info("[%s/%s] Primeira execução: de %s até %s", branch, alias, date_start, date_end)

    # ── 5. Extract ─────────────────────────────────────────────────────────────
    params   = _build_params(endpoint_cfg, date_start, date_end)
    all_data = extract(api_url, auth, params, endpoint_cfg, alias, branch, endpoint_label)

    if not all_data:
        log.warning("[%s/%s] Nenhum dado coletado. Verifique a API e as credenciais.", branch, alias)
        return

    # ── 6. Raw backup ──────────────────────────────────────────────────────────
    df_raw = pd.json_normalize(all_data, sep="_")
    save_raw(df_raw, alias, branch)

    # ── 7. Transform ───────────────────────────────────────────────────────────
    arquivo_clean      = f"{DIR_CLEAN}/{alias}_{branch}.csv"
    df, dfs_explodidos = transform(all_data, endpoint_cfg, arquivo_clean, branch, is_incremental)

    # ── 8. Load CSV (backup) ───────────────────────────────────────────────────
    load(df, alias, branch, is_incremental, dfs_explodidos)

    # ── 9. Load DB ─────────────────────────────────────────────────────────────
    if operacao == "full":
        load_db(alias, df, dfs_explodidos=dfs_explodidos)

    # ── 10. Checkpoint ─────────────────────────────────────────────────────────
    save_checkpoint(alias, branch, date_end)
    log.info("[%s/%s] Concluído.", branch, alias)
