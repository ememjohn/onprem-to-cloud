# Operational Runbook: Source Environment Management

## Operational Command Reference
| Operational Task | Command Invocation | Expected Output |
| :--- | :--- | :--- |
| Build and Start Stack | docker compose -f source/compose.yaml up -d --build | Containers oms_source_db and oms_source_app Up |
| Query Service Status | docker compose -f source/compose.yaml ps | Both services show healthy or running state |
| Validate Health Probe | curl -s http://localhost:8000/healthz | HTTP 200 with status healthy and database connected |
| Execute Unit Tests | docker exec -t oms_source_app pytest /workspace/tests -v | All automated tests report PASSED |
| Create Binary Backup | ./scripts/backup_source_db.sh | New uncorrupted dump created in backups/ |
| Verify Database Restore | ./scripts/restore_source_db.sh <DUMP_PATH> | Test database restored, records validated, cleaned up |
| Stop Services (Retain Data) | docker compose -f source/compose.yaml down | Containers stopped, volume oms_source_pgdata preserved |
| Full Environment Teardown | docker compose -f source/compose.yaml down -v | Containers stopped, volume deleted (destructive) |
