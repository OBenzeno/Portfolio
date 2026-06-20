"""
Estágio de carga: persistência do DataFrame em CSV (raw, clean e explodidos).
"""

import os
import logging
import pandas as pd

from pipeline.config import DIR_CLEAN, DIR_EXP, DIR_MERGED, DIR_RAW

log = logging.getLogger(__name__)


# Espelha _RECEIVABLES_RENAME de load_db — aplicado no merge para alinhar colunas ao DB
_DEBTORS_RENAME: dict[str, str] = {
    "idreceivable":     "receivableid",
    "idmemberpayer":    "memberid",
    "idreceivablefrom": "receivableidorigin",
    "idbranchmember":   "branchid",
    "paymenttype_id":   "idpaymenttype",
    "paymenttype_name": "paymenttype",
    "receivingdate":    "paymentdate",
    "registrationdate": "registerdate",
    "ammount":          "debtamount",
    "source":           "paymentorigin",
    "status_name":      "debtstatus",
}


def _enrich_branch_df(df: pd.DataFrame, alias: str, branch: str) -> pd.DataFrame:
    """
    Aplica as mesmas transformações de colunas que a carga no banco usa,
    garantindo que o CSV merged tenha a mesma estrutura do data_warehouse.

    - members: merge de contacts → phone_ddi, phone, email
    - sales:   merge de saleitens → idmembership, idsaleitem, salevalue, etc.
    - debtors: rename de colunas da API para nomenclatura do modelo
    """
    if alias == "members":
        arquivo_contacts = os.path.join(DIR_EXP, f"members_contacts_{branch}.csv")
        if os.path.exists(arquivo_contacts):
            df_c = pd.read_csv(arquivo_contacts, sep=";", encoding="utf-8-sig")
            df_c["description"] = df_c["description"].astype(str).str.strip()
            df_c = df_c[df_c["description"] != ""]
            df_c = df_c.drop_duplicates(subset=["idmember", "contacttype"])
            phones = (
                df_c[df_c["contacttype"].str.lower() == "cellphone"][["idmember", "ddi", "description"]]
                .rename(columns={"ddi": "phone_ddi", "description": "phone"})
            )
            emails = (
                df_c[df_c["contacttype"].str.lower() == "e-mail"][["idmember", "description"]]
                .rename(columns={"description": "email"})
            )
            df = df.merge(phones, on="idmember", how="left")
            df = df.merge(emails, on="idmember", how="left")
        else:
            log.warning("[%s/%s] contacts não encontrado para enrich do merge.", alias, branch)

    elif alias == "sales":
        arquivo_saleitens = os.path.join(DIR_EXP, f"sales_saleitens_{branch}.csv")
        if os.path.exists(arquivo_saleitens):
            df_s = pd.read_csv(arquivo_saleitens, sep=";", encoding="utf-8-sig")
            df_s = df_s.loc[:, ~df_s.columns.duplicated()]
            df = df.merge(df_s, on="idsale", how="left")
        else:
            log.warning("[%s/%s] saleitens não encontrado para enrich do merge.", alias, branch)

    elif alias == "debtors":
        df = df.rename(columns=_DEBTORS_RENAME)

    return df


def save_raw(df: pd.DataFrame, alias: str, branch: str) -> str:
    """
    Salva backup raw antes de qualquer transformação.

    Returns:
        Caminho do arquivo salvo.
    """
    arquivo_raw = f"{DIR_RAW}/{alias}_{branch}_raw.csv"
    df.to_csv(arquivo_raw, index=False, sep=";", encoding="utf-8-sig")
    log.info("Raw salvo em '%s'.", arquivo_raw)
    return arquivo_raw


def load(
    df: pd.DataFrame,
    alias: str,
    branch: str,
    is_incremental: bool,
    dfs_explodidos: dict[str, pd.DataFrame] | None = None,
) -> str:
    """
    Persiste o DataFrame principal e os DataFrames explodidos em CSV.

    Modo incremental: append sem header no CSV principal.
    DataFrames explodidos são sempre sobrescritos (sem histórico incremental).

    Args:
        df: DataFrame transformado e deduplicado.
        alias: Nome do endpoint.
        branch: Identificador da filial.
        is_incremental: True se existir checkpoint prévio.
        dfs_explodidos: Dict de DataFrames com colunas expandidas.

    Returns:
        Caminho do arquivo principal salvo.
    """
    arquivo = f"{DIR_CLEAN}/{alias}_{branch}.csv"

    if df.empty:
        log.warning("[%s/%s] DataFrame vazio. Nenhum registro exportado.", branch, alias)
    else:
        if is_incremental and os.path.exists(arquivo):
            df.to_csv(arquivo, mode="a", header=False, index=False, sep=";", encoding="utf-8-sig")
        else:
            df.to_csv(arquivo, index=False, sep=";", encoding="utf-8-sig")
        log.info("[%s/%s] %s registros exportados para '%s'.", branch, alias, len(df), arquivo)

    # Salva DataFrames explodidos
    for col_nome, df_exp in (dfs_explodidos or {}).items():
        arquivo_exp = f"{DIR_EXP}/{alias}_{col_nome}_{branch}.csv"
        df_exp.to_csv(arquivo_exp, index=False, sep=";", encoding="utf-8-sig")
        log.info(
            "[%s/%s] Expandido '%s' salvo em '%s'.",
            branch, alias, col_nome, arquivo_exp,
        )

    return arquivo


def merge_branches(alias: str, branches: list[str]) -> str | None:
    """
    Concatena os CSVs por filial de um mesmo endpoint em um único arquivo.

    Filiais sem arquivo em disco são ignoradas com aviso.

    Args:
        alias: Nome do endpoint.
        branches: Lista de identificadores de filiais.

    Returns:
        Caminho do arquivo merged, ou None se nenhum CSV foi encontrado.
    """
    presentes = []
    ausentes  = []
    for branch in branches:
        path = os.path.join(DIR_CLEAN, f"{alias}_{branch}.csv")
        if os.path.exists(path):
            presentes.append((branch, path))
        else:
            ausentes.append(branch)

    if ausentes:
        log.warning("[%s] Filiais ausentes no merge: %s", alias, ausentes)

    if not presentes:
        log.warning("[%s] Nenhum CSV encontrado. Merge ignorado.", alias)
        return None

    dfs = []
    for branch, path in presentes:
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
        df = _enrich_branch_df(df, alias, branch)
        dfs.append(df)
    merged = pd.concat(dfs, ignore_index=True)

    if merged.empty:
        log.warning("[%s] Merged resultou vazio. Arquivo não gerado.", alias)
        return None

    if "filial" in merged.columns:
        merged = merged.drop(columns=["filial"])

    output = os.path.join(DIR_MERGED, f"{alias}_merged.csv")
    merged.to_csv(output, index=False, sep=";", encoding="utf-8-sig")
    log.info(
        "[%s] Merge concluído: %s registros de %s filiais → '%s'.",
        alias, len(merged), len(presentes), output,
    )
    return output
