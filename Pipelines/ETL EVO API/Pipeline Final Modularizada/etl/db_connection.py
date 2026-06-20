"""
Conexão com o banco de dados via SQLAlchemy Core.

Fornece um Engine singleton reutilizável com pool de conexões e
cria os schemas 'db_raw' e 'data_warehouse' se não existirem.
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from pipeline.config import DB_URL

log = logging.getLogger(__name__)

_engine: Engine | None = None

SCHEMAS = ("db_raw", "data_warehouse")


def get_engine() -> Engine:
    """
    Retorna o Engine singleton. Cria na primeira chamada.

    Raises:
        RuntimeError: Se DATABASE_URL não estiver configurada no .env.
    """
    global _engine
    if _engine is None:
        if not DB_URL:
            raise RuntimeError(
                "DATABASE_URL não configurada no .env. "
                "Formato esperado: postgresql+psycopg2://user:pass@host:5432/dbname"
            )
        _engine = create_engine(
            DB_URL,
            pool_pre_ping=True,   # valida conexão antes de usar do pool
            pool_size=5,
            max_overflow=2,
        )
        log.info("Engine criado: %s", _engine.url.render_as_string(hide_password=True))
        _ensure_schemas(_engine)
    return _engine


def _ensure_schemas(engine: Engine) -> None:
    """Cria os schemas 'db_raw' e 'data_warehouse' se ainda não existirem."""
    with engine.begin() as conn:
        for schema in SCHEMAS:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            log.info("Schema '%s' verificado/criado.", schema)
