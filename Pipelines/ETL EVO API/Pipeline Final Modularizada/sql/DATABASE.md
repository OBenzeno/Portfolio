# Documentação do Banco de Dados — EvoGestor Pipeline

## Visão Geral

O banco de dados é dividido em dois schemas com responsabilidades distintas:

| Schema | Propósito |
|---|---|
| `db_raw` | Dump flat sem normalização — espelho do CSV limpo, usado para auditoria e reprocessamento |
| `data_warehouse` | Modelo normalizado Galaxy Schema com dimensões e fatos, consumido pelo Power BI |

---

## Schema `db_raw`

Tabelas planas sem foreign keys. Preservam os dados exatamente como recebidos da API, incluindo campos DateTime originais. Servem como camada de backup — não devem ser usadas para análise direta.

### `db_raw.members`

| Coluna | Tipo | Descrição |
|---|---|---|
| `idmember` | Integer (PK) | ID do membro |
| `firstname` | String(255) | Primeiro nome |
| `lastname` | String(255) | Sobrenome |
| `registername` | String(255) | Nome de registro |
| `registerlastname` | String(255) | Sobrenome de registro |
| `usepreferredname` | Boolean | Usa nome preferido |
| `registerdate` | DateTime | Data/hora de cadastro |
| `idbranch` | Integer | ID da filial |
| `branchname` | String(255) | Nome da filial |
| `accessblocked` | Boolean | Acesso bloqueado |
| `blockedreason` | String(255) | Motivo do bloqueio |
| `document` | String(20) | Tipo de documento |
| `documentid` | String(20) | Número do documento |
| `maritalstatus` | String(50) | Estado civil |
| `gender` | String(20) | Gênero |
| `birthdate` | DateTime | Data de nascimento |
| `updatedate` | DateTime | Última atualização |
| `state` | String(50) | Estado |
| `city` | String(100) | Cidade |
| `zipcode` | String(10) | CEP |
| `complement` | String(255) | Complemento |
| `number` | String(20) | Número |
| `country` | String(100) | País |
| `totalfitcoins` | Integer | Saldo de fitcoins |
| `penalized` | Boolean | Penalizado |
| `status` | String(50) | Status do membro |
| `lastaccessdate` | DateTime | Último acesso |
| `conversiondate` | DateTime | Data de conversão |
| `idemployeeconsultant` | Integer | ID do consultor |
| `nameemployeeconsultant` | String(255) | Nome do consultor |
| `idemployeeinstructor` | Integer | ID do instrutor |
| `nameemployeeinstructor` | String(255) | Nome do instrutor |
| `photourl` | String(500) | URL da foto |
| `gympassid` | String(100) | ID Gympass |
| `personaltrainer` | Boolean | É personal trainer |
| `codetotalpass` | String(100) | Código TotalPass |
| `clientwithpromotionalrestriction` | Boolean | Restrição promocional |

---

### `db_raw.sales`

| Coluna | Tipo | Descrição |
|---|---|---|
| `idsale` | Integer (PK) | ID da venda |
| `idsaleitem` | Integer | ID do item da venda |
| `idmember` | Integer | ID do membro |
| `idemployeesale` | Integer | ID do vendedor |
| `nameemployeesale` | String(255) | Nome do vendedor |
| `saledate` | DateTime | Data/hora da venda |
| `updatedate` | DateTime | Última atualização |
| `idbranch` | Integer | ID da filial |
| `idmembership` | Integer | ID do plano |
| `idmembermembership` | Integer | ID da matrícula |
| `item` | String(255) | Nome do item/plano |
| `itemvalue` | Numeric(12,2) | Valor do item |
| `salevalue` | Numeric(12,2) | Valor total da venda |
| `salevaluewithoutcreditvalue` | Numeric(12,2) | Valor sem crédito |
| `quantity` | Integer | Quantidade |
| `idmembershiprenewed` | Integer | ID da matrícula renovada |
| `membershipstartdate` | DateTime | Início da vigência |
| `valuenextmonth` | Numeric(12,2) | Valor do próximo mês |

---

### `db_raw.debtors`

