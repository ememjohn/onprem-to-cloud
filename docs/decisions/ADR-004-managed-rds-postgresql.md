# Architecture Decision Record 004

## Title
Database Replatforming to Amazon RDS for PostgreSQL

## Status
Accepted

## Context
The source database runs PostgreSQL 16 on a self managed Linux host. The bank requires automated backups, zero data loss recovery capabilities, high availability storage, and routine security patching. The engineering team evaluated whether to self host PostgreSQL on an EC2 instance or replatform to Amazon RDS for PostgreSQL.

## Decision Drivers
1. Minimize Operational Overhead: Offload database engine patching, OS upgrades, and storage management to AWS.
2. Reliable Disaster Recovery: Enforce automated daily snapshots and point in time recovery without custom cron scripts.
3. Cloud Native Logical Replication: Support logical decoding parameters required for AWS Database Migration Service (AWS DMS) Change Data Capture.
4. Multi AZ High Availability Readiness: Enable one click standby replica provisioning across multiple availability zones.

## Evaluated Alternatives
1. Self Managed PostgreSQL on Amazon EC2: Rejected. Running database software directly on virtual machines requires manual operating system patching, custom backup rotation scripts, manual failover configurations, and high operational maintenance.
2. Amazon Aurora PostgreSQL: Evaluated as a high performance option but deferred to future scale. Aurora incurs higher baseline hourly compute charges than standard Amazon RDS.
3. Amazon RDS for PostgreSQL: Selected. RDS provides fully managed relational storage, automated point in time recovery, storage volume auto scaling, and native support for logical write ahead log replication.

## Consequences
Positive:
1. Automated daily snapshots and point in time recovery up to thirty five days.
2. Native parameter group management enabling logical replication for AWS DMS.
3. Predictable performance through encrypted gp3 storage volumes.
4. Clean separation of concerns between stateless compute and managed persistence.

Negative:
1. Slight loss of low level operating system shell access to the database host.
2. Running Amazon RDS instances incurs higher hourly compute costs than equivalent bare EC2 instances.
