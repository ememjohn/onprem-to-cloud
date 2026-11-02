# Rollback Operational Runbook: Sabay Premium Bank Core Ledger

## 1. Purpose and Scope
This runbook establishes standard operating procedures for aborting a cutover and restoring core banking ledger operations if critical failures occur during migration.

## 2. Rollback Decision Thresholds

### Threshold 1: Failure Prior to Target Writes (Clean Rollback)
Condition:
Failures occurring before DNS traffic switches or before the target Amazon RDS database accepts new transactions.
Rollback Complexity:
Low.
Action:
1. Leave DNS pointing to the on premises server.
2. Restore write permissions on the source PostgreSQL database:
   `GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;`
3. Verify application health on port 8000.
4. Resume normal business operations on premises. Zero data divergence exists.

### Threshold 2: Failure After Target Accepted Live Writes (Point of No Return)
Condition:
The Application Load Balancer accepted live incoming banking transactions on AWS before an unrecoverable failure was detected.
Rollback Complexity:
High (Data Reconciliation Required).
Risk:
Flipping DNS back to on premises immediately causes data divergence. Any transactions created on Amazon RDS during the cutover window will be lost on the source database.
Mandatory Procedure:
1. Freeze writes on Amazon RDS immediately by revoking table write permissions.
2. Identify all new transactions inserted into Amazon RDS during the cloud window (records with ID greater than the pre cutover baseline).
3. Export the newly created transaction records from Amazon RDS into an intermediate reconciliation SQL script.
4. Revert DNS traffic to the on premises server.
5. Restore write privileges on the on premises database.
6. Ingest the exported cloud transactions into the on premises database to ensure ledger balance parity.
7. Execute `./migration/database/validate_data.py` to mathematically verify ledger reconciliation.
