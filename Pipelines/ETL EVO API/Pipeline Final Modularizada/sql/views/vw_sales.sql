CREATE OR REPLACE VIEW data_warehouse.vw_sales AS
SELECT
    s.idsale,
    s.idsaleitem,
    s.idmembermembership,
    s.idmembershiprenewed,
    s.idmember,
    m.firstname,
    m.lastname,
    m.status        AS memberstatus,
    s.idbranch,
    b.branchname,
    s.salevalue,
    s.itemvalue,
    s.salevaluewithoutcreditvalue,
    s.quantity,
    s.valuenextmonth,
    s.membershipstartdate,
    s.saledate,
    s.saletime,
    s.updatedate,
    s.updatetime
FROM data_warehouse.sales s
LEFT JOIN data_warehouse.members    m ON m.idmember = s.idmember
LEFT JOIN data_warehouse.dim_branch b ON b.branchid = s.idbranch;
