================================================================================
  DOCUMENTACAO DO BANCO DE DADOS — Pipeline BI
================================================================================

VISAO GERAL
-----------
O modelo relacional adota o padrao Galaxy Schema (tambem chamado de
Constellation Schema), composto por duas tabelas fato (sales e debtors) que
compartilham um conjunto de tabelas dimensao. A tabela members funciona como
dimensao principal, servindo de eixo central do modelo.

    dim_branch ──┬──> members ──> dim_address
                 │        │
    dim_employee ┘        ├──> dim_partnerships
                          │
                          ├──> sales ──> dim_planos
                          │       └──> dim_employee
                          │       └──> dim_branch
                          │
                          └──> debtors ──> dim_payment_type
                                    └──> dim_branch


================================================================================
  TABELAS
================================================================================

--------------------------------------------------------------------------------
  DIMENSOES LOOKUP
  (sem dependencias externas — devem ser criadas primeiro)
--------------------------------------------------------------------------------

  dim_branch
  ----------
  Cadastro de filiais.

  Coluna        Tipo          Descricao
  ----------    ----------    ---------------------------
  branchid      INTEGER PK    Identificador da filial
  branchname    VARCHAR(255)  Nome da filial


  dim_employee
  ------------
  Cadastro de funcionarios (consultores e instrutores).
  Utilizada duas vezes em members: idemployeeconsultant e idemployeeinstructor.

  Coluna          Tipo          Descricao
  ------------    ----------    ---------------------------
  idemployee      INTEGER PK    Identificador do funcionario
  nameemployee    VARCHAR(255)  Nome do funcionario


  dim_planos
  ----------
  Cadastro de planos/modalidades vendidas.
  Inclui planos convencionais e planos parceiros (GYMPASS, TOTALPASS, SKY PASS).

  Coluna          Tipo          Descricao
  ------------    ----------    ---------------------------
  idmembership    INTEGER PK    Identificador do plano
  nome_plano      VARCHAR(255)  Nome do plano


  dim_payment_type
  ----------------
  Cadastro de tipos de pagamento.

  Coluna           Tipo          Descricao
  -------------    ----------    ----------------------------
  idpaymenttype    INTEGER PK    Identificador do tipo
  paymenttype      VARCHAR(100)  Descricao do tipo de pagamento


--------------------------------------------------------------------------------
  DIMENSAO PRINCIPAL
--------------------------------------------------------------------------------

  members
  -------
  Cadastro central de membros.
  Depende de: dim_branch, dim_employee.
  Nota: endereco e parcerias foram normalizados em dim_address e
  dim_partnerships respectivamente.

  Coluna                            Tipo           Descricao
  --------------------------------  -------------  ------------------------------------
  idmember                          INTEGER PK     Identificador do membro
  firstname                         VARCHAR(255)   Primeiro nome
  lastname                          VARCHAR(255)   Sobrenome
  registername                      VARCHAR(255)   Nome de registro
  registerlastname                  VARCHAR(255)   Sobrenome de registro
  usepreferredname                  BOOLEAN        Usa nome preferido
  registerdate                      TIMESTAMP      Data de cadastro
  idbranch                          INT FK         -> dim_branch.branchid
  accessblocked                     BOOLEAN        Acesso bloqueado
  blockedreason                     VARCHAR(255)   Motivo do bloqueio
  document                          VARCHAR(20)    CPF/documento principal
  documentid                        VARCHAR(20)    RG ou documento secundario
  maritalstatus                     VARCHAR(50)    Estado civil
  gender                            VARCHAR(20)    Genero
  birthdate                         DATE           Data de nascimento
  updatedate                        TIMESTAMP      Ultima atualizacao
  totalfitcoins                     INTEGER        Saldo de fitcoins
  penalized                         BOOLEAN        Membro penalizado
  status                            VARCHAR(50)    Status atual (ativo, inativo, etc.)
  lastaccessdate                    TIMESTAMP      Ultimo acesso
  conversiondate                    TIMESTAMP      Data de conversao para membro
  idemployeeconsultant              INT FK         -> dim_employee.idemployee
  idemployeeinstructor              INT FK         -> dim_employee.idemployee
  photourl                          VARCHAR(500)   URL da foto de perfil
  personaltrainer                   BOOLEAN        E personal trainer
  clientwithpromotionalrestriction  BOOLEAN        Restricao promocional


--------------------------------------------------------------------------------
  DIMENSOES SATELITE
  (dependem de members — criadas apos members)
--------------------------------------------------------------------------------

  dim_address
  -----------
  Endereco de cada membro. Relacionamento 1:1 esperado (um endereco por membro).

  Coluna      Tipo           Descricao
  ----------  -------------  ------------------------------------
  idaddress   SERIAL PK      Identificador gerado automaticamente
  idmember    INT FK         -> members.idmember
  state       VARCHAR(50)    Estado (UF)
  city        VARCHAR(100)   Cidade
  zipcode     VARCHAR(10)    CEP
  complement  VARCHAR(255)   Complemento
  number      VARCHAR(20)    Numero
  country     VARCHAR(100)   Pais


  dim_partnerships
  ----------------
  Codigos de plataformas parceiras vinculadas a cada membro.
  Chave primaria composta: (idmember, plataforma).
  Um membro pode ter multiplas plataformas.

  Coluna      Tipo           Descricao
  ----------  -------------  ------------------------------------
  idmember    INT PK+FK      -> members.idmember
  plataforma  VARCHAR(50) PK Nome da plataforma parceira
  codigo      VARCHAR(100)   Codigo do membro na plataforma


