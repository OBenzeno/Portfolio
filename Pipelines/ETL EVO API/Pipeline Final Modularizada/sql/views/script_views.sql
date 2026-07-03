CREATE SCHEMA IF NOT EXISTS analytics;


/* 1. Membros ativos por filial */

CREATE OR REPLACE VIEW analytics.vw_membros_ativos AS
SELECT
    b.branchname                        AS filial,
    COUNT(m.idmember)                   AS total_membros,
    SUM(CASE WHEN m.accessblocked THEN 1 ELSE 0 END) AS bloqueados,
    SUM(CASE WHEN NOT m.accessblocked THEN 1 ELSE 0 END) AS ativos
FROM data_warehouse.members m
JOIN data_warehouse.dim_branch b ON m.idbranch = b.branchid
GROUP BY b.branchname;


/* 2. Receita mensal por filial */

CREATE OR REPLACE VIEW analytics.vw_receita_mensal AS
SELECT
    b.branchname                            AS filial,
    DATE_TRUNC('month', s.saledate)::DATE   AS mes,
    COUNT(s.idsale)                         AS total_vendas,
    SUM(s.salevalue)                        AS receita_total,
    ROUND(AVG(s.salevalue), 2)              AS ticket_medio
FROM data_warehouse.sales s
JOIN data_warehouse.dim_branch b ON s.idbranch = b.branchid
WHERE s.saledate IS NOT NULL
GROUP BY b.branchname, DATE_TRUNC('month', s.saledate)
ORDER BY mes DESC, filial;


/* 3. Inadimplentes com contato */

CREATE OR REPLACE VIEW analytics.vw_inadimplentes AS
SELECT
    m.idmember,
    COALESCE(m.firstname || ' ' || m.lastname, m.registername) AS nome,
    m.phone,
    m.email,
    b.branchname                AS filial,
    d.receivableid,
    d.debtamount                AS valor_divida,
    d.duedate                   AS vencimento,
    d.dayslate                  AS dias_atraso,
    d.debtstatus                AS status,
    pt.paymenttype              AS forma_pagamento
FROM data_warehouse.debtors d
JOIN data_warehouse.members m   ON d.memberid   = m.idmember
JOIN data_warehouse.dim_branch b ON d.branchid  = b.branchid
LEFT JOIN data_warehouse.dim_payment_type pt ON d.idpaymenttype = pt.idpaymenttype
WHERE d.debtstatus NOT IN ('Received', 'Cancelled')
ORDER BY d.dayslate DESC NULLS LAST;


/* 4. Novos membros por mês */

CREATE OR REPLACE VIEW analytics.vw_novos_membros AS
SELECT
    b.branchname                                AS filial,
    DATE_TRUNC('month', m.registerdate)::DATE   AS mes,
    COUNT(m.idmember)                           AS novos_membros
FROM data_warehouse.members m
JOIN data_warehouse.dim_branch b ON m.idbranch = b.branchid
WHERE m.registerdate IS NOT NULL
GROUP BY b.branchname, DATE_TRUNC('month', m.registerdate)
ORDER BY mes DESC, filial;


/* 5. Receita por plano */

CREATE OR REPLACE VIEW analytics.vw_receita_por_plano AS
SELECT
    p.nome_plano,
    b.branchname                            AS filial,
    DATE_TRUNC('month', s.saledate)::DATE   AS mes,
    COUNT(s.idsale)                         AS total_vendas,
    SUM(s.salevalue)                        AS receita_total,
    ROUND(AVG(s.salevalue), 2)              AS ticket_medio
FROM data_warehouse.sales s
JOIN data_warehouse.dim_planos p  ON s.idmembership = p.idmembership
JOIN data_warehouse.dim_branch b  ON s.idbranch     = b.branchid
WHERE s.saledate IS NOT NULL
GROUP BY p.nome_plano, b.branchname, DATE_TRUNC('month', s.saledate)
ORDER BY mes DESC, receita_total DESC;

/* 6. Churn — membros sem venda nos últimos 90 dias */

CREATE OR REPLACE VIEW analytics.vw_churn AS
SELECT
    m.idmember,
    COALESCE(m.firstname || ' ' || m.lastname, m.registername) AS nome,
    m.phone,
    m.email,
    b.branchname                AS filial,
    MAX(s.saledate)::DATE       AS ultima_venda,
    CURRENT_DATE - MAX(s.saledate)::DATE AS dias_sem_venda
FROM data_warehouse.members m
JOIN data_warehouse.dim_branch b ON m.idbranch = b.branchid
LEFT JOIN data_warehouse.sales s ON m.idmember = s.idmember
WHERE m.accessblocked = FALSE
GROUP BY m.idmember, m.firstname, m.lastname, m.registername, m.phone, m.email, b.branchname
HAVING MAX(s.saledate) < CURRENT_DATE - INTERVAL '90 days'
    OR MAX(s.saledate) IS NULL
ORDER BY dias_sem_venda DESC NULLS LAST;


/* 7. Performance de consultores (vendas) */

CREATE OR REPLACE VIEW analytics.vw_performance_consultores AS
SELECT
    e.nameemployee                          AS consultor,
    b.branchname                            AS filial,
    DATE_TRUNC('month', s.saledate)::DATE   AS mes,
    COUNT(s.idsale)                         AS total_vendas,
    SUM(s.salevalue)                        AS receita_gerada,
    ROUND(AVG(s.salevalue), 2)              AS ticket_medio
FROM data_warehouse.sales s
JOIN data_warehouse.dim_employee e  ON s.idemployeesale = e.idemployee
JOIN data_warehouse.dim_branch b    ON s.idbranch       = b.branchid
WHERE s.saledate IS NOT NULL
GROUP BY e.nameemployee, b.branchname, DATE_TRUNC('month', s.saledate)
ORDER BY mes DESC, receita_gerada DESC;