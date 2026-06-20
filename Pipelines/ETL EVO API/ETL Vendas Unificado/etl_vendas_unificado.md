# ETL Vendas — Unificado

> [!WARNING]
> **VERSÃO PROTÓTIPO** — Pipeline em fase de desenvolvimento. A configuração de endpoints e o mapeamento de parâmetros ainda podem mudar. Não utilizar em produção sem validação completa do `endpoint_config.json`.

---

## Visão Geral

Pipeline ETL **multi-endpoint** que centraliza a extração de diferentes fontes de dados (vendas, recebíveis, associados, prospectos) em um único script. O comportamento é controlado por um arquivo de configuração externo (`endpoint_config.json`), tornando o código extensível para novos endpoints sem alterações no script principal.

**Arquivo principal:** `etl_vendas_unificado.py`

---

## Fluxo de Dados

```
.env (credenciais + aliases de endpoints)
    │
    ▼
Seleção de endpoint via input do usuário
    │
    ▼
endpoint_config.json → parâmetros dinâmicos do endpoint selecionado
    │
    ▼
checkpoint_{alias}.json → define data de início (ou 2024-01-01 se ausente)
    │
    ▼
Requisições paginadas à API (take configurável por endpoint)
    │
    ▼
Tratamento de erros (máx. 5 tentativas) + signal handler (Ctrl+C)
    │
    ▼
Normalização JSON + limpeza de colunas
    │
    ▼
Backup bruto → {alias}_raw.csv
    │
    ▼
Deduplicação por idField configurável (batch + cross-file)
    │
    ├── Carga incremental → append em {alias}.csv
    └── Carga completa   → sobrescreve {alias}.csv
    │
    ▼
Atualização de checkpoint_{alias}.json
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

### 1. Arquivo `.env`

```env
API_DNS=seu_usuario
API_TOKEN=seu_token

