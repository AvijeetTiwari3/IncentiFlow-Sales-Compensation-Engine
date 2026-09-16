SELECT *
FROM {{ ref('audit_reconciliation_ledger') }}
WHERE reconciliation_status != 'BALANCED_ZERO_LEAKAGE'
