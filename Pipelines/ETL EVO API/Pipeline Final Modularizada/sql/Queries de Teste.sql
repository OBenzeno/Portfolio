/* SALES */
SELECT SUM(salevalue) as total_sales FROM data_warehouse.sales;

SELECT * FROM data_warehouse.sales
WHERE saledate = '2026-06-29'
ORDER BY saletime DESC;

SELECT * FROM data_warehouse.sales
WHERE idbranch = '60';

SELECT * FROM data_warehouse.sales
WHERE idmember = '1288143'
ORDER BY saledate DESC;

SELECT * FROM data_warehouse.debtors
WHERE memberid = '1288143'
ORDER BY registerdate DESC;


/* DEBTORS */
SELECT * FROM data_warehouse.debtors
ORDER BY duedate DESC;

SELECT * FROM data_warehouse.debtors
WHERE branchid = '60';

/* MEMBERS */
SELECT * FROM data_warehouse.members
WHERE registerdate = '2026-06-29'
ORDER BY registertime DESC;

SELECT * FROM data_warehouse.members
WHERE idbranch = '60';


SELECT * FROM data_warehouse.members
WHERE firstname IS NULL; AND lastname IS NULL;


SELECT COUNT(*) FROM data_warehouse.members
WHERE registerdate IS NULL;

SELECT * FROM data_warehouse.dim_partnerships
ORDER BY idpartnership DESC;
WHERE idpartnership = '5452';

SELECT * FROM data_warehouse.dim_branch;

