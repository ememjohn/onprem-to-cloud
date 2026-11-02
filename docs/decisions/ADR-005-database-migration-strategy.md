# Architecture Decision Record 005

## Title
Database Migration Methodology: AWS DMS Evaluation and Native Seeding Pipeline

## Status
Accepted

## Context
Sabay Premium Bank requires migrating its active PostgreSQL 16 core banking ledger to Amazon RDS for PostgreSQL. The database holds customer account profiles, transaction logs, and primary key sequence counters. The engineering team evaluated AWS Database Migration Service (AWS DMS) versus a direct cryptographic logical snapshot pipeline.

## Evaluation of AWS Database Migration Service (DMS)

### 1. Technical Capabilities
AWS DMS provides two continuous data movement modes:
1. Full Load: Extracts existing database tables into internal memory buffers and writes them in parallel into target tables.
2. Change Data Capture (CDC): Reads the source PostgreSQL Write Ahead Logs (WAL) via logical replication slots, capturing transactions occurring during the migration window and applying them to the target RDS database with sub second latency.

### 2. Network Prerequisites and Enterprise Boundary
AWS DMS replication instances reside inside the target AWS Virtual Private Cloud. In production enterprise banking, network engineers connect on premises datacenters to the VPC using AWS Direct Connect or an IPsec Site to Site VPN. 
In local development environments operating behind Network Address Translation (NAT) routers without public static IP addresses, the DMS replication engine in AWS cannot initiate inbound TCP handshakes to localhost port 5432 without exposing local workstations to public internet risks.

## Decision
1. In Enterprise Production: Sabay Premium Bank selects AWS DMS utilizing Full Load plus CDC across dedicated AWS Direct Connect circuits to minimize cutover downtime.
2. In Development and Staging: We implement a cryptographically verified logical migration pipeline. We extract schema and transactional records using PostgreSQL custom format archives (-Fc), stream them to Amazon RDS, realign sequences, and validate parity using SHA-256 row level checksums.

## Consequences
Positive:
1. Complete schema and referential integrity preserved without third party network exposure.
2. Sequence synchronization executed directly after initial data load.
3. Automated SHA-256 row level hashing mathematically proves zero data corruption.
4. Preserves AWS promotional budget by avoiding idle DMS replication instance hourly costs.

Negative:
1. Logical snapshot migrations require a scheduled maintenance window during cutover rather than continuous sub second CDC synchronization.
