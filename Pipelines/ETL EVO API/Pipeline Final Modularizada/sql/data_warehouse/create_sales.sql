CREATE TABLE IF NOT EXISTS data_warehouse.sales (
    idsale                          INTEGER         PRIMARY KEY,
    idsaleitem                      INTEGER,
    idmember                        INTEGER,
    idemployeesale                  INTEGER,
    idbranch                        INTEGER,
    idmembership                    INTEGER,
    idmembermembership              INTEGER,
    saledate                        TIMESTAMP,
    updatedate                      TIMESTAMP,
    salevalue                       NUMERIC(12,2),
    itemvalue                       NUMERIC(12,2),
    salevaluewithoutcreditvalue     NUMERIC(12,2),
    quantity                        INTEGER,
    idmembershiprenewed             INTEGER,
    membershipstartdate             TIMESTAMP,
    valuenextmonth                  NUMERIC(12,2),

    CONSTRAINT fk_sales_member      FOREIGN KEY (idmember)      REFERENCES data_warehouse.members(idmember),
    CONSTRAINT fk_sales_branch      FOREIGN KEY (idbranch)      REFERENCES data_warehouse.dim_branch(branchid),
    CONSTRAINT fk_sales_plano       FOREIGN KEY (idmembership)  REFERENCES data_warehouse.dim_planos(idmembership),
    CONSTRAINT fk_sales_employee    FOREIGN KEY (idemployeesale) REFERENCES data_warehouse.dim_employee(idemployee)
);
