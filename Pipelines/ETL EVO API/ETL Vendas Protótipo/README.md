![Status](https://img.shields.io/badge/status-protótipo-orange)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.2.3-150458?logo=pandas&logoColor=white)
![requests](https://img.shields.io/badge/requests-2.32.3-2CA5E0)
![dotenv](https://img.shields.io/badge/python--dotenv-1.1.0-ECD53F)

# ETL Vendas — Protótipo

> **Este script é uma prova de conceito.** Foi o ponto de partida para validar a conexão com a API, o fluxo de paginação e a exportação básica para CSV. Não possui checkpoint, deduplicação nem carga incremental.

---

## O que faz

Conecta à API de vendas via HTTP Basic Auth, percorre todas as páginas de resultado (50 registros por vez) e exporta tudo para `sales.csv`.

```
.env
 └─ credenciais
        │
        ▼
API de Vendas  ──  paginação take/skip
        │
        ▼
Normalização JSON  →  limpeza de colunas
        │
        ▼
    sales.csv
```

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

Crie um `.env` na mesma pasta:

```env
API_URL=https://sua-api.com/endpoint
API_DNS=seu_usuario
API_TOKEN=seu_token
```

## Uso

```bash
python etl_vendas_v1.py
```

## Comportamento

| Situação | O que acontece |
|---|---|
| HTTP 429 | Aguarda 10s e tenta novamente |
| HTTP 401 | Loga erro e encerra |
| Timeout | Aguarda 5s e tenta novamente |
| Outros erros | Aguarda 10s e tenta novamente (sem limite de tentativas) |

- Data de início fixa: `2026-01-01T00:00:00`
- Data de fim: timestamp atual (fuso `America/Fortaleza`)
- Delay entre páginas: 1,8 segundos
- Saída: `sales.csv` — sempre sobrescreve, delimitador `;`, UTF-8

## Limitações

- Sem checkpoint — sempre faz carga completa desde a data fixa
- Sem deduplicação
- Sem limite de tentativas em erros (risco de loop infinito)
- Data de início hardcoded no código
- Saída única em CSV local

## Próximas versões

Este protótipo evoluiu para:

| Versão | Pasta | O que adiciona |
|---|---|---|
| Incremental | `../ETL Vendas Incremental` | Checkpoint, deduplicação dupla, retry com limite |
| Unificado | `../ETL Vendas Unificado` | Multi-endpoint, config externa, signal handler |
