# Documentação do Banco de Dados — Pipeline BI

## Visão Geral

O modelo relacional adota o padrão **Galaxy Schema** (também chamado de Constellation Schema), composto por **duas tabelas fato** (`sales` e `debtors`) que compartilham um conjunto de **tabelas dimensão**. A tabela `members` funciona como **dimensão principal**, servindo de eixo central do modelo.

```
dim_branch ──┬──→ members ──→ dim_address
             │        │
dim_employee ┘        ├──→ dim_partnerships
                      │
                      ├──→ sales ──→ dim_planos
                      │       └──→ dim_employee
                      │       └──→ dim_branch
                      │
                      └──→ debtors ──→ dim_payment_type
                                └──→ dim_branch
```

---

## Tabelas

### Dimensões Lookup

Tabelas de referência simples, sem dependências externas. Devem ser criadas primeiro.

---

#### `dim_branch`
Cadastro de filiais.

| Coluna | Tipo | Descrição |
|---|---|---|
| `branchid` | INTEGER PK | Identificador da filial |
| `branchname` | VARCHAR(255) | Nome da filial |

---

#### `dim_employee`
Cadastro de funcionários (consultores e instrutores).

| Coluna | Tipo | Descrição |
|---|---|---|
| `idemployee` | INTEGER PK | Identificador do funcionário |
| `nameemployee` | VARCHAR(255) | Nome do funcionário |

> Utilizada duas vezes em `members`: para `idemployeeconsultant` e `idemployeeinstructor`.

---

#### `dim_planos`
Cadastro de planos/modalidades vendidas.

| Coluna | Tipo | Descrição |
|---|---|---|
| `idmembership` | INTEGER PK | Identificador do plano |
| `nome_plano` | VARCHAR(255) | Nome do plano |

> Inclui planos convencionais e planos parceiros (GYMPASS, TOTALPASS, SKY PASS, etc.).

---

#### `dim_payment_type`
Cadastro de tipos de pagamento.

| Coluna | Tipo | Descrição |
|---|---|---|
| `idpaymenttype` | INTEGER PK | Identificador do tipo |
| `paymenttype` | VARCHAR(100) | Descrição do tipo de pagamento |

---

### Dimensão Principal

#### `members`
Cadastro central de membros. Depende de `dim_branch` e `dim_employee`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `idmember` | INTEGER PK | Identificador do membro |
| `firstname` | VARCHAR(255) | Primeiro nome |
| `lastname` | VARCHAR(255) | Sobrenome |
| `registername` | VARCHAR(255) | Nome de registro |
| `registerlastname` | VARCHAR(255) | Sobrenome de registro |
| `usepreferredname` | BOOLEAN | Usa nome preferido |
| `registerdate` | TIMESTAMP | Data de cadastro |
| `idbranch` | INTEGER FK→dim_branch | Filial do membro |
| `accessblocked` | BOOLEAN | Acesso bloqueado |
| `blockedreason` | VARCHAR(255) | Motivo do bloqueio |
| `document` | VARCHAR(20) | CPF/documento principal |
| `documentid` | VARCHAR(20) | RG ou documento secundário |
| `maritalstatus` | VARCHAR(50) | Estado civil |
| `gender` | VARCHAR(20) | Gênero |
| `birthdate` | DATE | Data de nascimento |
| `updatedate` | TIMESTAMP | Última atualização |
| `totalfitcoins` | INTEGER | Saldo de fitcoins |
| `penalized` | BOOLEAN | Membro penalizado |
| `status` | VARCHAR(50) | Status atual (ativo, inativo, etc.) |
| `lastaccessdate` | TIMESTAMP | Último acesso |
| `conversiondate` | TIMESTAMP | Data de conversão para membro |
| `idemployeeconsultant` | INTEGER FK→dim_employee | Consultor responsável |
| `idemployeeinstructor` | INTEGER FK→dim_employee | Instrutor responsável |
| `photourl` | VARCHAR(500) | URL da foto de perfil |
| `personaltrainer` | BOOLEAN | É personal trainer |
| `clientwithpromotionalrestriction` | BOOLEAN | Restrição promocional |

> **Nota:** endereço e parcerias foram normalizados em `dim_address` e `dim_partnerships` respectivamente.

---

### Dimensões Satélite

Dependem de `members`. Devem ser criadas após `members`.

---

#### `dim_address`
Endereço de cada membro. Relacionamento 1:1 esperado (um endereço por membro).

| Coluna | Tipo | Descrição |
|---|---|---|
| `idaddress` | SERIAL PK | Identificador gerado automaticamente |
| `idmember` | INTEGER FK→members | Membro ao qual pertence |
| `state` | VARCHAR(50) | Estado (UF) |
| `city` | VARCHAR(100) | Cidade |
| `zipcode` | VARCHAR(10) | CEP |
| `complement` | VARCHAR(255) | Complemento |
| `number` | VARCHAR(20) | Número |
| `country` | VARCHAR(100) | País |

---

#### `dim_partnerships`
Codigos de plataformas parceiras vinculadas a cada membro (GYMPASS, TOTALPASS, SKY PASS, etc.).

