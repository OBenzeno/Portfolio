"""
Executa os scripts SQL do schema raw diretamente contra o banco,
usando DATABASE_URL do .env — sem necessidade de psql instalado.
"""

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

SQL_DIR = os.path.dirname(os.path.abspath(__file__))

EXECUTION_ORDER = [
    "create_raw_members.sql",
    "create_raw_sales.sql",
    "create_raw_debtors.sql",
]


def _resolve_db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    print("DATABASE_URL não encontrada no .env.")
    print("Informe os dados de conexão:\n")

    host  = input("  Host     [localhost]: ").strip() or "localhost"
    port  = input("  Porta    [5432]:      ").strip() or "5432"
    user  = input("  Usuário  [postgres]:  ").strip() or "postgres"
    senha = input("  Senha:               ").strip()
    banco = input("  Banco    [academia]:  ").strip() or "academia"

    url = f"postgresql+psycopg2://{user}:{senha}@{host}:{port}/{banco}"
    print(f"\n  URL montada: postgresql+psycopg2://{user}:***@{host}:{port}/{banco}")

    salvar = input("\nSalvar no .env para uso futuro? [s/N]: ").strip().lower()
    if salvar == "s":
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env",
        )
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"\nDATABASE_URL={url}\n")
        print(f"  .env atualizado em '{env_path}'.")

    os.environ["DATABASE_URL"] = url
    return url


def run_schema_raw() -> None:
    url    = _resolve_db_url()
    engine = create_engine(url)

    with engine.begin() as conn:
        for filename in EXECUTION_ORDER:
            path = os.path.join(SQL_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()
            conn.execute(text(sql))
            print(f"  ✓ {filename}")

    print("\nSchema db_raw criado/verificado com sucesso.")


if __name__ == "__main__":
    run_schema_raw()
