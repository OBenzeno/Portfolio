"""
Definição das tabelas via SQLAlchemy Core para dois schemas:

  db_raw          — dump flat sem FK, espelho do CSV limpo (camada de backup)
  data_warehouse  — modelo normalizado Galaxy Schema com dims e fatos
"""

from sqlalchemy import (
    MetaData, Table, Column,
    Integer, String, Numeric, Boolean, DateTime, Date, Time,
    ForeignKey, UniqueConstraint,
)

# ── Metadata por schema ────────────────────────────────────────────────────────

raw_meta        = MetaData(schema="db_raw")
relational_meta = MetaData(schema="data_warehouse")


# ==============================================================================
#  SCHEMA RAW — tabelas flat, sem constraints de FK, para backup/auditoria
# ==============================================================================

raw_members = Table("members", raw_meta,
    Column("idmember",                          Integer,     primary_key=True),
    Column("firstname",                         String(255)),
    Column("lastname",                          String(255)),
    Column("registername",                      String(255)),
    Column("registerlastname",                  String(255)),
    Column("usepreferredname",                  Boolean),
    Column("registerdate",                      DateTime),
    Column("idbranch",                          Integer),
    Column("branchname",                        String(255)),
    Column("accessblocked",                     Boolean),
    Column("blockedreason",                     String(255)),
    Column("document",                          String(20)),
    Column("documentid",                        String(20)),
    Column("maritalstatus",                     String(50)),
    Column("gender",                            String(20)),
    Column("birthdate",                         DateTime),
    Column("updatedate",                        DateTime),
    Column("state",                             String(50)),
    Column("city",                              String(100)),
    Column("zipcode",                           String(10)),
    Column("complement",                        String(255)),
    Column("number",                            String(20)),
    Column("country",                           String(100)),
    Column("totalfitcoins",                     Integer),
    Column("penalized",                         Boolean),
    Column("status",                            String(50)),
    Column("lastaccessdate",                    DateTime),
    Column("conversiondate",                    DateTime),
    Column("idemployeeconsultant",              Integer),
    Column("nameemployeeconsultant",            String(255)),
    Column("idemployeeinstructor",              Integer),
    Column("nameemployeeinstructor",            String(255)),
    Column("photourl",                          String(500)),
    Column("gympassid",                         String(100)),
    Column("personaltrainer",                   Boolean),
    Column("codetotalpass",                     String(100)),
    Column("clientwithpromotionalrestriction",  Boolean),
)

raw_sales = Table("sales", raw_meta,
    Column("idsale",            Integer,        primary_key=True),
    Column("idsaleitem",        Integer),
    Column("idmember",          Integer),
    Column("idemployeesale",    Integer),
    Column("nameemployeesale",  String(255)),
    Column("saledate",          DateTime),
    Column("updatedate",        DateTime),
    Column("idbranch",          Integer),
    Column("idmembership",      Integer),
    Column("idmembermembership",Integer),
    Column("item",              String(255)),
    Column("itemvalue",         Numeric(12, 2)),
    Column("salevalue",         Numeric(12, 2)),
    Column("salevaluewithoutcreditvalue", Numeric(12, 2)),
    Column("quantity",          Integer),
    Column("idmembershiprenewed",   Integer),
    Column("membershipstartdate",   DateTime),
    Column("valuenextmonth",        Numeric(12, 2)),
)

raw_debtors = Table("debtors", raw_meta,
    Column("receivableid",          Integer,    primary_key=True),
    Column("memberid",              Integer),
    Column("idmembermembership",    Integer),
    Column("receivableidorigin",    Integer),
    Column("branchid",              Integer),
    Column("idpaymenttype",         Integer),
    Column("memberstatus",          String(50)),
    Column("duedate",               Date),
    Column("paymentdate",           Date),
    Column("registerdate",          DateTime),
    Column("originalduedate",       Date),
    Column("chargedate",            Date),
    Column("dayslate",              Integer),
    Column("debtamount",            Numeric(10, 2)),
    Column("debtstatus",            String(50)),
    Column("paymentorigin",         String(100)),
    Column("chargeattemptscount",   Integer),
)


# ==============================================================================
#  SCHEMA RELATIONAL — modelo normalizado Galaxy Schema
#  Ordem de definição respeita dependências de FK
# ==============================================================================

# ── 1. Dimensões lookup (sem dependências) ─────────────────────────────────────

rel_dim_branch = Table("dim_branch", relational_meta,
    Column("branchid",   Integer,     primary_key=True),
    Column("branchname", String(255)),
)

rel_dim_employee = Table("dim_employee", relational_meta,
    Column("idemployee",   Integer,     primary_key=True),
    Column("nameemployee", String(255)),
)

rel_dim_planos = Table("dim_planos", relational_meta,
    Column("idmembership", Integer,     primary_key=True),
    Column("nome_plano",   String(255)),
)

rel_dim_payment_type = Table("dim_payment_type", relational_meta,
    Column("idpaymenttype", Integer,     primary_key=True),
    Column("paymenttype",   String(100)),
)

# ── 2. Dimensão principal ──────────────────────────────────────────────────────

