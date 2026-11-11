# Operational Runbook: Source Environment Management

## 1. Executive Summary
This runbook defines standard operating procedures for deploying, validating, backing up, and restoring the on premises core banking ledger for Sabay Premium Bank.

## 2. Operational Command Reference
| Operational Task | Command Invocation | Expected Output |
| :--- | :--- | :--- |
| Build and Start Stack | docker compose -f source/compose.yaml up -d --build | Containers bank_source_db and bank_source_app Up |
| Query Service Status | docker compose -f source/compose.yaml ps | Both services show healthy or running state |
| Validate Health Probe | curl -s http://localhost:8000/healthz | HTTP 200 with status healthy and database connected |
| Execute Unit Tests | docker exec -t bank_source_app pytest /workspace/tests -v | All automated tests report PASSED |
| Create Binary Backup | ./scripts/backup_source_db.sh | New uncorrupted dump created in backups/ |
| Verify Database Restore | ./scripts/restore_source_db.sh <DUMP_PATH> | Test database restored, records validated, cleaned up |
| Stop Services (Retain Data) | docker compose -f source/compose.yaml down | Containers stopped, volume bank_source_pgdata preserved |
| Full Environment Teardown | docker compose -f source/compose.yaml down -v | Containers stopped, volume deleted (destructive) |

## 3. Disaster Verification Drill
To verify point in time local recovery:
1. Trigger an uncorrupted compressed binary backup:
```bash
./scripts/backup_source_db.sh
```
2. Restore into a temporary test database and audit record counts:
```bash
LATEST_DUMP=$(ls -t backups/*.dump | head -n 1)
./scripts/restore_source_db.sh "${LATEST_DUMP}"
```