CREATE TABLE IF NOT EXISTS data_warehouse.debtors (
    receivableid            INTEGER         PRIMARY KEY,
    memberid                INTEGER,
    idmembermembership      INTEGER,
    receivableidorigin      INTEGER,
    branchid                INTEGER,
    idpaymenttype           INTEGER,
    memberstatus            VARCHAR(50),
    duedate                 DATE,
    paymentdate             DATE,
    registerdate            TIMESTAMP,
    originalduedate         DATE,
    chargedate              DATE,
    dayslate                INTEGER,
    debtamount              NUMERIC(10,2),
    debtstatus              VARCHAR(50),
    paymentorigin           VARCHAR(100),
    chargeattemptscount     INTEGER,

    CONSTRAINT fk_debtors_member        FOREIGN KEY (memberid)          REFERENCES data_warehouse.members(idmember),
    CONSTRAINT fk_debtors_branch        FOREIGN KEY (branchid)          REFERENCES data_warehouse.dim_branch(branchid),
    CONSTRAINT fk_debtors_paymenttype   FOREIGN KEY (idpaymenttype)     REFERENCES data_warehouse.dim_payment_type(idpaymenttype)
);
