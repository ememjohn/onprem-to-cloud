# Architecture Decision Record 005

## Title
Database Migration Methodology: AWS DMS Evaluation and Cryptographic Snapshot Pipeline

## Status
Accepted

## Context
Sabay Premium Bank operates an imaginary core banking ledger on PostgreSQL 16. The database holds corporate customer accounts, transaction logs, and sequence counters. I had to evaluate how to migrate this data to Amazon RDS for PostgreSQL with zero data loss and minimal cutover downtime.

## Decision Drivers
1. Zero Data Loss: Financial transaction integrity requires zero dropped records during data transfer.
2. Referential Integrity: Foreign key constraints and sequence counters must survive the migration.
3. Network Feasibility: The solution must account for local workstation network boundaries operating behind private routers without public static IP addresses.
4. Transport Encryption: Data in transit must negotiate TLS encryption during transfer.

## Evaluated Alternatives

### 1. AWS Database Migration Service (AWS DMS) with Change Data Capture (CDC)
I evaluated AWS DMS. In enterprise production environments with AWS Direct Connect or Site to Site VPN tunnels, AWS DMS provides continuous replication with sub second latency. However, for a local workstation operating behind a standard network router, the AWS DMS replication engine in Stockholm cannot initiate inbound connections to localhost port 5432 without exposing the machine to public internet risks.

### 2. Plain Text SQL Dump
I rejected plain text SQL exports. Plain SQL text files are uncompressed, slow to ingest over network pipes, and strip binary type metadata.

### 3. Compressed Custom Binary Snapshot Pipeline with Sequence Realignment
I selected a custom binary snapshot pipeline. Using PostgreSQL custom format archives (Fc) preserves relational types and table definitions in a compressed format. I coupled this with automated primary key sequence realignment and SHA-256 row level checksum validation.

## My Decision
I chose an automated binary snapshot pipeline with sequence realignment for development and staging, while documenting the AWS DMS Direct Connect architecture for enterprise production. 

I exported the source database using pg_dump custom binary format. I streamed the snapshot to Amazon RDS over an encrypted socket pipe using pg_restore with the no-owner flag. I executed setval automation immediately after restoration to synchronize primary key sequence counters.

## Consequences

### Positive
1. Schema and referential integrity preserved without third party network exposure.
2. Primary key sequence counters synchronized, preventing post cutover write collisions.
3. Automated SHA-256 row level hashing verified zero data corruption across tables.
4. Preserved cloud promotional credits by avoiding hourly DMS replication instance charges.

### Negative
1. Snapshot migrations require a scheduled maintenance window during cutover rather than continuous sub second CDC replication.
2. In flight writes must be frozen on the source database prior to the final snapshot export.