CREATE OR REPLACE VIEW data_warehouse.vw_members AS
SELECT
    m.idmember,
    m.firstname,
    m.lastname,
    m.registername,
    m.registerlastname,
    m.usepreferredname,
    m.status,
    m.gender,
    m.birthdate,
    m.maritalstatus,
    m.document,
    m.documentid,
    m.phone_ddi,
    m.phone,
    m.email,
    m.accessblocked,
    m.blockedreason,
    m.penalized,
    m.personaltrainer,
    m.clientwithpromotionalrestriction,
    m.totalfitcoins,
    m.photourl,
    m.idbranch,
    b.branchname,
    m.idemployeeconsultant,
    ec.nameemployee AS nameconsultant,
    MAX(CASE WHEN p.plataforma = 'GYMPASS'   THEN p.codigo END) AS gympass_codigo,
    MAX(CASE WHEN p.plataforma = 'TOTALPASS' THEN p.codigo END) AS totalpass_codigo,
    a.state,
    a.city,
    a.zipcode,
    a.complement,
    a.number,
    a.country,
    m.registerdate,
    m.registertime,
    m.updatedate,
    m.updatetime,
    m.lastaccessdate,
    m.lastaccesstime,
    m.conversiondate,
    m.conversiontime
FROM data_warehouse.members m
LEFT JOIN data_warehouse.dim_branch       b  ON b.branchid    = m.idbranch
LEFT JOIN data_warehouse.dim_employee     ec ON ec.idemployee = m.idemployeeconsultant
LEFT JOIN data_warehouse.dim_partnerships p  ON p.idmember    = m.idmember
LEFT JOIN data_warehouse.dim_address      a  ON a.idmember    = m.idmember
GROUP BY
    m.idmember, m.idbranch, b.branchname, m.idemployeeconsultant, ec.nameemployee,
    a.state, a.city, a.zipcode, a.complement, a.number, a.country;
