![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-336791?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.2.3-150458?logo=pandas&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.39-D71F00)
![requests](https://img.shields.io/badge/requests-2.32.3-2CA5E0)
![Status](https://img.shields.io/badge/status-produção-brightgreen)

# ETL EVO API

Pipeline ETL modular para coleta, transformação e carga de dados da API EVO em um banco de dados PostgreSQL estruturado para BI. Suporta múltiplas filiais e endpoints com carga incremental baseada em checkpoints.

---

## Visão Geral

```
┌──────────────────────────────────────┐
│             EVO API                  │
│   /members  /sales  /receivables     │
└──────────────┬───────────────────────┘
               │  HTTP Basic Auth + paginação
               ▼
┌──────────────────────────────────────┐
│            EXTRACT                   │
│  Paginação take/skip                 │
│  Retry com backoff exponencial       │
│  Salvamento parcial em Ctrl+C        │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│           TRANSFORM                  │
│  Normalização de colunas             │
│  Correção de encoding                │
│  Deduplicação (interna + histórico)  │
│  Explosão de nested columns          │
└──────┬───────────────────┬───────────┘
       │                   │
       ▼                   ▼
  data/raw/           data/final/
  backup bruto        clean/   → CSV por endpoint × filial
                      exp/     → tabelas expandidas
                      merged/  → consolidado das filiais
       │
       ▼
┌──────────────────────────────────────┐
│            LOAD DB                   │
│  db_raw         → flat, sem FK       │
│  data_warehouse → Galaxy Schema      │
│  Upsert: ON CONFLICT DO UPDATE       │
└──────────────┬───────────────────────┘
               │
               ▼
         checkpoint salvo
```

**Endpoints ativos:**

| Alias | Dados coletados |
|---|---|
| `members` | Cadastro de membros |
| `sales` | Vendas de planos e produtos |
| `receivables` | Recebíveis e inadimplência |

**Filiais ativas:**

| Identificador | Unidade |
|---|---|
| `filial_01` | Santa Helena |
| `filial_02` | Jardim Cambuí |

---

## Estrutura do Projeto

```
pipeline/
├── run_pipeline.py           ← execução automática (Task Scheduler) — ambas filiais
├── cli_pipeline.py           ← execução interativa com menus
├── main.py                   ← orquestrador endpoint × filial
├── config.py                 ← constantes globais
├── checkpoint.py             ← controle de checkpoint
├── http_client.py            ← HTTP com retry e backoff
├── logger.py                 ← logging centralizado
│
├── config/
│   ├── branches.json         ← filiais e variáveis de credencial
│   └── endpoint_config.json  ← parâmetros por endpoint
│
├── etl/
│   ├── extract.py            ← paginação e coleta
│   ├── transform.py          ← normalização, limpeza, deduplicação
│   ├── load.py               ← persistência CSV e merge de filiais
│   ├── load_db.py            ← upsert no PostgreSQL
│   ├── db_schema.py          ← tabelas via SQLAlchemy Core
│   └── db_connection.py      ← engine singleton com pool
│
├── sql/
│   ├── raw/                  ← scripts CREATE TABLE para db_raw
│   ├── data_warehouse/       ← scripts CREATE TABLE para data_warehouse
│   └── views/                ← views desnormalizadas para BI
│       ├── vw_members.sql
│       ├── vw_sales.sql
│       └── vw_debtors.sql
│
├── data/                     ← gerado em runtime (não versionar)
├── checkpoints/              ← gerado em runtime (não versionar)
├── .env                      ← credenciais (não versionar)
├── .gitignore
└── requirements.txt
```

---

## Instalação

**Requisitos:** Python 3.11+, PostgreSQL 12+

```bash
pip install -r requirements.txt
```

| Pacote | Versão | Uso |
|---|---|---|
| `pandas` | 2.2.3 | Manipulação de dados |
| `requests` | 2.32.3 | Requisições HTTP |
| `SQLAlchemy` | 2.0.39 | Abstração do banco |
| `psycopg2-binary` | 2.9.12 | Driver PostgreSQL |
| `python-dotenv` | 1.1.0 | Leitura do `.env` |
| `questionary` | 2.1.1 | Menus interativos |

---

## Configuração

### `.env`

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/banco

END_POINT_SALES=<url>
END_POINT_MEMBERS=<url>
END_POINT_RECEIVABLES=<url>

API_DNS=<dns>
API_TOKEN_FILIAL1=<token>
API_TOKEN_FILIAL2=<token>
```

### `config/branches.json`

Mapeia cada filial aos nomes das variáveis de ambiente — sem armazenar valores diretamente:

```json
{
  "filial_01": { "dns_env": "API_DNS", "token_env": "API_TOKEN_FILIAL1" },
  "filial_02": { "dns_env": "API_DNS", "token_env": "API_TOKEN_FILIAL2" }
}
```

### `config/endpoint_config.json`

| Campo | Descrição |
|---|---|
| `take` / `skip` | Tamanho e offset da paginação |
| `dateStartKey` / `dateEndKey` | Nomes dos parâmetros de data na API |
| `responseKey` | Chave JSON dos dados (`null` = raiz) |
| `idField` | Identificador único para deduplicação |
| `colunas_drop` | Colunas a remover após extração |
| `colunas_explode` | Colunas aninhadas que viram tabelas separadas |

### `config.py`

| Constante | Padrão | Descrição |
|---|---|---|
| `DEFAULT_DATE_START` | `"2023-01-01T00:00:00"` | Início da primeira carga histórica |
| `REQUEST_DELAY` | `1.8` | Intervalo entre páginas (rate limit) |
| `MAX_RETRIES` | `5` | Tentativas antes de abortar |
| `TIMEOUT` | `30` | Timeout por requisição (segundos) |

---

## Execução

### Automação (Task Scheduler)

```bash
python run_pipeline.py
```

Executa todas as filiais e endpoints em sequência (`members → sales → debtors`), sem interação. Indicado para Task Scheduler ou cron. Registra falhas individuais e continua as demais combinações.

### Modo interativo

```bash
python cli_pipeline.py
```

```
? Selecione o modo de execução:
  ❯ Automático
    Manual

? Selecione a operação:
  ❯ Extração + Carga DB
    Extração apenas
    Carga DB apenas
```

| Operação | Descrição |
|---|---|
| Extração + Carga DB | Fluxo completo — uso normal |
| Extração apenas | Coleta e salva em CSV, sem tocar no banco |
| Carga DB apenas | Lê CSVs existentes e carrega no banco |

---

## Fluxo Interno

Para cada **endpoint × filial**:

```
[1] Checkpoint
    ├── Existe  → dateSaleStart = last_run  (incremental)
    └── Ausente → dateSaleStart = DEFAULT_DATE_START  (histórica)

[2] Extract
    ├── GET paginado até página vazia
    ├── Retry: backoff 2^n segundos, max MAX_RETRIES
    └── Ctrl+C → salva parcial em data/partial/

[3] Transform
    ├── Normaliza colunas: camelCase → minúsculas
    ├── Corrige encoding (latin-1 detectado como UTF-8)
    ├── Remove colunas configuradas (colunas_drop)
    ├── Deduplica internamente por idField
    ├── Deduplica contra CSV histórico (se incremental)
    └── Expande colunas aninhadas:
        ├── members  → contacts  (phone_ddi, phone, email)
        └── sales    → saleitens (idsaleitem, idmembership, itemvalue)

[4] Load CSV
    ├── data/raw/{alias}_{filial}_raw.csv     (backup bruto)
    ├── data/final/clean/{alias}_{filial}.csv (append ou sobrescreve)
    └── data/final/exp/{alias}_{col}_{filial}.csv

[5] Load DB
    ├── db_raw          → upsert flat
    └── data_warehouse  → upsert respeitando FK:
        1. dim_branch, dim_employee, dim_planos, dim_payment_type
        2. members, dim_address, dim_partnerships
        3. sales, debtors

[6] Merge
    └── data/final/merged/{alias}_merged.csv

[7] Checkpoint salvo
    └── checkpoints/checkpoint_{alias}_{filial}.json
```

---

## Banco de Dados

### Galaxy Schema — `data_warehouse`

```
dim_branch ──┬──▶ members ──▶ dim_address
             │        │
dim_employee ┘        └──▶ dim_partnerships

members ──▶ sales ──▶ dim_branch
members ──▶ debtors ──▶ dim_branch
                    └──▶ dim_payment_type
```

**Schemas:**

| Schema | Propósito |
|---|---|
| `db_raw` | Cópia flat sem FK — auditoria |
| `data_warehouse` | Modelo normalizado — BI |

**Ordem de criação (respeitar FKs):**

```
1. dim_branch, dim_employee, dim_planos, dim_payment_type
2. members
3. dim_address, dim_partnerships
4. sales, debtors
```

**Notas de schema:**

- Colunas de data e hora armazenadas em campos separados (`registerdate` / `registertime`, `saledate` / `saletime`, etc.)
- `dim_partnerships` possui PK surrogate `idpartnership SERIAL` e restrição `UNIQUE (idmember, plataforma)` — permite um registro por plataforma por membro (GYMPASS, TOTALPASS)
- Membros compartilhados entre filiais são carregados uma única vez; registros stub (somente ID) são preservados e preenchidos quando a filial de origem é processada

**Tabelas inativas** (pendentes de validação — não criar):

| Tabela | Motivo |
|---|---|
| `membermembership` | Coluna aninhada (`receivables`) precisa ser tratada antes |
| `receivables` | Relacionamento com `membermembership` e `sales` não validado |

---

## Views para BI

Views desnormalizadas em `sql/views/`, prontas para importação no Power BI sem relacionamentos adicionais:

| View | Tabelas mescladas |
|---|---|
| `vw_members` | `members` + `dim_branch` + `dim_employee` + `dim_partnerships` + `dim_address` |
| `vw_sales` | `sales` + `members` + `dim_branch` |
| `vw_debtors` | `debtors` + `members` + `dim_branch` + `dim_payment_type` |

`vw_members` pivota `dim_partnerships` em colunas (`gympass_codigo`, `totalpass_codigo`) via `MAX(CASE WHEN ...)` para evitar multiplicação de linhas.

---

## Comportamento Incremental

- Checkpoint isolado por endpoint × filial
- Falha em uma combinação não afeta as demais
- Checkpoint **não atualizado** em execuções interrompidas
- Para forçar recarga completa: apagar `checkpoints/checkpoint_{alias}_{filial}.json`

---

## Interrupção (Ctrl+C)

```
? Pipeline interrompida. O que deseja fazer?
  ❯ Cancelar endpoint atual
    Cancelar filial atual
    Cancelar toda a pipeline
    Continuar
```

Dados parciais salvos automaticamente em `data/partial/`.

---

## Problemas Comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `Credenciais ausentes` | Variável faltando no `.env` | Verificar e preencher o `.env` |
| `0 registros coletados` | Intervalo sem dados ou `DEFAULT_DATE_START` comentado | Verificar `config.py` e `endpoint_config.json` |
| `FK violation` | Endpoint carregado antes de `members` | Executar `members` primeiro |
| Dados desatualizados | Checkpoint antigo | Apagar o arquivo em `checkpoints/` |
| Encoding quebrado | Latin-1 detectado como UTF-8 | `fix_encoding()` em `transform.py` trata automaticamente |
| Nome de filial incorreto no banco | Seed sobrescrita pela API | Pipeline reaplicar seed ao final de cada carga |
