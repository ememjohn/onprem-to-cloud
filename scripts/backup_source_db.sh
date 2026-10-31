#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/orders_db_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

echo "[*] Exporting clean binary PostgreSQL backup from oms_source_db (no TTY)..."
docker exec oms_source_db pg_dump -U app_user -d orders_db -Fc > "${BACKUP_FILE}"

echo "[✓] Clean binary backup saved to: ${BACKUP_FILE}"
ls -lh "${BACKUP_FILE}"
