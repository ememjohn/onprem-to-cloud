# Architecture Decision Record 004

## Title
Database Replatforming to Amazon RDS for PostgreSQL

## Status
Accepted

## Context
The source database ran PostgreSQL 16 on a self managed Linux host. The bank required automated backups, point in time recovery capabilities, high availability storage, and routine security patching. I had to evaluate whether to run self managed PostgreSQL on an EC2 instance or replatform to Amazon RDS for PostgreSQL.

## Decision Drivers
1. Minimize Operational Overhead: Offload database engine patching, OS maintenance, and storage provisioning to AWS.
2. Reliable Disaster Recovery: Enforce automated daily snapshots and point in time recovery up to thirty five days without custom shell scripts.
3. Storage Security: Guarantee data encryption at rest using AWS KMS managed keys.
4. Parameter Control: Maintain custom parameter groups to enforce transport encryption and replication logging.

## Evaluated Alternatives

### 1. Self Managed PostgreSQL on Amazon EC2
I rejected running database software directly on an EC2 instance. Self hosting requires manual operating system patching, custom backup rotation scripts, manual storage volume expansion, and complex custom failover setups.

### 2. Amazon Aurora PostgreSQL
I evaluated Amazon Aurora as a high performance option. I deferred Aurora to future scale because Aurora incurs higher baseline hourly compute charges than standard Amazon RDS during initial development and migration phases.

### 3. Amazon RDS for PostgreSQL
I selected Amazon RDS for PostgreSQL 16.10. RDS provides managed relational storage, automated point in time recovery, storage volume auto scaling, and native parameter group management.

## My Decision
I chose Amazon RDS for PostgreSQL 16.10. I allocated 20 GB of gp3 storage with AWS KMS encryption. I attached the instance to an isolated database subnet group spanning dual Availability Zones with zero internet routes. I configured the parameter group with rds.force_ssl = 1 to enforce transport layer encryption.

## Consequences

### Positive
1. Automated daily snapshots and point in time recovery up to thirty five days.
2. Storage encryption at rest managed natively through AWS KMS.
3. Clean separation of concerns between stateless compute and managed persistence.
4. Automated minor version engine patching managed during defined maintenance windows.

### Negative
1. Loss of operating system level shell access to the database host.
2. Running Amazon RDS instances incurs higher hourly compute costs than equivalent bare EC2 virtual machines.