--------------------------------------------------------------------------------
  TABELAS FATO
  (dependem de members e das dimensoes lookup — criadas por ultimo)
--------------------------------------------------------------------------------

  sales
  -----
  Vendas realizadas. Resultado da mesclagem de sales e saleitens da API.
  Relacao 1:1 confirmada em dados: 2274 idsale unicos, 0 com multiplos itens.
  Nota: planos parceiros (GYMPASS, TOTALPASS, SKY PASS) aparecem com
  salevalue = 0.0 pois o pagamento e feito externamente pela plataforma.

  Coluna                        Tipo            Descricao
  ----------------------------  --------------  ----------------------------------------
  idsale                        INTEGER PK      Identificador da venda (PK tabela mae)
  idsaleitem                    INTEGER         ID do item de venda (herdado da mesclagem)
  idmember                      INT FK          -> members.idmember
  idemployeesale                INT FK          -> dim_employee.idemployee
  idbranch                      INT FK          -> dim_branch.branchid
  idmembership                  INT FK          -> dim_planos.idmembership
  idmembermembership            INTEGER         Ref. contrato matricula (sem FK — inativo)
  saledate                      TIMESTAMP       Data da venda
  updatedate                    TIMESTAMP       Data da ultima atualizacao
  salevalue                     NUMERIC(12,2)   Valor total da venda
  itemvalue                     NUMERIC(12,2)   Valor do item
  salevaluewithoutcreditvalue   NUMERIC(12,2)   Valor sem credito aplicado
  quantity                      INTEGER         Quantidade
  idmembershiprenewed           INTEGER         ID do plano renovado (se houver)
  membershipstartdate           TIMESTAMP       Inicio da vigencia do plano
  valuenextmonth                NUMERIC(12,2)   Valor previsto para o proximo mes


  debtors
  -------
  Inadimplencia e cobranças em aberto.

  Coluna                  Tipo            Descricao
  ----------------------  --------------  ----------------------------------------
  receivableid            INTEGER PK      Identificador da cobranca
  memberid                INT FK          -> members.idmember
  idmembermembership      INTEGER         Ref. contrato (sem FK — tabela inativa)
  receivableidorigin      INTEGER         ID da cobranca original (renegociacao)
  branchid                INT FK          -> dim_branch.branchid
  idpaymenttype           INT FK          -> dim_payment_type.idpaymenttype
  memberstatus            VARCHAR(50)     Status do membro no momento da cobranca
  duedate                 DATE            Data de vencimento
  paymentdate             DATE            Data de pagamento (se pago)
  registerdate            TIMESTAMP       Data de registro da cobranca
  originalduedate         DATE            Vencimento original (antes de renegociacao)
  chargedate              DATE            Data da tentativa de cobranca
  dayslate                INTEGER         Dias de atraso
  debtamount              NUMERIC(10,2)   Valor da divida
  debtstatus              VARCHAR(50)     Status da cobranca (aberta, paga, cancelada)
  paymentorigin           VARCHAR(100)    Canal de pagamento
  chargeattemptscount     INTEGER         Numero de tentativas de cobranca


================================================================================
  ORDEM DE CRIACAO DAS TABELAS
================================================================================

  A ordem abaixo garante que todas as Foreign Keys referenciem tabelas ja
  existentes no banco. Executar os scripts em outra ordem resultara em erro
  de FK no PostgreSQL.

  Passo   Tabela              Depende de
  ------  ------------------  ------------------------------------------
  1       dim_branch          (sem dependencias)
  2       dim_employee        (sem dependencias)
  3       dim_planos          (sem dependencias)
  4       dim_payment_type    (sem dependencias)
  5       members             dim_branch, dim_employee
  6       dim_address         members
  7       dim_partnerships    members
  8       sales               members, dim_branch, dim_planos, dim_employee
  9       debtors             members, dim_branch, dim_payment_type


================================================================================
  TABELAS INATIVAS (pendentes de validacao)
================================================================================

  As tabelas abaixo existem em sql/inactive/ e NAO devem ser criadas ate
  validacao completa dos dados.

  Tabela              Motivo
  ------------------  ---------------------------------------------------------
  membermembership    Contem coluna aninhada (receivables) que precisa ser
                      explodida e tratada antes do uso
  receivables         Relacionamento com membermembership e sales precisa ser
                      validado com dados reais

  As colunas idmembermembership em sales e debtors sao mantidas como referencia
  informativa (sem FK) ate que membermembership seja promovida para ativa.

================================================================================
