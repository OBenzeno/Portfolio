CREATE TABLE IF NOT EXISTS db_raw.debtors (
    receivableid                    INTEGER         PRIMARY KEY,
    memberid                        INTEGER,
    idmembermembership              INTEGER,
    receivableidorigin              INTEGER,
    branchid                        INTEGER,
    idpaymenttype                   INTEGER,
    memberstatus                    VARCHAR(50),
    duedate                         DATE,
    paymentdate                     DATE,
    registerdate                    TIMESTAMP,
    originalduedate                 DATE,
    chargedate                      DATE,
    dayslate                        INTEGER,
    debtamount                      NUMERIC(10,2),
    debtstatus                      VARCHAR(50),
    paymentorigin                   VARCHAR(100),
    chargeattemptscount             INTEGER
);