# Aliases → URLs dos endpoints
END_POINT_SALES=https://sua-api.exemplo.com/vendas
END_POINT_RECEIVABLES=https://sua-api.exemplo.com/recebíveis
END_POINT_MEMBERSHIP=https://sua-api.exemplo.com/associados
END_POINT_PROSPECTS=https://sua-api.exemplo.com/prospectos
```

| Variável                | Descrição                                |
|-------------------------|------------------------------------------|
| `API_DNS`               | Usuário para autenticação HTTP Basic     |
| `API_TOKEN`             | Token/senha para autenticação HTTP Basic |
| `END_POINT_SALES`       | URL do endpoint de vendas                |
| `END_POINT_RECEIVABLES` | URL do endpoint de recebíveis            |
| `END_POINT_MEMBERSHIP`  | URL do endpoint de associados            |
| `END_POINT_PROSPECTS`   | URL do endpoint de prospectos            |

### 2. Arquivo `endpoint_config.json`

Define os parâmetros específicos de cada endpoint. Exemplo de estrutura:

```json
{
  "sales": {
    "idBranch": "0",
    "take": 100,
    "skip": 0,
    "dateStartKey": "dateSaleStart",
    "dateEndKey": "dateSaleEnd",
    "idField": "idsale",
    "responseKey": "data"
  },
  "receivables": {
    "idBranch": "0",
    "take": 100,
    "skip": 0,
    "dateStartKey": "dateReceivableStart",
    "dateEndKey": "dateReceivableEnd",
    "idField": "idreceivable",
    "responseKey": "data"
  }
}
```

| Campo          | Descrição                                                       |
|----------------|-----------------------------------------------------------------|
| `idBranch`     | Filtro de filial (`"0"` = todas)                               |
| `take`         | Registros por página                                            |
| `skip`         | Offset inicial                                                  |
| `dateStartKey` | Nome do parâmetro de data de início na API                     |
| `dateEndKey`   | Nome do parâmetro de data de fim na API                        |
| `idField`      | Coluna usada como identificador único para deduplicação         |
| `responseKey`  | Chave do JSON de resposta que contém o array de dados           |

---

## Como Executar

```bash
python etl_vendas_unificado.py
```

O script solicitará a seleção do endpoint:

```
Endpoints disponíveis: sales, receivables, membership, prospects
Informe o endpoint: sales
```

---

## Comportamento

### Checkpoint por Endpoint
- Cada endpoint possui seu próprio arquivo de checkpoint (`checkpoint_{alias}.json`).
- Falha em um endpoint **não afeta** o estado dos demais.
- Atualizado **somente após conclusão bem-sucedida**.

### Paginação
- Tamanho do batch configurável por endpoint via `endpoint_config.json`.
- Intervalo de **1,8 segundos** entre requisições.
- Encerra quando a resposta retorna menos registros que o `take` configurado.

### Deduplicação (dupla camada)
| Camada | Escopo | Descrição |
|--------|--------|-----------|
| 1 | Batch atual | Remove duplicatas pelo `idField` dentro dos dados recém-buscados |
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
| `Ctrl+C` / SIGINT | Signal handler intercepta, loga aviso e encerra sem atualizar checkpoint |

### Modo de Escrita
| Condição | Comportamento |
|----------|---------------|
| Checkpoint existe + arquivo CSV existe | **Append** (carga incremental) |
| Qualquer outra situação | **Sobrescreve** (carga completa) |

---

## Arquivos Gerados

Os nomes são dinâmicos com base no alias do endpoint selecionado (`{alias}`):

| Arquivo | Descrição |
|---------|-----------|
| `{alias}.csv` | Dados processados (`;` como delimitador, UTF-8) |
| `{alias}_raw.csv` | Backup bruto antes do processamento |
| `checkpoint_{alias}.json` | Timestamp da última execução bem-sucedida |

Exemplos para o endpoint `sales`:

```
sales.csv
sales_raw.csv
checkpoint_sales.json
```

---

## Extensibilidade

Para adicionar um novo endpoint **sem alterar o código**:

1. Adicione a URL no `.env`:
   ```env
   END_POINT_NOVO=https://api.exemplo.com/novo
   ```

2. Registre o alias no dicionário `ENDPOINT_ALIASES` dentro do script (única alteração de código necessária).

3. Adicione a configuração no `endpoint_config.json`:
   ```json
   "novo": {
     "idBranch": "0",
     "take": 100,
     "skip": 0,
     "dateStartKey": "dateNovoStart",
     "dateEndKey": "dateNovoEnd",
     "idField": "idnovo",
     "responseKey": "data"
   }
   ```

---

## Limitações Conhecidas (Protótipo)

- [ ] Seleção de endpoint via `input()` — não suporta execução não interativa (ex: agendadores como cron/Airflow)
- [ ] Data de fallback (`2024-01-01`) está hardcoded no script
- [ ] Adicionar novos aliases ainda requer edição do dicionário `ENDPOINT_ALIASES` no código
- [ ] Lista de colunas a remover contém placeholders (`coluna1`, `coluna2`, `coluna3`)
- [ ] Sem testes automatizados
- [ ] Sem integração com sistema de logs estruturado

---

## Roadmap

- [ ] Aceitar endpoint como argumento de linha de comando (`--endpoint sales`) para execução não interativa
- [ ] Mover `ENDPOINT_ALIASES` para o `endpoint_config.json`, eliminando necessidade de editar o código
- [ ] Tornar data de fallback configurável via `.env`
- [ ] Parametrizar lista de colunas a remover por endpoint no `endpoint_config.json`
- [ ] Testes unitários para lógica de roteamento e deduplicação
- [ ] Logging estruturado com níveis (INFO, WARNING, ERROR)
- [ ] Suporte a exportação para banco de dados ou cloud storage
- [ ] Containerização com Docker

---

## Estrutura do Projeto

```
Pipelines/
├── etl_vendas_unificado.py     # Script principal
├── endpoint_config.json        # Configuração dos endpoints (versionar)
├── .env                        # Credenciais (não versionar)
├── checkpoint_sales.json       # Checkpoint por endpoint (não versionar)
├── sales.csv                   # Saída por endpoint (não versionar)
├── sales_raw.csv               # Backup bruto por endpoint (não versionar)
└── etl_vendas_unificado.md     # Esta documentação
```

> [!IMPORTANT]
> Nunca versione `.env`, arquivos `checkpoint_*.json`, `*.csv`. O `endpoint_config.json` **pode e deve** ser versionado, pois é parte da configuração do projeto.

---

## Comparativo das Versões

| Característica | `pipeline_vendas_v1.py` | `etl_vendas_incremental.py` | `etl_vendas_unificado.py` |
|---|---|---|---|
| Checkpoint | Não | Sim | Sim (por endpoint) |
| Multi-endpoint | Não | Não | **Sim (4 endpoints)** |
| Deduplicação | Não | Dupla camada | Dupla camada |
| Backup bruto | Não | Sim | Sim |
| Tentativas de retry | Infinitas | Máx. 5 | Máx. 5 |
| Signal handler | Não | Apenas Ctrl+C | **SIGINT completo** |
| Config externa | Não | Não | **Sim (`endpoint_config.json`)** |
| Batch size | 50 | 100 | Configurável |
| Execução não interativa | Sim | Sim | **Não (requer `input()`)** |

---

## Versão

| Campo  | Valor                    |
|--------|--------------------------|
| Versão | Unificado (protótipo)    |
| Status | Em desenvolvimento       |