| Coluna | Tipo | Descrição |
|---|---|---|
| `receivableid` | Integer (PK) | ID do recebível |
| `memberid` | Integer | ID do membro |
| `idmembermembership` | Integer | ID da matrícula |
| `receivableidorigin` | Integer | ID de origem |
| `branchid` | Integer | ID da filial |
| `idpaymenttype` | Integer | ID do tipo de pagamento |
| `memberstatus` | String(50) | Status do membro |
| `duedate` | Date | Data de vencimento |
| `paymentdate` | Date | Data de pagamento |
| `registerdate` | DateTime | Data/hora de registro |
| `originalduedate` | Date | Vencimento original |
| `chargedate` | Date | Data da cobrança |
| `dayslate` | Integer | Dias em atraso |
| `debtamount` | Numeric(10,2) | Valor da dívida |
| `debtstatus` | String(50) | Status do débito |
| `paymentorigin` | String(100) | Origem do pagamento |
| `chargeattemptscount` | Integer | Tentativas de cobrança |

---

## Schema `data_warehouse`

Modelo Galaxy Schema normalizado. Todas as tabelas possuem foreign keys. Os campos DateTime da fonte são separados em colunas `Date` e `Time` distintas durante a carga ETL.

### Diagrama de Relacionamentos

```
dim_branch ◄────────────────── members ──────────────────► dim_employee
    ▲                              ▲
    │                              │
    ├──────── sales ───────────────┤
    │           │                  │
    │      dim_planos         dim_employee
    │
    └──────── debtors ─────────────┤
                │             dim_payment_type
                └──────────── members
                              │
                         dim_address (1:1)
                         dim_partnerships (1:N)
```

---

### Dimensões Lookup

#### `data_warehouse.dim_branch`

| Coluna | Tipo | Descrição |
|---|---|---|
| `branchid` | Integer (PK) | ID da filial |
| `branchname` | String(255) | Nome da filial |

> Seeds pré-carregados: `60 = Sete Lagoas`, `327 = Santa Helena`

---

#### `data_warehouse.dim_employee`

| Coluna | Tipo | Descrição |
|---|---|---|
| `idemployee` | Integer (PK) | ID do funcionário |
| `nameemployee` | String(255) | Nome do funcionário |

> Consolida consultores e instrutores em uma única dimensão.

---

#### `data_warehouse.dim_planos`

| Coluna | Tipo | Descrição |
|---|---|---|
| `idmembership` | Integer (PK) | ID do plano |
| `nome_plano` | String(255) | Nome do plano |

---

#### `data_warehouse.dim_payment_type`

| Coluna | Tipo | Descrição |
|---|---|---|
| `idpaymenttype` | Integer (PK) | ID do tipo de pagamento |
| `paymenttype` | String(100) | Descrição do tipo |

---

### Dimensão Principal

#### `data_warehouse.members`

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `idmember` | Integer (PK) | — | ID do membro |
| `firstname` | String(255) | — | Primeiro nome |
| `lastname` | String(255) | — | Sobrenome |
| `registername` | String(255) | — | Nome de registro |
| `registerlastname` | String(255) | — | Sobrenome de registro |
| `usepreferredname` | Boolean | — | Usa nome preferido |
| `idbranch` | Integer | `dim_branch.branchid` | Filial |
| `accessblocked` | Boolean | — | Acesso bloqueado |
| `blockedreason` | String(255) | — | Motivo do bloqueio |
| `document` | String(20) | — | Tipo de documento |
| `documentid` | String(20) | — | Número do documento |
| `maritalstatus` | String(50) | — | Estado civil |
| `gender` | String(20) | — | Gênero |
| `birthdate` | Date | — | Data de nascimento |
| `totalfitcoins` | Integer | — | Saldo de fitcoins |
| `penalized` | Boolean | — | Penalizado |
| `status` | String(50) | — | Status do membro |
| `idemployeeconsultant` | Integer | `dim_employee.idemployee` | Consultor |
| `idemployeeinstructor` | Integer | `dim_employee.idemployee` | Instrutor |
| `photourl` | String(500) | — | URL da foto |
| `personaltrainer` | Boolean | — | É personal trainer |
| `clientwithpromotionalrestriction` | Boolean | — | Restrição promocional |
| `phone_ddi` | String(10) | — | DDI do telefone |
| `phone` | String(50) | — | Telefone |
| `email` | String(255) | — | E-mail |
| `registerdate` | Date | — | Data de cadastro |
| `registertime` | Time | — | Hora de cadastro |
| `updatedate` | Date | — | Data da última atualização |
| `updatetime` | Time | — | Hora da última atualização |
| `lastaccessdate` | Date | — | Data do último acesso |
| `lastaccesstime` | Time | — | Hora do último acesso |
| `conversiondate` | Date | — | Data de conversão |
| `conversiontime` | Time | — | Hora de conversão |

---

### Dimensões Satélite

#### `data_warehouse.dim_address`

