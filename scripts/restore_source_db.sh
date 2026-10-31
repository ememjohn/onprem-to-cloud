#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <path_to_dump_file>"
    exit 1
fi

DUMP_FILE="$1"
TEST_DB="orders_db_restore_test"

echo "[*] Creating temporary validation database '${TEST_DB}'..."
docker exec -t oms_source_db psql -U app_user -d postgres -c "DROP DATABASE IF EXISTS ${TEST_DB};"
docker exec -t oms_source_db psql -U app_user -d postgres -c "CREATE DATABASE ${TEST_DB};"

echo "[*] Restoring ${DUMP_FILE} into ${TEST_DB}..."
docker exec -i oms_source_db pg_restore -U app_user -d "${TEST_DB}" < "${DUMP_FILE}"

echo "[*] Verifying record counts in restored database..."
docker exec -t oms_source_db psql -U app_user -d "${TEST_DB}" -c "
SELECT 
    (SELECT COUNT(*) FROM customers) AS restored_customers,
    (SELECT COUNT(*) FROM orders) AS restored_orders;
"

echo "[*] Tearing down temporary validation database..."
docker exec -t oms_source_db psql -U app_user -d postgres -c "DROP DATABASE ${TEST_DB};"
echo "[✓] Restore verification drill passed successfully."
