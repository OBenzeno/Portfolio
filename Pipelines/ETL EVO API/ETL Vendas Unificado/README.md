![Status](https://img.shields.io/badge/status-protótipo-orange)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.2.3-150458?logo=pandas&logoColor=white)
![requests](https://img.shields.io/badge/requests-2.32.3-2CA5E0)
![dotenv](https://img.shields.io/badge/python--dotenv-1.1.0-ECD53F)

# ETL Vendas — Unificado

Pipeline ETL **multi-endpoint** controlado por configuração externa. Um único script suporta múltiplas fontes de dados (vendas, recebíveis, associados, prospectos) sem alteração de código — basta adicionar uma entrada no `endpoint_config.json`.

> **Versão protótipo.** Suporte a múltiplos endpoints funcional, mas a seleção ainda exige interação manual (`input()`), o que impede uso em agendadores como cron ou Airflow. Ver [Limitações](#limitações).

---

## Diferenciais em relação às versões anteriores

| Recurso | Protótipo | Incremental | Unificado |
|---|---|---|---|
| Endpoints suportados | 1 (vendas) | 1 (vendas) | **4 configuráveis** |
| Config externa | — | — | `endpoint_config.json` |
| Checkpoint | — | Sim | **Por endpoint** (isolado) |
| Deduplicação | — | Dupla | Dupla (por `idField` configurável) |
| Signal handler | — | Ctrl+C | **SIGINT completo** |
| Execução não interativa | Sim | Sim | Não (`input()`) |

---

## Arquitetura orientada a config

O comportamento de cada endpoint é definido inteiramente em `endpoint_config.json`:

```json
{
  "sales": {
    "idBranch": "0",
    "take": 100,
    "dateStartKey": "dateSaleStart",
    "dateEndKey": "dateSaleEnd",
    "idField": "idsale",
    "responseKey": "data"
  },
  "receivables": { "..." }
}
```

Para adicionar um novo endpoint, basta incluir a URL no `.env` e criar a entrada no JSON — sem tocar no código Python.

## Fluxo

```
.env ──▶ aliases de endpoints
            │
            ▼
        input() ──▶ seleção do endpoint
            │
            ▼
endpoint_config.json ──▶ parâmetros dinâmicos
            │
            ▼
checkpoint_{alias}.json ──▶ dateSaleStart
            │
            ▼
     API  (take configurável)
            │
            ▼
  Dedup interna + cross-file por idField
            │
            ├──▶ {alias}_raw.csv
            ├──▶ {alias}.csv   (append ou sobrescreve)
            └──▶ checkpoint_{alias}.json
```

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

### `.env`

```env
API_DNS=seu_usuario
API_TOKEN=seu_token

END_POINT_SALES=https://sua-api.com/vendas
END_POINT_RECEIVABLES=https://sua-api.com/recebiveis
END_POINT_MEMBERSHIP=https://sua-api.com/associados
END_POINT_PROSPECTS=https://sua-api.com/prospectos
```

### `endpoint_config.json`

| Campo | Descrição |
|---|---|
| `idBranch` | Filtro de filial (`"0"` = todas) |
| `take` | Registros por página |
| `dateStartKey` / `dateEndKey` | Nomes dos parâmetros de data na API |
| `idField` | Coluna identificadora para deduplicação |
| `responseKey` | Chave JSON onde os dados estão (`null` = raiz) |

## Uso

```bash
python etl_vendas_unificado.py
# Endpoints disponíveis: sales, receivables, membership, prospects
# Informe o endpoint: sales
```

## Arquivos gerados

Os nomes são dinâmicos com base no alias selecionado:

| Arquivo | Descrição |
|---|---|
| `{alias}.csv` | Dados processados |
| `{alias}_raw.csv` | Backup bruto |
| `checkpoint_{alias}.json` | Timestamp por endpoint |

## Limitações

- Seleção de endpoint via `input()` — incompatível com execução automatizada
- Data de fallback (`2024-01-01`) hardcoded no script
- Adicionar novos aliases ainda requer edição de `ENDPOINT_ALIASES` no código
- Sem testes automatizados
- Logs via `print` sem nível estruturado