Endereço por membro. Relação 1:1 com `members`.

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `idaddress` | Integer (PK, autoincrement) | — | ID interno |
| `idmember` | Integer (UNIQUE) | `members.idmember` | Membro |
| `state` | String(50) | — | Estado |
| `city` | String(100) | — | Cidade |
| `zipcode` | String(10) | — | CEP |
| `complement` | String(255) | — | Complemento |
| `number` | String(20) | — | Número |
| `country` | String(100) | — | País |

> Constraint: `uq_address_member UNIQUE (idmember)`

---

#### `data_warehouse.dim_partnerships`

Parcerias por membro (Gympass, TotalPass). PK composta.

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `idmember` | Integer (PK) | `members.idmember` | Membro |
| `plataforma` | String(50) (PK) | — | `GYMPASS` ou `TOTALPASS` |
| `codigo` | String(100) | — | Código da parceria |

---

### Tabelas Fato

#### `data_warehouse.sales`

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `idsale` | Integer (PK) | — | ID da venda |
| `idsaleitem` | Integer | — | ID do item |
| `idmember` | Integer | `members.idmember` | Membro |
| `idemployeesale` | Integer | `dim_employee.idemployee` | Vendedor |
| `idbranch` | Integer | `dim_branch.branchid` | Filial |
| `idmembership` | Integer | `dim_planos.idmembership` | Plano |
| `idmembermembership` | Integer | — | ID da matrícula |
| `salevalue` | Numeric(12,2) | — | Valor total da venda |
| `itemvalue` | Numeric(12,2) | — | Valor do item |
| `salevaluewithoutcreditvalue` | Numeric(12,2) | — | Valor sem crédito |
| `quantity` | Integer | — | Quantidade |
| `idmembershiprenewed` | Integer | — | Matrícula renovada |
| `membershipstartdate` | Date | — | Início da vigência |
| `valuenextmonth` | Numeric(12,2) | — | Valor próximo mês |
| `saledate` | Date | — | Data da venda |
| `saletime` | Time | — | Hora da venda |
| `updatedate` | Date | — | Data da atualização |
| `updatetime` | Time | — | Hora da atualização |

> Registros com `salevalue = 0` correspondem a lançamentos de agregadores — filtrar nas análises.

---

#### `data_warehouse.debtors`

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `receivableid` | Integer (PK) | — | ID do recebível |
| `memberid` | Integer | `members.idmember` | Membro |
| `idmembermembership` | Integer | — | ID da matrícula |
| `receivableidorigin` | Integer | — | ID de origem |
| `branchid` | Integer | `dim_branch.branchid` | Filial |
| `idpaymenttype` | Integer | `dim_payment_type.idpaymenttype` | Tipo de pagamento |
| `memberstatus` | String(50) | — | Status do membro |
| `duedate` | Date | — | Vencimento |
| `paymentdate` | Date | — | Data de pagamento |
| `originalduedate` | Date | — | Vencimento original |
| `chargedate` | Date | — | Data da cobrança |
| `dayslate` | Integer | — | Dias em atraso |
| `debtamount` | Numeric(10,2) | — | Valor do débito |
| `debtstatus` | String(50) | — | Status do débito |
| `paymentorigin` | String(100) | — | Origem do pagamento |
| `chargeattemptscount` | Integer | — | Tentativas de cobrança |
| `registerdate` | Date | — | Data de registro |
| `registertime` | Time | — | Hora de registro |

---

## Ordem de Criação das Tabelas

A criação respeita as dependências de foreign key:

```
1. dim_branch
2. dim_employee
3. dim_planos
4. dim_payment_type
5. members
6. dim_address
7. dim_partnerships
8. sales
9. debtors
```

---

## Decisões de Design

### Separação de DateTime em Date + Time
Todos os campos de data/hora do `data_warehouse` são armazenados em colunas separadas (`*date` e `*time`). A derivação ocorre na camada ETL (Python/Pandas) antes do upsert. O `db_raw` preserva os `DateTime` originais da API para fins de auditoria.

### Idempotência
A carga usa `ON CONFLICT DO UPDATE` (upsert) pela chave primária. A pipeline pode ser executada múltiplas vezes sem duplicar registros.

### Members Stub
Quando `sales` ou `debtors` são carregados antes de `members`, a pipeline insere registros stub (somente `idmember`) para satisfazer a FK — sem sobrescrever dados reais já existentes (`ON CONFLICT DO NOTHING`).

### Galaxy Schema
`members` é a dimensão central compartilhada por `sales` e `debtors`. As dimensões satélite (`dim_address`, `dim_partnerships`) estendem `members` sem adicionar colunas à tabela principal.
