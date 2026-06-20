![Status](https://img.shields.io/badge/status-protótipo-orange)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.2.3-150458?logo=pandas&logoColor=white)
![requests](https://img.shields.io/badge/requests-2.32.3-2CA5E0)
![dotenv](https://img.shields.io/badge/python--dotenv-1.1.0-ECD53F)

# ETL Vendas — Incremental

Pipeline de coleta de dados de vendas com **carga incremental baseada em checkpoint**. Busca apenas registros novos desde a última execução bem-sucedida, com deduplicação em duas camadas e backup bruto automático.

> **Versão protótipo.** Lógica de checkpoint e deduplicação funcional, mas configuração ainda parcialmente hardcoded. Ver [Limitações](#limitações).

---

## Diferenciais em relação ao protótipo

| Recurso | Protótipo | Incremental |
|---|---|---|
| Checkpoint | — | `checkpoint.json` salvo após cada sucesso |
| Deduplicação | — | Dupla: interna ao batch + contra CSV histórico |
| Retry com limite | Infinito | Máx. 5 tentativas por falha |
| Backup bruto | — | `vendas_raw.csv` antes de qualquer transformação |
| Carga em modo append | — | Detecta se deve appendar ou sobrescrever |
| Tratamento de Ctrl+C | — | Salva dados parciais antes de sair |

---

## Como funciona

```
checkpoint.json ──▶ define dateSaleStart
       │               (ou 2024-01-01 se ausente)
       ▼
API de Vendas ── paginação 100 registros/req.
       │
       ▼
Deduplicação interna (por idsale)
       │
       ▼
Deduplicação cross-file (contra vendas.csv existente)
       │
       ├──▶ vendas_raw.csv    (backup bruto)
       │
       └──▶ vendas.csv
             ├── incremental → append
             └── completa   → sobrescreve
       │
       ▼
checkpoint.json atualizado
```

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

```env
END_POINT_SALES=https://sua-api.com/vendas
API_DNS=seu_usuario
API_TOKEN=seu_token
```

## Uso

```bash
python etl_vendas_incremental.py
```

Na primeira execução (sem `checkpoint.json`) faz carga completa desde `2024-01-01`. Nas seguintes, busca apenas o delta desde o último checkpoint.

## Arquivos gerados

| Arquivo | Descrição |
|---|---|
| `vendas.csv` | Dados processados (`;`, UTF-8) |
| `vendas_raw.csv` | Backup bruto pré-transformação |
| `checkpoint.json` | Timestamp da última execução bem-sucedida |

> Nenhum desses deve ser versionado. Adicione ao `.gitignore`.

## Tratamento de erros

| Situação | Comportamento |
|---|---|
| HTTP 429 | Aguarda 10s, tenta novamente |
| HTTP 401 | Encerra — credenciais inválidas |
| HTTP 5xx | Até **5 tentativas** com 10s de espera |
| Timeout | Aguarda 5s, tenta novamente |
| Ctrl+C | Salva dados parciais e encerra sem atualizar checkpoint |

## Limitações

- Data de fallback (`2024-01-01`) está hardcoded no script
- Endpoint único — só suporta vendas
- Lista de colunas a remover tem placeholders (`coluna1`, `coluna2`, `coluna3`)
- Sem testes automatizados
- Logs via `print` sem nível estruturado
