#!/usr/bin/env bash
set -euo pipefail

echo "======================================================================"
echo "  SABAY PREMIUM BANK: CORE LEDGER SYSTEM: AUTOMATED CUTOVER PREFLIGHT VALIDATION"
echo "======================================================================"

EXIT_CODE=0

# Check 1: Source Application Health
echo -n "[*] Checking application healthz endpoint (http://localhost:8000/healthz)... "
if APP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/healthz 2>/dev/null) && [ "$APP_STATUS" -eq 200 ]; then
    echo "PASSED (HTTP 200)"
else
    echo "FAILED (Status: ${APP_STATUS:-Unreachable})"
    EXIT_CODE=1
fi

# Check 2: Database Connectivity
echo -n "[*] Checking database socket connectivity on port 5432... "
if docker exec oms_source_db pg_isready -U app_user -d orders_db >/dev/null 2>&1; then
    echo "PASSED (Accepting connections)"
else
    echo "FAILED (Database unavailable)"
    EXIT_CODE=1
fi

# Check 3: Sequence Synchronization Check
echo -n "[*] Validating primary key sequence alignment... "
SEQ_MISMATCH=$(docker exec oms_source_db psql -U app_user -d orders_db -t -c "
SELECT 
    CASE 
        WHEN (SELECT last_value FROM customers_id_seq) < (SELECT COALESCE(MAX(id), 1) FROM customers) THEN 1
        WHEN (SELECT last_value FROM orders_id_seq) < (SELECT COALESCE(MAX(id), 1) FROM orders) THEN 1
        ELSE 0
    END;
" | tr -d '[:space:]')

if [ "$SEQ_MISMATCH" -eq 0 ]; then
    echo "PASSED (Sequences aligned with MAX primary keys)"
else
    echo "FAILED (Sequence desynchronization detected)"
    EXIT_CODE=1
fi

# Check 4: Backup Verification Check
echo -n "[*] Verifying presence of recent database backup archive... "
if [ -d "backups" ] && [ "$(find backups -name '*.dump' -mmin -1440 | wc -l)" -gt 0 ]; then
    LATEST_DUMP=$(ls -t backups/*.dump | head -n 1)
    echo "PASSED (Recent snapshot: ${LATEST_DUMP})"
else
    echo "WARNING (No backup archive found from the last 24 hours)"
fi

echo "======================================================================"
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "[VERDICT] ALL MANDATORY PREFLIGHT GATES PASSED. READY FOR CUTOVER."
    exit 0
else
    echo "[VERDICT] PREFLIGHT CHECKS FAILED. CUTOVER ABORTED."
    exit 1
fi
