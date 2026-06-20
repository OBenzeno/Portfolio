# ETL Vendas — Incremental

> [!WARNING]
> **VERSÃO PROTÓTIPO** — Pipeline em fase de desenvolvimento. Validar comportamento de deduplicação e checkpoint antes de qualquer uso em produção.

---

## Visão Geral

Pipeline ETL focado em **carga incremental** de dados de vendas. Utiliza um mecanismo de checkpoint para registrar a última execução bem-sucedida e buscar apenas os registros novos a partir desse ponto, evitando recargas completas desnecessárias.

**Arquivo principal:** `etl_vendas_incremental.py`

---

## Fluxo de Dados

```
.env (credenciais)
    │
    ▼
checkpoint.json → define dateSaleStart (ou 2024-01-01 se ausente)
    │
    ▼
Requisições paginadas à API (100 registros/requisição)
    │
    ▼
Tratamento de erros (máx. 5 tentativas por falha)
    │
    ▼
Normalização JSON + limpeza de colunas
    │
    ▼
Backup bruto → vendas_raw.csv
    │
    ▼
Deduplicação (batch + cross-file)
    │
    ├── Carga incremental → append em vendas.csv
    └── Carga completa   → sobrescreve vendas.csv
    │
    ▼
Atualização do checkpoint.json
```

---

## Pré-requisitos

- Python 3.9+
- Bibliotecas:

```bash
pip install requests pandas python-dotenv
```

---

## Configuração

Crie um arquivo `.env` na mesma pasta do script:

```env
END_POINT_SALES=https://sua-api.exemplo.com/vendas
API_DNS=seu_usuario
API_TOKEN=seu_token
```

| Variável          | Descrição                                |
|-------------------|------------------------------------------|
| `END_POINT_SALES` | Endpoint da API de vendas                |
| `API_DNS`         | Usuário para autenticação HTTP Basic     |
| `API_TOKEN`       | Token/senha para autenticação HTTP Basic |

---

## Como Executar

```bash
python etl_vendas_incremental.py
```

Na **primeira execução** (sem `checkpoint.json`), o pipeline realiza carga completa a partir de `2024-01-01`. Nas execuções seguintes, busca apenas registros após o último timestamp salvo.

---

## Comportamento

### Checkpoint
- Lido de `checkpoint.json` no início da execução.
- Define o valor de `dateSaleStart` para a API.
- Atualizado **somente após conclusão bem-sucedida**.
- Em caso de falha ou interrupção, o checkpoint não é alterado — a próxima execução reprocessa a partir do mesmo ponto.

### Paginação
- 100 registros por requisição.
- Encerra quando a resposta retorna menos de 100 registros.
- Intervalo de **1,8 segundos** entre requisições.

### Deduplicação (dupla camada)
| Camada | Escopo | Descrição |
|--------|--------|-----------|
| 1 | Batch atual | Remove `idsale` duplicados dentro dos dados recém-buscados |
| 2 | Cross-file | Compara com o CSV existente e descarta IDs já presentes |

### Tratamento de Erros
| Situação | Comportamento |
|----------|---------------|
| HTTP 429 | Aguarda 10s e tenta novamente |
| HTTP 401 | Loga erro de autenticação e encerra |
| HTTP 5xx | Tenta novamente até **5 tentativas** com 10s de espera |
| Timeout | Aguarda 5s e tenta novamente |
| Erro de conexão | Loga e encerra o loop |
| JSON inválido | Captura `ValueError` e encerra |
| `Ctrl+C` | Salva dados parciais antes de sair |

### Modo de escrita
| Condição | Comportamento |
|----------|---------------|
| Checkpoint existe + `vendas.csv` existe | **Append** (carga incremental) |
| Qualquer outra situação | **Sobrescreve** (carga completa) |

---

## Arquivos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `vendas.csv` | Dados processados (`;` como delimitador, UTF-8) |
| `vendas_raw.csv` | Backup bruto antes do processamento |
| `checkpoint.json` | Timestamp da última execução bem-sucedida |

---

## Logs

O pipeline utiliza prefixos estruturados nas mensagens:

| Prefixo | Significado |
|---------|-------------|
| `[LOAD]` | Início/fim de carga |
| `[ERRO]` | Erros e falhas |
| `[REGISTRO]` | Contagem de registros e deduplicação |

---

## Limitações Conhecidas (Protótipo)

- [ ] Data de fallback (`2024-01-01`) está hardcoded no script
- [ ] Endpoint único — suporta apenas dados de vendas
- [ ] Lista de colunas a remover contém placeholders (`coluna1`, `coluna2`, `coluna3`)
- [ ] Função `tratar_saleitens()` existe mas está desabilitada por padrão
- [ ] Sem testes automatizados
- [ ] Sem integração com sistema de logs estruturado (ex: `logging`, `loguru`)

---

## Roadmap

- [ ] Tornar data de fallback configurável via `.env` ou argumento CLI
- [ ] Parametrizar lista de colunas a remover via config externa
- [ ] Testes unitários para lógica de deduplicação e checkpoint
- [ ] Logging estruturado com níveis (INFO, WARNING, ERROR)
- [ ] Suporte a exportação para banco de dados ou cloud storage
- [ ] Containerização com Docker

---

## Estrutura do Projeto

```
Pipelines/
├── etl_vendas_incremental.py   # Script principal
├── .env                        # Credenciais (não versionar)
├── checkpoint.json             # Estado da última execução (não versionar)
├── vendas.csv                  # Saída processada (não versionar)
├── vendas_raw.csv              # Backup bruto (não versionar)
└── etl_vendas_incremental.md   # Esta documentação
```

> [!IMPORTANT]
> Nunca versione `.env`, `checkpoint.json`, `vendas.csv` ou `vendas_raw.csv`. Adicione-os ao `.gitignore`.

---

## Versão

| Campo  | Valor               |
|--------|---------------------|
| Versão | Incremental (protótipo) |
| Status | Em desenvolvimento  |
