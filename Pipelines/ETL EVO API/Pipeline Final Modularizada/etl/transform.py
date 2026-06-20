"""
Estágio de transformação: normalização, limpeza, deduplicação e explode de colunas aninhadas.
"""

import os
import ast
import logging
import pandas as pd

log = logging.getLogger(__name__)


# ── Utilitários ────────────────────────────────────────────────────────────────

def fix_encoding(value) -> str:
    """Corrige encoding corrompido (latin-1 interpretado como utf-8)."""
    if not isinstance(value, str):
        return value
    try:
        return value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def safe_eval(x):
    """Avalia string como literal Python (listas, dicts) quando possível."""
    if not isinstance(x, str):
        return x
    try:
        return ast.literal_eval(x)
    except Exception:
        return x


def is_valid_explode_value(x) -> bool:
    """Retorna True se o valor for válido para explode."""
    if x is None:
        return False
    try:
        if pd.isna(x):
            return False
    except (TypeError, ValueError):
        pass
    if isinstance(x, (list, dict)) and len(x) == 0:
        return False
    if isinstance(x, str) and x.strip() == "":
        return False
    return True


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza nomes de colunas: remove espaços, pontos, acentos e converte para minúsculas."""
    df.columns = [
        col.replace(" ", "_").replace(".", "_").lower()
        for col in df.columns
    ]
    return df


def drop_columns(df: pd.DataFrame, endpoint_cfg: dict) -> pd.DataFrame:
    """Remove colunas configuradas em 'colunas_drop' do endpoint_config.json."""
    colunas_drop = endpoint_cfg.get("colunas_drop") or []
    removed = [c for c in colunas_drop if c in df.columns]
    if removed:
        df = df.drop(columns=removed, errors="ignore")
        log.info("%s colunas removidas: %s", len(removed), removed)
    else:
        log.info("Nenhuma coluna existente para remoção no DataFrame.")
    return df


def apply_regex(df: pd.DataFrame, sub_cfg: dict) -> pd.DataFrame:
    """Aplica substituições regex em colunas configuradas em 'colunas_regex'."""
    for col, cfg in sub_cfg.get("colunas_regex", {}).items():
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(
                cfg["pattern"], cfg["replacement"], regex=True
            ).str.strip()
            log.debug("Regex aplicado em '%s'.", col)
        else:
            log.warning("Coluna '%s' não encontrada para regex.", col)
    return df


def explode_columns(
    df: pd.DataFrame,
    endpoint_cfg: dict,
    id_col: str,
) -> dict[str, pd.DataFrame]:
    """
    Expande colunas aninhadas (listas/dicts) configuradas em 'colunas_explode'.
    Aplica 'colunas_drop' por sub-tabela se configurado em 'sub_tables'.

    Returns:
        Dict mapeando nome da coluna → DataFrame expandido.
    """
    colunas_explode = endpoint_cfg.get("colunas_explode", [])
    sub_tables      = endpoint_cfg.get("sub_tables", {})
    dfs_explodidos  = {}

    for col in colunas_explode:
        col_lower = col.lower()
        if col_lower not in df.columns:
            log.warning("Coluna '%s' não encontrada para explode.", col_lower)
            continue

        df_temp             = df[[id_col, col_lower]].copy()
        df_temp[col_lower]  = df_temp[col_lower].apply(safe_eval)
        df_temp             = df_temp[df_temp[col_lower].apply(is_valid_explode_value)]

        if df_temp.empty:
            log.debug("Coluna '%s' sem dados válidos para explode. Ignorando.", col_lower)
            continue

        df_explodido = df_temp.explode(col_lower).reset_index(drop=True)
        df_explodido = df_explodido[df_explodido[col_lower].notna()]

        df_normalizado = pd.json_normalize(df_explodido[col_lower])
        # Drop case-insensitive: API pode retornar idSale (camelCase) dentro do objeto
        cols_to_drop = [c for c in df_normalizado.columns if c.lower() == id_col]
        if cols_to_drop:
            df_normalizado = df_normalizado.drop(columns=cols_to_drop)
        df_expandido   = pd.concat([df_explodido[[id_col]], df_normalizado], axis=1)
        df_expandido   = normalize_columns(df_expandido)

        # Aplica transformações da sub-tabela se configurado
        sub_cfg = sub_tables.get(col_lower, {})
        if sub_cfg:
            df_expandido = drop_columns(df_expandido, sub_cfg)
            df_expandido = apply_regex(df_expandido, sub_cfg)

        dfs_explodidos[col_lower] = df_expandido
        log.info(
            "Coluna '%s' expandida: %s linhas x %s colunas.",
            col_lower, df_expandido.shape[0], df_expandido.shape[1],
        )

    return dfs_explodidos


# ── Estágio principal ──────────────────────────────────────────────────────────

def transform(
    all_data: list,
    endpoint_cfg: dict,
    arquivo_final: str,
    branch: str,
    is_incremental: bool = True,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """
    Aplica transformações ao dataset extraído.

    Etapas:
        1. json_normalize
        2. Normalização de nomes de colunas
        3. Drop de colunas configuradas
        4. Injeção da coluna 'filial'
        5. Deduplicação (interna + contra histórico se incremental)
        6. Explode de colunas aninhadas

    Args:
        all_data: Registros brutos extraídos.
        endpoint_cfg: Configuração do endpoint.
        arquivo_final: Caminho do CSV histórico para dedup incremental.
        branch: Identificador da filial (ex: 'filial_01').
        is_incremental: Se False, ignora dedup contra CSV histórico.

    Returns:
        Tupla (df_principal, dfs_explodidos).
    """
    df = pd.json_normalize(all_data, sep="_")
    log.info("DataFrame criado: %s linhas x %s colunas.", df.shape[0], df.shape[1])

    df = normalize_columns(df)
    df = df.apply(lambda col: col.map(fix_encoding) if col.dtype == object else col)
    df = drop_columns(df, endpoint_cfg)

    # Injeta coluna de filial para consolidação futura no banco
    df.insert(0, "filial", branch)
    log.debug("Coluna 'filial' inserida com valor '%s'.", branch)

    # Deduplicação
    id_col = endpoint_cfg.get("idField", "").lower()

    if not id_col or id_col not in df.columns:
        log.warning("Coluna '%s' não encontrada. Deduplicação ignorada.", id_col)
        return df, {}

    df.drop_duplicates(subset=[id_col], inplace=True)
    log.debug("Duplicatas internas removidas por '%s'.", id_col)

    if is_incremental and os.path.exists(arquivo_final):
        df_old_ids    = pd.read_csv(arquivo_final, sep=";", usecols=[id_col])
        qtd_antes     = len(df)
        df            = df[~df[id_col].isin(df_old_ids[id_col])]
        qtd_removidas = qtd_antes - len(df)
        if qtd_removidas:
            log.debug("%s registros já existentes removidos.", qtd_removidas)
        else:
            log.debug("Nenhuma duplicata contra histórico detectada.")
    elif not is_incremental:
        log.debug("Carga completa: dedup contra histórico ignorada.")
    else:
        log.warning("Arquivo CSV não existe. Será criado do zero.")

    # Explode de colunas aninhadas
    dfs_explodidos = explode_columns(df, endpoint_cfg, id_col)

    # Remove colunas explodidas do DataFrame principal (já persistidas separadamente)
    colunas_explode = [c.lower() for c in endpoint_cfg.get("colunas_explode", [])]
    df = df.drop(columns=[c for c in colunas_explode if c in df.columns], errors="ignore")

    return df, dfs_explodidos
