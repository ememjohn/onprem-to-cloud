# Database Migration and Scale Benchmark Report

## 1. Executive Summary
This report documents the data migration and scale benchmarking for Sabay Premium Bank. The initiative migrated the core banking ledger from on premises PostgreSQL 16 to Amazon RDS for PostgreSQL 16.10 in Stockholm (eu-north-1). The validation proved relational schema preservation, transport encryption compliance, primary key sequence synchronization, and exact row parity across 100,000 synthetic banking records.

## 2. Scale Benchmark Execution Metrics
| Benchmark Metric | Source Environment | Target Amazon RDS | Audit Result |
| :--- | :--- | :--- | :--- |
| Database Engine Version | PostgreSQL 16.4 Alpine | PostgreSQL 16.10 Managed RDS | Compatible |
| Socket Transport Security | Local Bridge Network | TLS Encrypted (sslmode=verify-full) | Enforced |
| Corporate Account Records | 20,000 Rows | 20,000 Rows | Exact Match (0 Mismatches) |
| Transaction Ledger Records | 80,000 Rows | 80,000 Rows | Exact Match (0 Mismatches) |
| Total Relational Volume | 100,000 Rows | 100,000 Rows | Exact Match (0 Mismatches) |
| Data Classification | Labeled Synthetic Data | Labeled Synthetic Data | Verified Synthetic |
| Measured Migration Duration | Baseline Dump Stream | 42.18 Seconds | Verified |
| Sequence Alignment Check | customers_id_seq: 20000 | orders_id_seq: 80000 | Synchronized |

## 3. Measured Operational Durations
All durations represent real benchmarks recorded during live execution drills:
1. Source Write Freeze Window: Executed in under 1 second by revoking table write privileges from app_user.
2. Snapshot Staging Duration: Staged 4.5 MB compressed binary dump to temporary S3 bucket via presigned URL.
3. Database Ingestion Duration: Completed in 42.18 seconds via pg_restore with the no-owner flag over an encrypted socket.
4. Sequence Synchronization: Executed setval automation in under 2 seconds, preventing post cutover write collisions.
5. Emergency Rollback Duration: Reconciled post cutover transaction ID 80001 back into source database in under 2 seconds.

## 4. Verification Evidence
1. Output file `docs/evidence/2026-11-08-rds-scale-100k-counts.txt` confirms target row counts:
   `CUSTOMERS_COUNT: 20000`
   `ORDERS_COUNT: 80000`
2. Output file `docs/evidence/timings.md` logs exact UTC timestamps for freeze, migration, validation, and rollback.
3. Checksum verification engine confirmed zero discrepancies across both tables.