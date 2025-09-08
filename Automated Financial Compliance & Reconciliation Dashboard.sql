CREATE DATABASE Automated_Financial_Compliance_Reconciliation_Dashboard;
USE Automated_Financial_Compliance_Reconciliation_Dashboard;
 -- Table 1: AP Invoices
CREATE TABLE ap_invoices (
    invoice_id VARCHAR(20) PRIMARY KEY,
    vendor_id VARCHAR(20),
    invoice_date DATE,
    invoice_amount DECIMAL(12,2),
    tax_amount DECIMAL(12,2),
    currency VARCHAR(10),
    approval_status VARCHAR(20),
    supporting_doc_link VARCHAR(255)
);

-- Table 2: GL Postings
CREATE TABLE gl_postings (
    posting_id VARCHAR(20) PRIMARY KEY,
    ledger_date DATE,
    ref_invoice_id VARCHAR(20),
    account_code VARCHAR(20),
    debit DECIMAL(12,2),
    credit DECIMAL(12,2),
    description VARCHAR(255)
);

-- Table 3: Tax Register
CREATE TABLE tax_register (
    invoice_id VARCHAR(20),
    computed_tax_amount DECIMAL(12,2),
    tax_code VARCHAR(20),
    tax_rate DECIMAL(5,2),
    PRIMARY KEY (invoice_id)
);

LOAD DATA INFILE '/var/lib/mysql-files/AP_Invoices.csv'
INTO TABLE ap_invoices
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/GL_Postings.csv'
INTO TABLE gl_postings
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/Tax_Register.csv'
INTO TABLE tax_register
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

