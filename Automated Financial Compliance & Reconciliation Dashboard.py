# reconciliation_pipeline.py
import pandas as pd
import numpy as np

# Config
AMOUNT_TOLERANCE_PCT = 0.5  # 0.5%
TAX_MISMATCH_THRESHOLD = 100.00
HIGH_VALUE_THRESHOLD = 100000.00

# Load (replace with DB reads)
ap = pd.read_csv("AP_Invoices.csv", parse_dates=["invoice_date"])
gl = pd.read_csv("GL_Postings.csv", parse_dates=["ledger_date"])
tax = pd.read_csv("Tax_Register.csv")

# Preprocess
ap['invoice_id'] = ap['invoice_id'].str.strip()
gl['ref_invoice_id'] = gl['ref_invoice_id'].fillna('').str.strip()
ap['invoice_amount'] = ap['invoice_amount'].astype(float)
gl['amount'] = (gl['debit'].fillna(0) - gl['credit'].fillna(0)).abs()

# 1) Exact match by invoice_id
exact = ap.merge(gl, left_on='invoice_id', right_on='ref_invoice_id', how='inner', suffixes=('_ap','_gl'))
exact['match_type'] = 'exact'
exact['match_score'] = 1.0

# 2) Amount tolerance match (AP invoice amount vs GL aggregated)
# aggregate GL by ref_invoice_id (non-empty) and try match by amount
gl_agg = gl[gl['ref_invoice_id']!=''].groupby('ref_invoice_id', as_index=False).agg({'amount':'sum','posting_id':'count'})
gl_agg.rename(columns={'ref_invoice_id':'invoice_id','amount':'gl_amount'}, inplace=True)
amount_match = ap.merge(gl_agg, on='invoice_id', how='inner')
amount_match['pct_diff'] = ((amount_match['invoice_amount'] - amount_match['gl_amount']).abs() / amount_match['invoice_amount'])*100
amount_match = amount_match[amount_match['pct_diff'] <= AMOUNT_TOLERANCE_PCT]
amount_match['match_type'] = 'amount_tolerance'
amount_match['match_score'] = 0.9

# 3) Fuzzy match on vendor + date +/- 7 days + amount diff small
ap_candidates = ap.copy()
gl_candidates = gl.copy()
# simplify: for demo, do join on vendor_id (if gl has vendor in description, otherwise skip),
# fallback: join by amount within tolerance and date window
ap_candidates['key_amount'] = ap_candidates['invoice_amount'].round(0)
gl_candidates['key_amount'] = gl_candidates['amount'].round(0)
fuzzy = ap_candidates.merge(gl_candidates, on='key_amount', suffixes=('_ap','_gl'))
fuzzy['date_diff'] = (fuzzy['ledger_date'] - fuzzy['invoice_date']).abs().dt.days
fuzzy = fuzzy[(fuzzy['date_diff'] <= 7) & (abs(fuzzy['invoice_amount'] - fuzzy['amount'])/fuzzy['invoice_amount']*100 <= 2.0)]
fuzzy['match_type'] = 'fuzzy'
fuzzy['match_score'] = 0.6

# Combine matches, avoid duplicates (invoice matched by best match_type priority)
combined = pd.concat([exact, amount_match, fuzzy], ignore_index=True, sort=False)
combined.sort_values(['invoice_id','match_score'], ascending=[True, False], inplace=True)
best_matches = combined.drop_duplicates(subset=['invoice_id'], keep='first').reset_index(drop=True)

# Build exceptions (AP invoices not in best_matches)
matched_invoice_ids = set(best_matches['invoice_id'])
exceptions = ap[~ap['invoice_id'].isin(matched_invoice_ids)].copy()
exceptions['issue'] = 'unmatched_invoice'

# Compliance checks
issues = []
# Tax mismatch
tax_join = ap.merge(tax, on='invoice_id', how='left')
tax_join['tax_diff'] = (tax_join['tax_amount'] - tax_join['computed_tax_amount']).abs()
tax_issues = tax_join[tax_join['tax_diff'] > TAX_MISMATCH_THRESHOLD]
for _, row in tax_issues.iterrows():
    issues.append({
        'invoice_id': row['invoice_id'],
        'issue_type': 'tax_mismatch',
        'severity': 'high' if row['tax_diff'] > 1000 else 'medium',
        'description': f"Tax recorded {row['tax_amount']} vs computed {row['computed_tax_amount']}"
    })
# Approval missing
ap_pr = ap[ (ap['invoice_amount'] > HIGH_VALUE_THRESHOLD) & (ap['approval_status'] != 'Approved') ]
for _, row in ap_pr.iterrows():
    issues.append({
        'invoice_id': row['invoice_id'],
        'issue_type': 'missing_approval',
        'severity': 'high',
        'description': f"High value invoice {row['invoice_amount']} missing approval"
    })

issues_df = pd.DataFrame(issues)

# Outputs
best_matches.to_csv('reconciled_results.csv', index=False)
exceptions.to_csv('exceptions.csv', index=False)
issues_df.to_csv('compliance_issues.csv', index=False)

print("Done. Files: reconciled_results.csv, exceptions.csv, compliance_issues.csv")
