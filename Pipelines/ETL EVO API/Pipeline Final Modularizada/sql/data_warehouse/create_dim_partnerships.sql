CREATE TABLE IF NOT EXISTS data_warehouse.dim_partnerships (
    idmember        INTEGER,
    plataforma      VARCHAR(50),
    codigo          VARCHAR(100),

    CONSTRAINT pk_partnerships          PRIMARY KEY (idmember, plataforma),
    CONSTRAINT fk_partnerships_member   FOREIGN KEY (idmember) REFERENCES data_warehouse.members(idmember)
);
