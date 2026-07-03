CREATE OR REPLACE VIEW data_warehouse.vw_debtors AS
SELECT
    d.receivableid,
    d.receivableidorigin,
    d.idmembermembership,
    d.memberid,
    m.firstname,
    m.lastname,
    d.memberstatus,
    d.branchid,
    b.branchname,
    d.idpaymenttype,
    pt.paymenttype,
    d.paymentorigin,
    d.debtamount,
    d.debtstatus,
    d.dayslate,
    d.chargeattemptscount,
    d.duedate,
    d.originalduedate,
    d.paymentdate,
    d.chargedate,
    d.registerdate,
    d.registertime
FROM data_warehouse.debtors d
LEFT JOIN data_warehouse.members          m  ON m.idmember       = d.memberid
LEFT JOIN data_warehouse.dim_branch       b  ON b.branchid       = d.branchid
LEFT JOIN data_warehouse.dim_payment_type pt ON pt.idpaymenttype = d.idpaymenttype;
