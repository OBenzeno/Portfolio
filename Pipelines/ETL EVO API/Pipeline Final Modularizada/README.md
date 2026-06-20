# ETL EVO API — Pipeline Modularizada

Sistema ETL modular para coleta, transformação e carga de dados das APIs EVO das unidades Skyfit Academia em um banco de dados PostgreSQL estruturado para BI.

---

## Visão Geral

A pipeline opera sobre **3 endpoints** e **2 filiais**, com carga incremental baseada em checkpoints:

| Endpoint      | Dados coletados                       |
|---------------|---------------------------------------|
| `members`     | Cadastro de alunos e membros          |
| `sales`       | Vendas de planos e produtos           |
| `receivables` | Recebíveis e inadimplência            |

| Identificador | Unidade      |
|---------------|--------------|
| `filial_01`   | Santa Helena |
| `filial_02`   | Cambuí       |

---

## Arquitetura

```
EVO API (3 endpoints × 2 filiais)
        │
        ▼
   [Extract]  ── paginação com retry automático
        │
        ▼
  [Transform] ── normalização, deduplicação, explosão de colunas aninhadas
        │
        ├──▶ data/raw/          ← backup bruto (pré-transform)
        ├──▶ data/final/clean/  ← CSVs limpos por endpoint × filial
        ├──▶ data/final/exp/    ← tabelas expandidas (contacts, saleitens)
        └──▶ data/final/merged/ ← CSVs consolidados das duas filiais
        │
        ▼
   [Load DB]  ── upsert no PostgreSQL (2 schemas)
        ├──▶ db_raw          (flat, sem FK — auditoria)
        └──▶ data_warehouse  (Galaxy Schema — BI)
        │
        ▼
  [Checkpoint] ── registra timestamp para próxima carga incremental
```

---

## Pré-requisitos

- Python 3.11+
- PostgreSQL 12+ acessível localmente ou via rede
- Dependências:

```bash
pip install -r requirements.txt
```

---

## Configuração

### `.env`

Crie o arquivo `.env` na raiz de `pipeline/`:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/banco

END_POINT_SALES=https://evo-integracao-api.w12app.com.br/api/v2/sales
END_POINT_MEMBERS=https://evo-integracao-api.w12app.com.br/api/v2/members
END_POINT_RECEIVABLES=https://evo-integracao-api.w12app.com.br/api/v1/receivables/debtors

API_DNS=dns_da_academia
API_TOKEN_FILIAL1=token-da-filial-01
API_TOKEN_FILIAL2=token-da-filial-02
```

> [!IMPORTANT]
> Nunca versione o `.env`. Credenciais e tokens de API ficam exclusivamente neste arquivo.

### `config/branches.json`

Mapeia cada filial aos nomes das variáveis de ambiente — não armazena valores diretamente:

```json
{
  "filial_01": { "dns_env": "API_DNS", "token_env": "API_TOKEN_FILIAL1", "nome": "Unidade 1" },
  "filial_02": { "dns_env": "API_DNS", "token_env": "API_TOKEN_FILIAL2", "nome": "Unidade 2" }
}
```

### `config/endpoint_config.json`

Define o comportamento de cada endpoint:

| Campo            | Descrição                                              |
|------------------|--------------------------------------------------------|
| `take` / `skip`  | Tamanho e offset da paginação                          |
| `dateStartKey`   | Nome do parâmetro de data inicial na API               |
| `dateEndKey`     | Nome do parâmetro de data final na API                 |
| `responseKey`    | Chave JSON onde os dados estão aninhados (`null` = raiz) |
| `idField`        | Identificador único para deduplicação                  |
| `colunas_drop`   | Colunas a remover após a extração                      |
| `colunas_explode`| Colunas aninhadas que viram tabelas separadas          |

### `config.py`

Parâmetros globais ajustáveis:

| Constante          | Padrão                  | Descrição                                        |
|--------------------|-------------------------|--------------------------------------------------|
| `DEFAULT_DATE_START` | `"2023-01-01T00:00:00"` | Data de início para a primeira carga histórica   |
| `REQUEST_DELAY`    | `1.8`                   | Intervalo em segundos entre páginas (rate limit) |
| `MAX_RETRIES`      | `5`                     | Tentativas antes de abortar em falha HTTP        |
| `TIMEOUT`          | `30`                    | Timeout por requisição (segundos)                |

---

## Como Executar

```bash
cd pipeline/
python run_all_branches.py
```

### Menu 1 — Modo de execução

```
? Selecione o modo de execução:
  ❯ Automático   (percorre todas as filiais × endpoints sem interação)
    Manual        (seleciona filial e endpoint individualmente)