| Coluna | Tipo | Descrição |
|---|---|---|
| `idmember` | INTEGER PK+FK→members | Membro |
| `plataforma` | VARCHAR(50) PK | Nome da plataforma parceira |
| `codigo` | VARCHAR(100) | Código do membro na plataforma |

> Chave primária composta: `(idmember, plataforma)`. Um membro pode ter múltiplas plataformas.

---

### Tabelas Fato

Dependem de `members` e das dimensões lookup. Criadas por último.

---

#### `sales`
Vendas realizadas. Resultado da mesclagem das tabelas `sales` e `saleitens` da API (relação 1:1 confirmada em dados: 2274 idsale únicos, 0 com múltiplos itens).

| Coluna | Tipo | Descrição |
|---|---|---|
| `idsale` | INTEGER PK | Identificador da venda (PK original da tabela mãe) |
| `idsaleitem` | INTEGER | Identificador do item de venda (herdado da mesclagem) |
| `idmember` | INTEGER FK→members | Membro que realizou a compra |
| `idemployeesale` | INTEGER FK→dim_employee | Funcionário que realizou a venda |
| `idbranch` | INTEGER FK→dim_branch | Filial da venda |
| `idmembership` | INTEGER FK→dim_planos | Plano vendido |
| `idmembermembership` | INTEGER | Referência ao contrato de matrícula (sem FK — tabela inativa pendente de validação) |
| `saledate` | TIMESTAMP | Data da venda |
| `updatedate` | TIMESTAMP | Data da última atualização |
| `salevalue` | NUMERIC(12,2) | Valor total da venda |
| `itemvalue` | NUMERIC(12,2) | Valor do item |
| `salevaluewithoutcreditvalue` | NUMERIC(12,2) | Valor sem crédito aplicado |
| `quantity` | INTEGER | Quantidade |
| `idmembershiprenewed` | INTEGER | ID do plano renovado (se houver) |
| `membershipstartdate` | TIMESTAMP | Início da vigência do plano |
| `valuenextmonth` | NUMERIC(12,2) | Valor previsto para o próximo mês |

> **Nota:** planos parceiros (GYMPASS, TOTALPASS, SKY PASS) aparecem com `salevalue = 0.0` pois o pagamento é feito externamente pela plataforma parceira.

---

#### `debtors`
Inadimplência e cobranças em aberto.

| Coluna | Tipo | Descrição |
|---|---|---|
| `receivableid` | INTEGER PK | Identificador da cobrança |
| `memberid` | INTEGER FK→members | Membro devedor |
| `idmembermembership` | INTEGER | Referência ao contrato (sem FK — tabela inativa pendente de validação) |
| `receivableidorigin` | INTEGER | ID da cobrança original (em caso de renegociação) |
| `branchid` | INTEGER FK→dim_branch | Filial |
| `idpaymenttype` | INTEGER FK→dim_payment_type | Tipo de pagamento |
| `memberstatus` | VARCHAR(50) | Status do membro no momento da cobrança |
| `duedate` | DATE | Data de vencimento |
| `paymentdate` | DATE | Data de pagamento (se pago) |
| `registerdate` | TIMESTAMP | Data de registro da cobrança |
| `originalduedate` | DATE | Vencimento original (antes de renegociação) |
| `chargedate` | DATE | Data da tentativa de cobrança |
| `dayslate` | INTEGER | Dias de atraso |
| `debtamount` | NUMERIC(10,2) | Valor da dívida |
| `debtstatus` | VARCHAR(50) | Status da cobrança (aberta, paga, cancelada, etc.) |
| `paymentorigin` | VARCHAR(100) | Canal de pagamento |
| `chargeattemptscount` | INTEGER | Número de tentativas de cobrança |

---

## Ordem de Criação das Tabelas

A ordem abaixo garante que todas as Foreign Keys referenciem tabelas já existentes no banco:

```
1. dim_branch          — sem dependências
2. dim_employee        — sem dependências
3. dim_planos          — sem dependências
4. dim_payment_type    — sem dependências
5. members             — depende de: dim_branch, dim_employee
6. dim_address         — depende de: members
7. dim_partnerships    — depende de: members
8. sales               — depende de: members, dim_branch, dim_planos, dim_employee
9. debtors             — depende de: members, dim_branch, dim_payment_type
```

> Executar os scripts em outra ordem resultará em erro de FK no PostgreSQL.

---

## Tabelas Inativas (pendentes de validação)

As tabelas abaixo existem na pasta `sql/inactive/` e **não devem ser criadas** até validação completa dos dados:

| Tabela | Motivo |
|---|---|
| `membermembership` | Contém coluna aninhada (`receivables`) que precisa ser explodida e tratada antes do uso |
| `receivables` | Relacionamento com `membermembership` e `sales` precisa ser validado com dados reais |

Colunas `idmembermembership` em `sales` e `debtors` são mantidas como referência informativa (sem FK) até que `membermembership` seja promovida para ativa.

---

## Diagrama ER

![DER Tabelas Ativas](active/der_active.png)
