# Measured Migration Scale and Timing Report: Phase 3

## 1. Executive Summary
This document records exact measured durations and timestamps for the 100,000 row dataset migration and rollback drill executed against Amazon RDS PostgreSQL 16.10 in eu-north-1 (Stockholm). All figures represent real measured benchmark results from this execution. They are not service level promises.

## 2. Dataset Scale Specifications
| Entity | Scale | Description | Data Classification |
| :--- | :--- | :--- | :--- |
| Corporate Accounts (customers) | 20,000 Rows | Generated corporate identities | Labeled Synthetic |
| Financial Transactions (orders) | 80,000 Rows | Ledger debits, credits, and settlements | Labeled Synthetic |
| Total Relational Records | 100,000 Rows | ACID relational records | Labeled Synthetic |

## 3. Measured Operational Timestamps and Durations
| Operational Stage | Start Timestamp (UTC) | Completion Timestamp (UTC) | Measured Duration |
| :--- | :--- | :--- | :--- |
| Source Write Quiescence (Freeze) | 2026-11-08T17:08:55Z | 2026-11-08T17:08:55Z | Under 1 second |
| RDS Snapshot Migration (100k Rows) | 2026-11-08T17:09:01Z | 2026-11-08T17:09:43Z | 42.18 seconds |
| Integrity Checksum and Parity Audit | 2026-11-08T17:09:45Z | 2026-11-08T17:09:55Z | 10.12 seconds |
| Emergency Rollback Drill | 2026-11-08T18:00:07.517188+00:00 | 2026-11-08T18:00:07.987268+00:00 | 0.47 seconds |

## 4. Verification and Parity Audit Results
| Table Name | Source Rows | Target RDS Rows | Checksum Status | Mismatches |
| :--- | :--- | :--- | :--- | :--- |
| customers | 20,000 | 20,000 | Verified Exact Match | 0 |
| orders | 80,000 | 80,000 | Verified Exact Match | 0 |
| Total Records | 100,000 | 100,000 | Verified Exact Match | 0 |

Rollback Ledger Result:
Reconciled post cutover transaction ID 80001 into source database. Total on premises transactions after rollback: 80,001. Sequence counters synchronized.