```

### Menu 2 — Operação

```
? Selecione a operação:
  ❯ Extração + Carga DB   (fluxo completo — uso normal)
    Extração apenas        (salva em CSV, sem tocar no banco)
    Carga DB apenas        (lê CSVs existentes e carrega no banco)
```

### Automação (Task Scheduler)

Para execução agendada sem interação:

```bash
python run_filial_01.py
```

Executa os 3 endpoints da filial 01 em sequência, atualiza checkpoints e consolida CSVs.

---

## Fluxo Interno

Para cada combinação **endpoint × filial**:

```
[1] Checkpoint
    ├── Existe → carga incremental (date_start = last_run)
    └── Ausente → carga histórica (date_start = DEFAULT_DATE_START)

[2] Extract
    ├── GET paginado (take/skip) até página vazia
    ├── Retry com backoff exponencial (até MAX_RETRIES)
    └── Ctrl+C → salva parcial em data/partial/

[3] Transform
    ├── Normaliza colunas (camelCase → minúsculas)
    ├── Corrige encoding (latin-1 detectado como UTF-8)
    ├── Remove colunas configuradas em colunas_drop
    ├── Deduplica internamente (por idField)
    ├── Deduplica contra CSV histórico (se incremental)
    └── Expande colunas aninhadas:
        ├── members → contacts (phone_ddi, phone, email)
        └── sales   → saleitens (item, valor, plano)

[4] Load CSV
    ├── Backup bruto  → data/raw/{alias}_{filial}_raw.csv
    ├── CSV limpo     → data/final/clean/{alias}_{filial}.csv
    │   ├── Incremental: append sem cabeçalho
    │   └── Completa: sobrescreve
    └── CSVs expandidos → data/final/exp/{alias}_{col}_{filial}.csv

[5] Load DB
    ├── db_raw          → upsert flat (ON CONFLICT DO UPDATE)
    └── data_warehouse  → upsert normalizado, respeitando FKs:
        1. dim_branch, dim_employee, dim_planos, dim_payment_type
        2. members, dim_address, dim_partnerships
        3. sales, debtors

[6] Merge de filiais
    └── Consolida CSVs das filiais → data/final/merged/{alias}_merged.csv

[7] Checkpoint salvo
    └── checkpoints/checkpoint_{alias}_{filial}.json
```

---

## Banco de Dados

### Schemas

| Schema           | Propósito                                                |
|------------------|----------------------------------------------------------|
| `db_raw`         | Cópia flat dos dados brutos, sem FK — camada de auditoria |
| `data_warehouse` | Modelo normalizado (Galaxy Schema) — camada de BI        |

Ambos os schemas são **criados automaticamente** na primeira execução.

### Modelo — Galaxy Schema (`data_warehouse`)

```
dim_branch ──┬──▶ members ──▶ dim_address
             │        │
dim_employee ┘        ├──▶ dim_partnerships
                      │
                      ├──▶ sales ──▶ dim_planos
                      │       └──▶ dim_employee
                      │       └──▶ dim_branch
                      │
                      └──▶ debtors ──▶ dim_payment_type
                                  └──▶ dim_branch
