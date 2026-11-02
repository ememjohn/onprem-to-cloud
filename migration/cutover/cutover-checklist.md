# Cutover Execution Checklist: Sabay Premium Bank Core Ledger

## 1. Operational Overview
This checklist governs the migration cutover of the Sabay Premium Bank core accounting ledger from the on premises source server to Amazon Web Services. The planned maintenance window spans thirty minutes.

## 2. Minute by Minute Cutover Timeline

### Stage 1: Preflight Verification (T minus 60 Minutes)
1. Verify source application health endpoint returns HTTP 200 on port 8000.
2. Execute automated preflight validation script: `./migration/cutover/preflight.sh`.
3. Confirm latest source backup snapshot exists in backups directory.
4. Verify AWS target infrastructure is online in eu-north-1 using Terraform.
5. Record baseline row counts on source: 3 customer accounts, 5 financial transactions.

### Stage 2: Source Quiescence and Read Only Freeze (T minus 15 Minutes)
1. Notify bank operations and payment network partners of the planned maintenance window.
2. Freeze application write operations on the source database to prevent in flight split brain transactions:
   `REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM app_user;`
3. Execute final pre cutover binary dump using `./scripts/backup_source_db.sh`.
4. Run `./migration/database/validate_data.py` to capture the final cryptographic checksum baseline.

### Stage 3: Target Database Synchronization (T Zero)
1. Transfer final differential snapshot to Amazon RDS using `./scripts/migrate_to_rds.py`.
2. Synchronize primary key sequences on Amazon RDS to the maximum existing record ID.
3. Grant read and write permissions to the application role on Amazon RDS.

### Stage 4: Ingress Traffic Switch (T plus 10 Minutes)
1. Update DNS routing records or load balancer ingress rules to point to the Application Load Balancer.
2. Verify public Application Load Balancer healthcheck returns HTTP 200 on path /healthz.

### Stage 5: Acceptance Validation (T plus 15 Minutes)
1. Execute automated acceptance suite: `./migration/validation/smoke_tests.sh`.
2. Verify customer account listings return HTTP 200.
3. Submit a test transaction to verify write path functionality.
4. If all tests pass, declare cutover complete and sign off the maintenance window.