rel_members = Table("members", relational_meta,
    Column("idmember",                          Integer,    primary_key=True),
    Column("firstname",                         String(255)),
    Column("lastname",                          String(255)),
    Column("registername",                      String(255)),
    Column("registerlastname",                  String(255)),
    Column("usepreferredname",                  Boolean),
    Column("idbranch",                          Integer,    ForeignKey("data_warehouse.dim_branch.branchid")),
    Column("accessblocked",                     Boolean),
    Column("blockedreason",                     String(255)),
    Column("document",                          String(20)),
    Column("documentid",                        String(20)),
    Column("maritalstatus",                     String(50)),
    Column("gender",                            String(20)),
    Column("birthdate",                         Date),
    Column("totalfitcoins",                     Integer),
    Column("penalized",                         Boolean),
    Column("status",                            String(50)),
    Column("idemployeeconsultant",              Integer,    ForeignKey("data_warehouse.dim_employee.idemployee")),
    Column("idemployeeinstructor",              Integer,    ForeignKey("data_warehouse.dim_employee.idemployee")),
    Column("photourl",                          String(500)),
    Column("personaltrainer",                   Boolean),
    Column("clientwithpromotionalrestriction",  Boolean),
    Column("phone_ddi",                         String(10)),
    Column("phone",                             String(50)),
    Column("email",                             String(255)),
    Column("registerdate",                      Date),
    Column("registertime",                      Time),
    Column("updatedate",                        Date),
    Column("updatetime",                        Time),
    Column("lastaccessdate",                    Date),
    Column("lastaccesstime",                    Time),
    Column("conversiondate",                    Date),
    Column("conversiontime",                    Time),
)

# ── 3. Dimensões satélite (dependem de members) ────────────────────────────────

rel_dim_address = Table("dim_address", relational_meta,
    Column("idaddress",  Integer,    primary_key=True, autoincrement=True),
    Column("idmember",   Integer,    ForeignKey("data_warehouse.members.idmember")),
    Column("state",      String(50)),
    Column("city",       String(100)),
    Column("zipcode",    String(10)),
    Column("complement", String(255)),
    Column("number",     String(20)),
    Column("country",    String(100)),
    UniqueConstraint("idmember", name="uq_address_member"),
)

rel_dim_partnerships = Table("dim_partnerships", relational_meta,
    Column("idpartnership", Integer,    primary_key=True, autoincrement=True),
    Column("idmember",      Integer,    ForeignKey("data_warehouse.members.idmember")),
    Column("plataforma",    String(50)),
    Column("codigo",        String(100)),
    UniqueConstraint("idmember", "plataforma", name="uq_partnerships"),
)

# ── 4. Tabelas fato ────────────────────────────────────────────────────────────

rel_sales = Table("sales", relational_meta,
    Column("idsale",                        Integer,        primary_key=True),
    Column("idsaleitem",                    Integer),
    Column("idmember",                      Integer,        ForeignKey("data_warehouse.members.idmember")),
    Column("idemployeesale",                Integer,        ForeignKey("data_warehouse.dim_employee.idemployee")),
    Column("idbranch",                      Integer,        ForeignKey("data_warehouse.dim_branch.branchid")),
    Column("idmembership",                  Integer,        ForeignKey("data_warehouse.dim_planos.idmembership")),
    Column("idmembermembership",            Integer),
    Column("salevalue",                     Numeric(12, 2)),
    Column("itemvalue",                     Numeric(12, 2)),
    Column("salevaluewithoutcreditvalue",   Numeric(12, 2)),
    Column("quantity",                      Integer),
    Column("idmembershiprenewed",           Integer),
    Column("membershipstartdate",           Date),
    Column("valuenextmonth",                Numeric(12, 2)),
    Column("saledate",                      Date),
    Column("saletime",                      Time),
    Column("updatedate",                    Date),
    Column("updatetime",                    Time),
)

rel_debtors = Table("debtors", relational_meta,
    Column("receivableid",          Integer,    primary_key=True),
    Column("memberid",              Integer,    ForeignKey("data_warehouse.members.idmember")),
    Column("idmembermembership",    Integer),
    Column("receivableidorigin",    Integer),
    Column("branchid",              Integer,    ForeignKey("data_warehouse.dim_branch.branchid")),
    Column("idpaymenttype",         Integer,    ForeignKey("data_warehouse.dim_payment_type.idpaymenttype")),
    Column("memberstatus",          String(50)),
    Column("duedate",               Date),
    Column("paymentdate",           Date),
    Column("originalduedate",       Date),
    Column("chargedate",            Date),
    Column("dayslate",              Integer),
    Column("debtamount",            Numeric(10, 2)),
    Column("debtstatus",            String(50)),
    Column("paymentorigin",         String(100)),
    Column("chargeattemptscount",   Integer),
    Column("registerdate",          Date),
    Column("registertime",          Time),
)


# ==============================================================================
#  Ordem de criação das tabelas no schema relational
#  (respeita dependências de FK)
# ==============================================================================

RELATIONAL_TABLE_ORDER = [
    rel_dim_branch,
    rel_dim_employee,
    rel_dim_planos,
    rel_dim_payment_type,
    rel_members,
    rel_dim_address,
    rel_dim_partnerships,
    rel_sales,
    rel_debtors,
]