```

### Tabelas

| Tabela             | Tipo      | Descrição                                  |
|--------------------|-----------|--------------------------------------------|
| `dim_branch`       | Dimensão  | Filiais                                    |
| `dim_employee`     | Dimensão  | Funcionários (consultores e instrutores)   |
| `dim_planos`       | Dimensão  | Planos e produtos                          |
| `dim_payment_type` | Dimensão  | Tipos de pagamento                         |
| `members`          | Dimensão  | Cadastro de alunos (contatos já integrados) |
| `dim_address`      | Satélite  | Endereço por membro (1:1)                  |
| `dim_partnerships` | Satélite  | Parcerias por membro (Gympass, Totalpass)  |
| `sales`            | Fato      | Vendas de planos                           |
| `debtors`          | Fato      | Recebíveis e inadimplência                 |

> Toda carga usa **upsert** (`ON CONFLICT DO UPDATE`) — a pipeline é idempotente e segura para re-execução.

---

## Estrutura do Projeto

```
pipeline/
├── run_all_branches.py      ← ponto de entrada interativo
├── run_filial_01.py         ← execução automatizada (Task Scheduler)
├── main.py                  ← orquestrador por endpoint × filial
├── config.py                ← constantes globais e caminhos
├── checkpoint.py            ← leitura e escrita de checkpoints
├── http_client.py           ← cliente HTTP com retry e backoff
├── logger.py                ← configuração centralizada de logs
│
├── config/
│   ├── branches.json        ← filiais e variáveis de credencial
│   └── endpoint_config.json ← configuração por endpoint
│
├── etl/
│   ├── extract.py           ← paginação e coleta da API
│   ├── transform.py         ← normalização, limpeza e deduplicação
│   ├── load.py              ← persistência em CSV e merge de filiais
│   ├── load_db.py           ← upsert no banco (dims, fatos, raw)
│   ├── db_schema.py         ← definição das tabelas (SQLAlchemy Core)
│   └── db_connection.py     ← engine PostgreSQL (singleton, pool)
│
├── sql/                     ← scripts SQL de referência
│   ├── raw/                 ← criação das tabelas db_raw
│   └── data_warehouse/      ← criação das tabelas do modelo relacional
│
├── data/
│   ├── raw/                 ← backups brutos (pré-transform)
│   ├── partial/             ← dados salvos em caso de interrupção
│   └── final/
│       ├── clean/           ← CSVs limpos por endpoint × filial
│       ├── exp/             ← tabelas expandidas (contacts, saleitens)
│       └── merged/          ← CSVs consolidados das duas filiais
│
├── checkpoints/             ← estado das execuções por endpoint × filial
├── .env                     ← credenciais (não versionar)
├── .gitignore
└── requirements.txt
```

---

## Comportamento Incremental

- **Primeira execução**: coleta desde `DEFAULT_DATE_START` (definido em `config.py`)
- **Execuções seguintes**: coleta apenas dados novos desde o último checkpoint
- **Checkpoint por endpoint × filial**: falha em uma combinação não afeta as demais
- **Forçar recarga completa**: apagar o arquivo em `checkpoints/` da combinação desejada

---

## Interrupção (Ctrl+C)

No modo **Automático**, `Ctrl+C` exibe um menu de escolha:

```
? Pipeline interrompida. O que deseja fazer?
  ❯ Cancelar endpoint atual
    Cancelar filial atual
    Cancelar toda a pipeline
    Continuar
```

- Dados parcialmente extraídos são salvos automaticamente em `data/partial/`
- O checkpoint **não é atualizado** em execuções interrompidas
- Ao cancelar toda a pipeline, o sistema pergunta se os checkpoints salvos na sessão devem ser mantidos ou removidos

---

## Módulos Principais

| Módulo              | Responsabilidade                                               |
|---------------------|----------------------------------------------------------------|
| `extract.py`        | Paginação, retry com backoff exponencial, salvamento parcial  |
| `transform.py`      | Normalização de colunas, fix de encoding, deduplicação dupla, explosão de nested columns |
| `load.py`           | CSV (raw, clean, exp), merge de filiais com re-integração de contatos e itens |
| `load_db.py`        | Extração de dimensões, upsert em lote, coerção de tipos Pandas → PostgreSQL |
| `db_schema.py`      | Definição declarativa das tabelas (SQLAlchemy Core, dois metadatas) |
| `db_connection.py`  | Engine singleton com pool e pre-ping                          |
| `checkpoint.py`     | Leitura e escrita de `{ "last_run": "..." }` por combinação   |
| `http_client.py`    | GET com retry em `{429, 500, 502, 503, 504}`, backoff `2^n`s  |

---

## Problemas Comuns

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| `Credenciais ausentes no .env` | Variável não definida | Verificar e preencher o `.env` |
| `0 registros coletados` | Intervalo de datas sem dados | Verificar `DEFAULT_DATE_START` e `endpoint_config.json` |
| `Coluna X não encontrada` | Campo mudou na API | Verificar `idField` e `colunas_drop` no config |
| Dados desatualizados após recarga | Checkpoint antigo | Apagar `checkpoints/checkpoint_{alias}_{filial}.json` |
| `FK violation` no banco | Endpoint carregado antes de `members` | Executar `members` antes de `sales` e `receivables` |
| Nomes de filial incorretos no banco | Seed sobrescrita pela API | A seed é reaplicada automaticamente ao final de cada carga |

---

## Dependências

| Pacote             | Versão   | Uso                                     |
|--------------------|----------|-----------------------------------------|
| `pandas`           | 2.2.3    | Manipulação de dados e DataFrames       |
| `requests`         | 2.32.3   | Requisições HTTP à API EVO              |
| `SQLAlchemy`       | 2.0.39   | Abstração do banco e definição do schema |
| `psycopg2-binary`  | 2.9.12   | Driver PostgreSQL                       |
| `python-dotenv`    | 1.1.0    | Leitura de variáveis do `.env`          |
| `questionary`      | 2.1.1    | Menus interativos no terminal           |

```bash
pip install -r requirements.txt
```

---

## Arquivos que não devem ser versionados

```gitignore
.env
data/
checkpoints/
```

O `endpoint_config.json` e `branches.json` **devem** ser versionados — fazem parte da configuração do projeto e não contêm credenciais.
