# Automated Financial Compliance & Reconciliation Dashboard

## 📖 Overview

This project automates financial reconciliation and compliance monitoring by combining Python, SQL, and Power BI into a unified solution. It enables finance teams to detect anomalies, track compliance risks, and visualize reconciliation coverage in real-time.

## The pipeline:
- Matches Accounts Payable (AP) invoices with General Ledger (GL) postings.
- Flags unmatched invoices, tax mismatches, and missing approvals.
- Stores results in MySQL and visualizes insights in Power BI dashboards.

## ⚙️ Tech Stack
- Python (Pandas, NumPy, SQLAlchemy) → Reconciliation, compliance checks, and data pipelines.
- MySQL (SQL queries) → Coverage metrics and compliance summaries.
- Power BI → Interactive dashboards for finance and audit teams.

## 🏗 Workflow
### 🔹 Step 1: Reconciliation (Python)
- Exact Match → AP invoice ID = GL reference invoice ID.
- Amount Tolerance Match → Matches within 0.5% tolerance.
- Fuzzy Match → Vendor, date window (±7 days), and small amount difference.
- Produces reconciled_results.csv + MySQL table.

### 🔹 Step 2: Exception Handling

- Identifies unmatched invoices (exceptions).
- Produces exceptions.csv + MySQL table.

### 🔹 Step 3: Compliance Checks

- Tax Mismatch → Compares recorded vs. computed tax.
- Missing Approval → Flags high-value invoices without approval.
- Produces compliance_issues.csv + MySQL table.

###🔹 Step 4: Analytics (SQL Queries)

- Reconciliation Coverage % by month.
- Compliance issues grouped by type.

###🔹 Step 5: Visualization (Power BI)

- Executive Summary → Reconciliation % trends, issue counts.
- Invoice Audit & Risk Insights → Exceptions by type/severity, compliance issue tables.

## 📊 Dashboard Previews
### 🔹 Executive Summary
![ Executive Summary] (visual/Executive summary (2).png)

### 🔹 Invoice Audit & Risk Insights
![Invoice Audit & Risk Insights]()

## How to Run

1. Download this project (or clone from GitHub).
2. Install the required Python packages:
pip install -r requirements.txt

3. Add your input files (AP_Invoices.csv, GL_Postings.csv, Tax_Register.csv) into the data folder.
4. Run the script:
python scripts/reconciliation_pipeline.py

5. Check the results:
CSV files (dataset) → reconciled_results.csv, exceptions.csv, compliance_issues.csv
MySQL tables → reconciled_results, exceptions, compliance_issues

6. Open the Power BI file (Financial_Audit.pbix) to see dashboards.
