# Pipeline de Vendas — v1

> [!WARNING]
> **VERSÃO PROTÓTIPO** — Este pipeline está em fase inicial de desenvolvimento. A estrutura, os parâmetros e os comportamentos podem mudar significativamente nas próximas versões. Não utilize em ambientes de produção sem validação prévia.

---

## Visão Geral

Pipeline ETL para extração de dados de vendas via API REST, com paginação automática, tratamento de erros e exportação para CSV.

**Arquivo principal:** `pipeline_vendas_v1.py`

---

## Fluxo de Dados

```
.env (credenciais)
    │
    ▼
Autenticação HTTP Basic (DNS + TOKEN)
    │
    ▼
Requisições paginadas à API (50 registros/requisição)
    │
    ▼
Tratamento de erros e retentativas
    │
    ▼
Normalização do JSON e limpeza de colunas
    │
    ▼
Exportação → sales.csv (delimitador: ;)
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

Crie um arquivo `.env` na mesma pasta do script com as seguintes variáveis:

```env
API_URL=https://sua-api.exemplo.com/endpoint
API_DNS=seu_usuario
API_TOKEN=seu_token
```

| Variável    | Descrição                                  |
|-------------|--------------------------------------------|
| `API_URL`   | Endpoint da API de vendas                  |
| `API_DNS`   | Usuário para autenticação HTTP Basic       |
| `API_TOKEN` | Token/senha para autenticação HTTP Basic   |

---

## Como Executar

```bash
python pipeline_vendas_v1.py
```

---

## Comportamento

### Paginação
- Busca **50 registros por requisição** com incremento de offset automático.
- Encerra quando a resposta retorna menos de 50 registros (última página).

### Filtros aplicados
| Parâmetro       | Valor                                          |
|-----------------|------------------------------------------------|
| `idBranch`      | `null` (todas as filiais)                      |
| `dateSaleStart` | `2026-01-01T00:00:00` (fixo — ver limitações) |
| `dateSaleEnd`   | Data/hora atual (fuso: `America/Fortaleza`)    |

### Tratamento de Erros
| Situação           | Comportamento                         |
|--------------------|---------------------------------------|
| HTTP 429           | Aguarda 10s e tenta novamente         |
| HTTP 401           | Loga erro de autenticação e encerra   |
| Outros erros HTTP  | Aguarda 10s e tenta novamente         |
| Timeout            | Aguarda 5s e tenta novamente          |
| Erro de conexão    | Loga o erro e encerra o loop          |
| JSON inválido      | Captura `ValueError` e loga           |

### Rate Limiting
- Intervalo de **1,8 segundos** entre cada requisição para respeitar limites da API.

---

## Saída

Arquivo gerado: **`sales.csv`**

- Delimitador: `;`
- Encoding: `UTF-8`
- Colunas: normalizadas (minúsculas, sem espaços)
  - Exemplo: `"Sales Amount"` → `"sales_amount"`

---

## Limitações Conhecidas (Protótipo)

- [ ] Data de início (`dateSaleStart`) está fixa no código — deve ser parametrizável
- [ ] Sem suporte a múltiplos endpoints ou múltiplas filiais de forma configurável
- [ ] Sem schema de validação dos dados recebidos
- [ ] Destino de saída (CSV local) ainda não suporta exportação para banco de dados ou cloud storage
- [ ] Sem testes automatizados
- [ ] Logging básico via `print` — sem integração com sistema de logs estruturado

---

## Roadmap

- [ ] Parametrização do intervalo de datas via argumentos de linha de comando
- [ ] Suporte a múltiplos destinos de saída (banco de dados, S3, GCS)
- [ ] Schema de validação com `pydantic` ou `pandera`
- [ ] Testes unitários e de integração
- [ ] Logging estruturado com `logging` ou `loguru`
- [ ] Containerização com Docker

---

## Estrutura do Projeto

```
Pipelines/
├── pipeline_vendas_v1.py   # Script principal
├── .env                    # Credenciais (não versionar)
├── sales.csv               # Saída gerada (não versionar)
└── README.md               # Esta documentação
```

> [!IMPORTANT]
> Nunca versione o arquivo `.env` ou `sales.csv`. Adicione-os ao `.gitignore`.

---

## Versão

| Campo   | Valor         |
|---------|---------------|
| Versão  | v1 (protótipo) |
| Status  | Em desenvolvimento |
| Autor   | Weslley Bitencourt |
