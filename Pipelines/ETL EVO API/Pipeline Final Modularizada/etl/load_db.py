"""
Estágio de carga para o banco de dados via SQLAlchemy Core.

Fluxo por execução:
    1. Garante que os schemas e tabelas existam
    2. Upsert no schema 'db_raw'        — dump flat sem transformação adicional
    3. Upsert no schema 'data_warehouse' — modelo normalizado, na ordem correta de FK

Cada tabela usa ON CONFLICT DO UPDATE (upsert) pela sua chave primária,
garantindo idempotência na carga incremental.
"""

import logging
import math
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Integer, String

from pipeline.etl.db_connection import get_engine
from pipeline.etl.db_schema import (
    raw_meta, relational_meta, RELATIONAL_TABLE_ORDER,
    # raw
    raw_members, raw_sales, raw_debtors,
    # relational dims lookup
    rel_dim_branch, rel_dim_employee, rel_dim_planos, rel_dim_payment_type,
    # relational dim principal + satélites
    rel_members, rel_dim_address, rel_dim_partnerships,
    # relational fatos
    rel_sales, rel_debtors,
)

log = logging.getLogger(__name__)


# ==============================================================================
#  Mapeamento de colunas: API receivables → modelo debtors
# ==============================================================================

# A API retorna nomes no padrão da plataforma (idReceivable, idMemberPayer, etc.).
# O modelo relacional usa a nomenclatura de negócio (receivableid, memberid, etc.).
# A renomeação ocorre apenas no momento do load no banco — o CSV de backup
# preserva os nomes originais da API para fins de auditoria.
_RECEIVABLES_RENAME: dict[str, str] = {
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


# ==============================================================================
#  Utilitários
# ==============================================================================

def _upsert(engine: Engine, table, rows: list[dict], pk_cols: list[str]) -> int:
    """
    Executa upsert em lote em uma tabela.

    Colunas não-PK são atualizadas em caso de conflito.
    Linhas com PK nula são descartadas com aviso.

    Args:
        engine:   Engine SQLAlchemy.
        table:    Objeto Table do SQLAlchemy Core.
        rows:     Lista de dicts com os dados a inserir.
        pk_cols:  Colunas que formam a chave de conflito.

    Returns:
        Número de linhas processadas.
    """
    if not rows:
        log.warning("[%s] Nenhuma linha para upsert.", table.name)
        return 0

    # Remove linhas com PK nula
    valid = [r for r in rows if all(r.get(pk) is not None for pk in pk_cols)]
    skipped = len(rows) - len(valid)
    if skipped:
        log.warning("[%s] %s linha(s) descartada(s) por PK nula.", table.name, skipped)
    if not valid:
        return 0

    # Deduplica por PK (PostgreSQL rejeita duplicatas de chave na mesma query)
    seen: dict = {}
    for r in valid:
        key = tuple(r.get(pk) for pk in pk_cols)
        seen[key] = r
    dedup_skipped = len(valid) - len(seen)
    if dedup_skipped:
        log.warning("[%s] %s linha(s) duplicada(s) removidas antes do upsert.", table.name, dedup_skipped)
    valid = list(seen.values())

    # Corrige float→int para colunas Integer e float→str para colunas String
    valid = _coerce_types(table, valid)

    # PKs reais da tabela que NÃO são o conflict target (ex: idaddress em dim_address).
    # Devem ser removidas dos rows antes do INSERT — o banco gera o valor via sequence.
    # Incluí-las como NULL causaria NotNullViolation na PK.
    table_pk_names = {c.name for c in table.columns if c.primary_key}
    extra_pk_names = table_pk_names - set(pk_cols)
    if extra_pk_names:
        valid = [{k: v for k, v in row.items() if k not in extra_pk_names} for row in valid]

    # Colunas atualizáveis: todas menos o conflict target E as PKs reais da tabela.
    update_cols = [
        c.name for c in table.columns
        if c.name not in pk_cols and c.name not in table_pk_names
    ]

    # PostgreSQL limita a 32.767 parâmetros por query.
    # Calculamos o tamanho máximo do lote para não ultrapassar esse limite.
    n_cols    = len(table.columns)
    BATCH_SIZE = max(1, 32000 // n_cols)

    total = 0
    try:
        with engine.begin() as conn:
            for i in range(0, len(valid), BATCH_SIZE):
                batch = valid[i : i + BATCH_SIZE]
                stmt  = insert(table).values(batch)
                if update_cols:
                    stmt = stmt.on_conflict_do_update(
                        index_elements=pk_cols,
                        set_={col: stmt.excluded[col] for col in update_cols},
                    )
                else:
                    stmt = stmt.on_conflict_do_nothing(index_elements=pk_cols)
                conn.execute(stmt)
                total += len(batch)
    except SQLAlchemyError as e:
        orig = getattr(e, "orig", e)
        log.error(
            "[%s] %s — tipo: %s | detalhe: %s",
            table.name,
            type(e).__name__,
            type(orig).__name__,
            str(orig).splitlines()[0],
        )
        raise

    log.info("[%s] %s registros processados (upsert).", table.name, total)
    return total


def _df_to_rows(df: pd.DataFrame, columns: list[str]) -> list[dict]:
    """
    Filtra e converte DataFrame para lista de dicts com as colunas da tabela.
    Colunas ausentes no DataFrame são ignoradas (ficam como None).
    """
    present = [c for c in columns if c in df.columns]
    subset  = df[present].copy()

    # Garante que colunas faltando existam como None
    for col in columns:
        if col not in subset.columns:
            subset[col] = None

    subset = subset[columns]
    # Converte para object dtype antes do where para garantir que NaN vire
    # Python None (colunas float64 mantêm nan mesmo após where(..., None)).
    subset = subset.astype(object).where(pd.notna(subset), None)
    return subset.to_dict(orient="records")


def _table_columns(table) -> list[str]:
    return [c.name for c in table.columns]


def _coerce_types(table, rows: list[dict]) -> list[dict]:
    """
    Corrige tipos Python antes do envio ao PostgreSQL.

    Pandas mantém colunas como float64 quando há NaN, mesmo para campos
    originalmente inteiros. Após o NaN→None, valores como 1.0 / 55.0
    permanecem como float e precisam ser convertidos:

      - Coluna Integer: float → int   (ex: idemployeeconsultant: 1.0 → 1)
      - Coluna String:  float inteiro → str sem decimal  (ex: phone_ddi: 55.0 → "55")
    """
    int_cols    = {c.name for c in table.columns if isinstance(c.type, Integer)}
    string_cols = {c.name for c in table.columns if isinstance(c.type, String)}

    if not int_cols and not string_cols:
        return rows

    result = []
    for row in rows:
        new_row = {}
        for k, v in row.items():
            if v is None:
                new_row[k] = v
            elif k in int_cols and isinstance(v, float):
                new_row[k] = int(v)
            elif k in string_cols and isinstance(v, int):
                new_row[k] = str(v)
            elif k in string_cols and isinstance(v, float) and math.isfinite(v) and v == int(v):
                new_row[k] = str(int(v))
            else:
                new_row[k] = v
        result.append(new_row)
    return result


# ==============================================================================
#  Inicialização do banco
# ==============================================================================

def init_db() -> Engine:
    """
    Garante que schemas e todas as tabelas existam no banco.
    Deve ser chamado uma vez antes do primeiro load.
    """
    from sqlalchemy import text
    engine = get_engine()
    raw_meta.create_all(engine, checkfirst=True)
    # Cria tabelas relacionais na ordem correta de FK
    for table in RELATIONAL_TABLE_ORDER:
        table.metadata.create_all(engine, tables=[table], checkfirst=True)
    # Migração: adiciona colunas que podem não existir em tabelas criadas anteriormente
    _migrate_columns(engine)
    # Seed: garante nomes de filiais conhecidas em dim_branch
    _seed_dim_branch(engine)
    log.info("Schemas e tabelas verificados/criados.")
    return engine


# IDs de filial conhecidos da API → nome legível.
# Garante que dim_branch tenha nomes mesmo quando a fonte de dados não os envia.
_BRANCH_SEEDS: dict[int, str] = {
    60:  "Jardim Cambui",
    327: "Santa Helena",
}


def _seed_dim_branch(engine) -> None:
    """
    Upsert de registros conhecidos em dim_branch.
    Usa ON CONFLICT DO UPDATE para sobrescrever nomes nulos sem duplicar linhas.
    Chamado por init_db() após create_all() e _migrate_columns().
    """
    rows = [{"branchid": bid, "branchname": name} for bid, name in _BRANCH_SEEDS.items()]
    _upsert(engine, rel_dim_branch, rows, ["branchid"])
    log.info("Seed de dim_branch concluído: %s filiais.", len(rows))


def _migrate_columns(engine) -> None:
    """
    Adiciona colunas que foram incluídas no schema após a criação inicial das tabelas.
    Usa ADD COLUMN IF NOT EXISTS — seguro para rodar múltiplas vezes.
    """
    from sqlalchemy import text
    migrations = [
        # Colunas adicionadas ao members após criação inicial
        "ALTER TABLE data_warehouse.members ADD COLUMN IF NOT EXISTS phone_ddi VARCHAR(10)",
        "ALTER TABLE data_warehouse.members ADD COLUMN IF NOT EXISTS phone    VARCHAR(50)",
        "ALTER TABLE data_warehouse.members ADD COLUMN IF NOT EXISTS email    VARCHAR(255)",
        # Unique constraint em dim_address necessária para ON CONFLICT (idmember)
        """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_address_member'
            ) THEN
                ALTER TABLE data_warehouse.dim_address
                ADD CONSTRAINT uq_address_member UNIQUE (idmember);
            END IF;
        END $$
        """,
        # Colunas de tempo separadas — members
        "ALTER TABLE data_warehouse.members ADD COLUMN IF NOT EXISTS registertime    TIME",
        "ALTER TABLE data_warehouse.members ADD COLUMN IF NOT EXISTS updatetime      TIME",
        "ALTER TABLE data_warehouse.members ADD COLUMN IF NOT EXISTS lastaccesstime  TIME",
        "ALTER TABLE data_warehouse.members ADD COLUMN IF NOT EXISTS conversiontime  TIME",
        # Colunas de tempo separadas — sales
        "ALTER TABLE data_warehouse.sales ADD COLUMN IF NOT EXISTS saletime   TIME",
        "ALTER TABLE data_warehouse.sales ADD COLUMN IF NOT EXISTS updatetime TIME",
        # Colunas de tempo separadas — debtors
        "ALTER TABLE data_warehouse.debtors ADD COLUMN IF NOT EXISTS registertime TIME",
        # dim_partnerships — PK surrogate e unique constraint
        """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data_warehouse'
                AND table_name    = 'dim_partnerships'
                AND column_name   = 'idpartnership'
            ) THEN
                ALTER TABLE data_warehouse.dim_partnerships
                    DROP CONSTRAINT IF EXISTS dim_partnerships_idmember_plataforma_pkey,
                    DROP CONSTRAINT IF EXISTS partnerships_pkey;
                ALTER TABLE data_warehouse.dim_partnerships
                    ADD COLUMN idpartnership SERIAL PRIMARY KEY;
            END IF;
        END $$
        """,
        """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_partnerships'
            ) THEN
                ALTER TABLE data_warehouse.dim_partnerships
                ADD CONSTRAINT uq_partnerships UNIQUE (idmember, plataforma);
            END IF;
        END $$
        """,
    ]
    with engine.begin() as conn:
        for stmt in migrations:
            conn.execute(text(stmt))
    log.info("Migração de colunas concluída.")


# ==============================================================================
#  Utilitário de merge para sales
# ==============================================================================

def _merge_saleitens(
    df: pd.DataFrame,
    df_saleitens: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Re-mergeia o DataFrame de saleitens no df principal de sales.

    O transform explode saleitens e remove do df principal para o CSV.
    Para o DB precisamos dos campos (idmembership, idsaleitem, salevalue, etc.)
    de volta no df antes do upsert.

    Se df_saleitens for None (endpoint sem dados de saleitens), retorna df original.
    """
    if df_saleitens is None or df_saleitens.empty:
        log.warning("[sales] saleitens ausente — campos de itens serão nulos no DB.")
        return df

    # Salvaguarda: remove colunas duplicadas que possam ter escapado do transform
    df_s = df_saleitens.loc[:, ~df_saleitens.columns.duplicated()]

    df_merged = df.merge(df_s, on="idsale", how="left")
    log.info(
        "[sales] Merge saleitens: %s → %s linhas, %s colunas.",
        len(df), len(df_merged), len(df_merged.columns),
    )
    return df_merged


# ==============================================================================
#  Carga raw (flat, sem normalização adicional)
# ==============================================================================

def load_raw_members(df: pd.DataFrame, engine: Engine) -> None:
    rows = _df_to_rows(df, _table_columns(raw_members))
    _upsert(engine, raw_members, rows, ["idmember"])


def load_raw_sales(df: pd.DataFrame, engine: Engine) -> None:
    rows = _df_to_rows(df, _table_columns(raw_sales))
    _upsert(engine, raw_sales, rows, ["idsale"])


def load_raw_debtors(df: pd.DataFrame, engine: Engine) -> None:
    rows = _df_to_rows(df, _table_columns(raw_debtors))
    _upsert(engine, raw_debtors, rows, ["receivableid"])


# ==============================================================================
#  Carga relational — dims extraídas do DataFrame de members
# ==============================================================================

def _extract_dim_branch(df: pd.DataFrame) -> pd.DataFrame:
    """Extrai pares únicos (idbranch, branchname) do DataFrame."""
    cols = [c for c in ["idbranch", "branchname"] if c in df.columns]
    return df[cols].drop_duplicates(subset=["idbranch"]).rename(
        columns={"idbranch": "branchid"}
    )


def _extract_dim_employee(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai funcionários únicos do DataFrame de members.
    Consolida consultores e instrutores em uma única dimensão.
    Colunas ausentes no DataFrame são ignoradas sem erro.
    """
    frames = []
    if "idemployeeconsultant" in df.columns and "nameemployeeconsultant" in df.columns:
        frames.append(
            df[["idemployeeconsultant", "nameemployeeconsultant"]].rename(
                columns={"idemployeeconsultant": "idemployee", "nameemployeeconsultant": "nameemployee"}
            )
        )
    if "idemployeeinstructor" in df.columns and "nameemployeeinstructor" in df.columns:
        frames.append(
            df[["idemployeeinstructor", "nameemployeeinstructor"]].rename(
                columns={"idemployeeinstructor": "idemployee", "nameemployeeinstructor": "nameemployee"}
            )
        )
    if not frames:
        return pd.DataFrame(columns=["idemployee", "nameemployee"])
    combined = pd.concat(frames, ignore_index=True)
    return combined.dropna(subset=["idemployee"]).drop_duplicates(subset=["idemployee"])


def _extract_dim_planos(df_sales: pd.DataFrame) -> pd.DataFrame:
    """Extrai pares únicos (idmembership, item) do DataFrame de sales."""
    cols = [c for c in ["idmembership", "item"] if c in df_sales.columns]
    if "idmembership" not in cols:
        return pd.DataFrame(columns=["idmembership", "nome_plano"])
    result = df_sales[cols].drop_duplicates(subset=["idmembership"]).dropna(subset=["idmembership"])
    return result.rename(columns={"item": "nome_plano"})


def _extract_dim_address(df: pd.DataFrame) -> pd.DataFrame:
    """Extrai endereço por membro do DataFrame de members."""
    addr_cols = ["idmember", "state", "city", "zipcode", "complement", "number", "country"]
    present   = [c for c in addr_cols if c in df.columns]
    return df[present].drop_duplicates(subset=["idmember"]).dropna(subset=["idmember"])


def _extract_dim_partnerships(df: pd.DataFrame) -> list[dict]:
    """
    Extrai parcerias (gympassid, codetotalpass) por membro.
    Retorna lista de dicts no formato (idmember, plataforma, codigo).
    """
    rows = []
    for _, row in df.iterrows():
        if pd.notna(row.get("gympassid")) and str(row["gympassid"]).strip():
            rows.append({
                "idmember":  row["idmember"],
                "plataforma": "GYMPASS",
                "codigo":     str(row["gympassid"]).strip(),
            })
        if pd.notna(row.get("codetotalpass")) and str(row["codetotalpass"]).strip():
            rows.append({
                "idmember":  row["idmember"],
                "plataforma": "TOTALPASS",
                "codigo":     str(row["codetotalpass"]).strip(),
            })
    return rows


def _merge_contacts(
    df: pd.DataFrame,
    df_contacts: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Pivota o DataFrame de contacts por tipo e merge no df de members.

    Tipos mapeados:
        Cellphone → phone_ddi, phone
        E-mail    → email

    Duplicatas por (idmember, contacttype) são resolvidas mantendo
    o primeiro registro não-vazio (strip de espaços).
    """
    if df_contacts is None or df_contacts.empty:
        log.warning("[members] contacts ausente — phone/email serão nulos no DB.")
        return df

    df_c = df_contacts.copy()
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
    log.info("[members] contacts mergeados: %s registros.", len(df))
    return df


# ==============================================================================
#  Carga relational — funções públicas por tabela
# ==============================================================================

def _load_dim_branch_from_sales(df_sales: pd.DataFrame, engine: Engine) -> None:
    """
    Garante que os branchids presentes em df_sales existam em dim_branch
    antes do upsert de rel_sales (evita FK violation).
    Se branchname não estiver disponível no df, insere só o id (nome nulo).
    """
    if "idbranch" not in df_sales.columns:
        return
    cols = [c for c in ["idbranch", "branchname"] if c in df_sales.columns]
    df = df_sales[cols].drop_duplicates(subset=["idbranch"]).dropna(subset=["idbranch"])
    df = df.rename(columns={"idbranch": "branchid"})
    rows = _df_to_rows(df, _table_columns(rel_dim_branch))
    _upsert(engine, rel_dim_branch, rows, ["branchid"])


def _load_dim_employee_from_sales(df_sales: pd.DataFrame, engine: Engine) -> None:
    """
    Garante que os idemployeesale presentes em df_sales existam em dim_employee
    antes do upsert de rel_sales (evita FK violation).
    """
    if "idemployeesale" not in df_sales.columns:
        return
    cols = [c for c in ["idemployeesale", "nameemployeesale"] if c in df_sales.columns]
    df = df_sales[cols].drop_duplicates(subset=["idemployeesale"]).dropna(subset=["idemployeesale"])
    df = df.rename(columns={"idemployeesale": "idemployee", "nameemployeesale": "nameemployee"})
    rows = _df_to_rows(df, _table_columns(rel_dim_employee))
    _upsert(engine, rel_dim_employee, rows, ["idemployee"])


def _load_members_stub(ids: list[int], engine: Engine) -> None:
    """
    Insere registros stub em data_warehouse.members para cada idmember fornecido,
    usando ON CONFLICT DO NOTHING para não sobrescrever dados reais já existentes.

    Necessário para satisfazer FKs de rel_sales e rel_debtors quando o alias
    'members' não foi executado antes desses endpoints na mesma sessão.
    """
    if not ids:
        return
    rows = [{"idmember": int(v)} for v in ids]
    with engine.begin() as conn:
        stmt = insert(rel_members).values(rows).on_conflict_do_nothing(index_elements=["idmember"])
        conn.execute(stmt)
    log.info("[members stub] %s idmember(s) garantidos para constraint FK.", len(rows))


def load_rel_dim_branch(df_members: pd.DataFrame, engine: Engine) -> None:
    df  = _extract_dim_branch(df_members)
    rows = _df_to_rows(df, _table_columns(rel_dim_branch))
    _upsert(engine, rel_dim_branch, rows, ["branchid"])


def load_rel_dim_employee(df_members: pd.DataFrame, engine: Engine) -> None:
    df   = _extract_dim_employee(df_members)
    rows = _df_to_rows(df, _table_columns(rel_dim_employee))
    _upsert(engine, rel_dim_employee, rows, ["idemployee"])


def load_rel_dim_planos(df_sales: pd.DataFrame, engine: Engine) -> None:
    df   = _extract_dim_planos(df_sales)
    rows = _df_to_rows(df, _table_columns(rel_dim_planos))
    _upsert(engine, rel_dim_planos, rows, ["idmembership"])


def load_rel_dim_payment_type(df_debtors: pd.DataFrame, engine: Engine) -> None:
    cols   = [c for c in ["idpaymenttype", "paymenttype"] if c in df_debtors.columns]
    df     = df_debtors[cols].drop_duplicates(subset=["idpaymenttype"]).dropna(subset=["idpaymenttype"])
    rows   = _df_to_rows(df, _table_columns(rel_dim_payment_type))
    _upsert(engine, rel_dim_payment_type, rows, ["idpaymenttype"])


def load_rel_members(df: pd.DataFrame, engine: Engine) -> None:
    rows = _df_to_rows(df, _table_columns(rel_members))
    _upsert(engine, rel_members, rows, ["idmember"])


def load_rel_dim_address(df_members: pd.DataFrame, engine: Engine) -> None:
    df   = _extract_dim_address(df_members)
    rows = _df_to_rows(df, _table_columns(rel_dim_address))
    # upsert por idmember (constraint uq_address_member)
    _upsert(engine, rel_dim_address, rows, ["idmember"])


def load_rel_dim_partnerships(df_members: pd.DataFrame, engine: Engine) -> None:
    rows = _extract_dim_partnerships(df_members)
    _upsert(engine, rel_dim_partnerships, rows, ["idmember", "plataforma"])


def load_rel_sales(df: pd.DataFrame, engine: Engine) -> None:
    rows = _df_to_rows(df, _table_columns(rel_sales))
    _upsert(engine, rel_sales, rows, ["idsale"])


def load_rel_debtors(df: pd.DataFrame, engine: Engine) -> None:
    rows = _df_to_rows(df, _table_columns(rel_debtors))
    _upsert(engine, rel_debtors, rows, ["receivableid"])


# ==============================================================================
#  Orquestrador principal
# ==============================================================================

def load_db(
    alias: str,
    df: pd.DataFrame,
    engine: Engine | None = None,
    dfs_explodidos: dict[str, pd.DataFrame] | None = None,
) -> None:
    """
    Ponto de entrada do load para o banco.

    Executa upsert nos schemas raw e relational de acordo com o alias do endpoint.
    A ordem de carga do relational respeita as dependências de FK.

    Args:
        alias:          Identificador do endpoint (ex: 'members', 'sales', 'receivables').
        df:             DataFrame transformado pelo estágio transform.
        engine:         Engine SQLAlchemy (usa get_engine() se None).
        dfs_explodidos: Dict de DataFrames expandidos retornado pelo transform.
                        Necessário para sales: saleitens são re-mergeados antes do upsert.
    """
    if engine is None:
        engine = get_engine()

    dfs_explodidos = dfs_explodidos or {}

    log.info("[load_db] Iniciando carga DB para alias='%s' (%s linhas).", alias, len(df))

    if alias == "members":
        # raw (sem contacts — ficam no CSV explodido como backup)
        load_raw_members(df, engine)
        # relational — ordem de FK obrigatória
        load_rel_dim_branch(df, engine)
        load_rel_dim_employee(df, engine)
        # Merge de contacts antes do upsert de members
        df_members = _merge_contacts(df, dfs_explodidos.get("contacts"))
        # Deriva colunas de data e hora a partir dos campos DateTime
        for col, timecol in [
            ("registerdate",   "registertime"),
            ("updatedate",     "updatetime"),
            ("lastaccessdate", "lastaccesstime"),
            ("conversiondate", "conversiontime"),
        ]:
            if col in df_members.columns:
                dt = pd.to_datetime(df_members[col], errors="coerce")
                df_members[timecol] = dt.dt.time
                df_members[col]     = dt.dt.date
        # birthdate: converte para Date puro (sem hora)
        if "birthdate" in df_members.columns:
            df_members["birthdate"] = pd.to_datetime(df_members["birthdate"], errors="coerce").dt.date
        load_rel_members(df_members, engine)
        load_rel_dim_address(df, engine)
        load_rel_dim_partnerships(df, engine)
        # Re-aplica seed para garantir que nomes da API não sobrescrevam o padrão
        _seed_dim_branch(engine)

    elif alias == "sales":
        # Re-merge saleitens no df principal para recuperar campos removidos pelo explode
        df_sales = _merge_saleitens(df, dfs_explodidos.get("saleitens"))
        # raw
        load_raw_sales(df_sales, engine)
        # relational — dims primeiro (FK deps de rel_sales)
        load_rel_dim_planos(df_sales, engine)
        _load_dim_branch_from_sales(df_sales, engine)
        _load_dim_employee_from_sales(df_sales, engine)
        # Garante que todos os idmember de sales existam em data_warehouse.members
        # (FK: rel_sales.idmember → members.idmember) — stubs sem sobrescrever dados reais
        if "idmember" in df_sales.columns:
            member_ids = (
                df_sales["idmember"]
                .dropna()
                .drop_duplicates()
                .astype(int)
                .tolist()
            )
            _load_members_stub(member_ids, engine)
        # Deriva colunas de data e hora — sales
        for col, timecol in [("saledate", "saletime"), ("updatedate", "updatetime")]:
            if col in df_sales.columns:
                dt = pd.to_datetime(df_sales[col], errors="coerce")
                df_sales[timecol] = dt.dt.time
                df_sales[col]     = dt.dt.date
        # membershipstartdate: converte para Date puro (sem hora)
        if "membershipstartdate" in df_sales.columns:
            df_sales["membershipstartdate"] = pd.to_datetime(df_sales["membershipstartdate"], errors="coerce").dt.date
        load_rel_sales(df_sales, engine)
        # Re-aplica seed para garantir que nomes da API não sobrescrevam o padrão
        _seed_dim_branch(engine)

    elif alias == "debtors":
        # Padroniza nomes de colunas da API para o modelo debtors
        df_debtors = df.rename(columns=_RECEIVABLES_RENAME)
        # raw
        load_raw_debtors(df_debtors, engine)
        # relational — dim_branch + members stubs antes de rel_debtors (FK deps)
        load_rel_dim_payment_type(df_debtors, engine)
        if "branchid" in df_debtors.columns:
            df_branch = (
                df_debtors[["branchid"]]
                .drop_duplicates(subset=["branchid"])
                .dropna(subset=["branchid"])
                .rename(columns={"branchid": "branchid"})
            )
            rows_branch = _df_to_rows(df_branch, _table_columns(rel_dim_branch))
            _upsert(engine, rel_dim_branch, rows_branch, ["branchid"])
        if "memberid" in df_debtors.columns:
            member_ids = (
                df_debtors["memberid"]
                .dropna()
                .drop_duplicates()
                .astype(int)
                .tolist()
            )
            _load_members_stub(member_ids, engine)
        # Deriva colunas de data e hora — debtors
        if "registerdate" in df_debtors.columns:
            dt = pd.to_datetime(df_debtors["registerdate"], errors="coerce")
            df_debtors["registertime"] = dt.dt.time
            df_debtors["registerdate"] = dt.dt.date
        load_rel_debtors(df_debtors, engine)
        # Re-aplica seed para garantir que nomes da API não sobrescrevam o padrão
        _seed_dim_branch(engine)

    else:
        log.warning("[load_db] Alias '%s' não mapeado para carga DB. Ignorado.", alias)
        return

    log.info("[load_db] Carga DB concluída para alias='%s'.", alias)
