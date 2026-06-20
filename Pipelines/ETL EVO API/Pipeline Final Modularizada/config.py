"""
Configurações globais da pipeline: variáveis de ambiente, constantes e caminhos.
"""

import os
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

# ── Endpoints disponíveis ──────────────────────────────────────────────────────
ENDPOINT_ALIASES: dict[str, str | None] = {
    "sales":               os.getenv("END_POINT_SALES"),
    "debtors":             os.getenv("END_POINT_DEBTORS"),
    "members":          os.getenv("END_POINT_MEMBERS"),
    #"membership":          os.getenv("END_POINT_MEMBERSHIPS"),
    #"membership_category": os.getenv("END_POINT_MEMBERSHIP_CATEGORY"),
    #"membermembership":    os.getenv("END_POINT_MEMBERMEMBERSHIP"),
}

# ── Credenciais por filial ─────────────────────────────────────────────────────
# branches.json armazena apenas os nomes das variáveis de ambiente,
# nunca os valores — os segredos vivem exclusivamente no .env
_BRANCHES_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "branches.json")

with open(_BRANCHES_CONFIG_PATH, "r", encoding="utf-8") as _f:
    _branches_raw: dict = json.load(_f)

BRANCHES: dict[str, dict] = _branches_raw  # metadados completos por filial

BRANCHES_AUTH: dict[str, HTTPBasicAuth] = {}
for _branch_id, _cfg in _branches_raw.items():
    _dns   = os.getenv(_cfg["dns_env"])
    _token = os.getenv(_cfg["token_env"])
    if not _dns or not _token:
        raise ValueError(
            f"Credenciais ausentes no .env para '{_branch_id}': "
            f"{_cfg['dns_env']} / {_cfg['token_env']}"
        )
    BRANCHES_AUTH[_branch_id] = HTTPBasicAuth(_dns, _token)

# ── Parâmetros HTTP ────────────────────────────────────────────────────────────
MAX_RETRIES   = 5
RETRY_CODES   = {429, 500, 502, 503, 504}
TIMEOUT       = 30
REQUEST_DELAY = 1.8  # segundos entre páginas (ajuste para evitar rate limit)

# ── Caminhos de saída ──────────────────────────────────────────────────────────
# BASE_DIR resolve o caminho absoluto da pasta pipeline/ independente de onde é executado
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
DIR_CLEAN       = os.path.join(BASE_DIR, "data", "final", "clean")
DIR_EXP         = os.path.join(BASE_DIR, "data", "final", "exp")
DIR_MERGED      = os.path.join(BASE_DIR, "data", "final", "merged")
DIR_RAW         = os.path.join(BASE_DIR, "data", "raw")
DIR_PARTIAL     = os.path.join(BASE_DIR, "data", "partial")
DIR_CHECKPOINTS = os.path.join(BASE_DIR, "checkpoints")

OUTPUT_DIRS = [DIR_CLEAN, DIR_EXP, DIR_MERGED, DIR_RAW, DIR_PARTIAL, DIR_CHECKPOINTS]

# ── Banco de dados ────────────────────────────────────────────────────────────
DB_URL = os.getenv("DATABASE_URL")  # ex: postgresql+psycopg2://user:pass@host:5432/dbname

# ── Data de início padrão (carga full) ────────────────────────────────────────
DEFAULT_DATE_START = "2023-01-01T00:00:00"
