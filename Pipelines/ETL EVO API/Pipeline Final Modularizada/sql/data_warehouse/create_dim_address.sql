CREATE TABLE IF NOT EXISTS data_warehouse.dim_address (
    idaddress       SERIAL          PRIMARY KEY,
    idmember        INTEGER,
    state           VARCHAR(50),
    city            VARCHAR(100),
    zipcode         VARCHAR(10),
    complement      VARCHAR(255),
    number          VARCHAR(20),
    country         VARCHAR(100),

    CONSTRAINT fk_address_member    FOREIGN KEY (idmember) REFERENCES data_warehouse.members(idmember),
    CONSTRAINT uq_address_member    UNIQUE (idmember)
);
