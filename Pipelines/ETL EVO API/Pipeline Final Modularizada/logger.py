"""
Configuração centralizada de logging.
Chame setup_logging() uma única vez em main.py antes de importar os demais módulos.
"""

import logging


def setup_logging(level: int = logging.DEBUG) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Silencia logs verbosos de bibliotecas externas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    # Suprime SQL/parameters debug do SQLAlchemy (cada query gera linhas de parâmetros)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
