# Sabay Premium Bank: Core Banking Cloud Migration and Application Modernization

## Executive Summary
This document provides the definitive engineering retrospective for the migration and modernization of the core transaction ledger and customer accounting system at Sabay Premium Bank. The initiative migrated a mission critical financial workload from an on premises Linux server to Amazon Web Services, verified mathematical data integrity through SHA-256 checksums, established zero open port administrative security, rehearsed disaster recovery cutover and rollback scenarios, and modernized the monolith into scalable microservices on Kubernetes.

## 1. Business Context and Migration Drivers
Sabay Premium Bank operates as a regulated commercial financial institution. The core accounting ledger was previously hosted on a self managed on premises Linux server running Docker Compose and PostgreSQL 16.
Primary business drivers for cloud migration included:
1. High Availability and Disaster Recovery: Eliminating physical hardware single points of failure with multi availability zone automated failover.
2. Financial Data Integrity: Achieving Recovery Point Objective (RPO) under 5 seconds and Recovery Time Objective (RTO) under 15 minutes.
3. Operational Security: Eliminating public SSH port exposure in compliance with banking regulations.
4. Scalability for Settlement Spikes: Decoupling account lookups from high volume transaction settlement batches.

## 2. End to End Master Architecture-Workflow


## 3. Architecture Decision Records (ADRs) Summary Matrix
| Decision Record | Strategic Focus | Evaluated Options | Selected Engineering Approach |
| :--- | :--- | :--- | :--- |
| ADR 001 | Baseline Stack | FastAPI vs Django / SQLite vs PostgreSQL | FastAPI and PostgreSQL 16 on Docker Compose |
| ADR 002 | Migration Strategy | Terraform vs CloudFormation / Rehost vs Replatform | Staged Replatforming managed via Terraform |
| ADR 003 | Administrative Security | SSH Bastions vs AWS Systems Manager | Zero open port 22 via AWS SSM Session Manager |
| ADR 004 | Database Engine | Self Managed EC2 vs Amazon RDS | Managed Amazon RDS PostgreSQL with automated PITR |
| ADR 005 | Replication Method | AWS DMS Full Load & CDC vs Native Snapshot Pipe | Cryptographic snapshot pipeline and sequence alignment |
| ADR 006 | Cloud Observability | Native CloudWatch vs Standalone Splunk Cluster | Native CloudWatch Alarms with SIEM Firehose Streaming |
| ADR 007 | Server Migration | AWS MGN Block Rehosting vs Container Rebuild | Clean Container Rebuilding with Terraform |
| ADR 008 | Modernization | Modular Monolith vs ECS Fargate vs Amazon EKS | Managed Kubernetes on Amazon EKS with HPA |
| ADR 009 | Disaster Recovery | Backup/Restore vs Pilot Light vs Active/Active | Pilot Light with Amazon RDS Cross Region Read Replica |
| ADR 010 | Cutover Boundaries | Immediate DNS vs Pre-Cutover TTL Reduction | Route 53 Health Checks with Post Write Reconciliation |
| ADR 011 | Secrets Protection | Plaintext Files vs SSM Parameter Store vs Secrets Manager | AWS Secrets Manager with KMS Envelope Encryption |
| ADR 012 | FinOps Network Egress | Multi-AZ NAT Gateway vs Direct IGW Route | Direct IGW Egress with Strict Security Group Referencing |

## 4. Security, Compliance, and FinOps Retrospective
1. Zero Inbound Administrative Ports: TCP port 22 was eliminated. All shell executions operated through encrypted channels via AWS Systems Manager Session Manager.
2. Complete Database Network Isolation: Amazon RDS operates in isolated subnets with zero internet routes. Public network probes time out automatically at the security group perimeter.
3. Transport and Rest Encryption: Enforced TLS 1.3 encryption with sslmode=require for all application database connections and AWS KMS gp3 volume encryption.
4. Total Project Cloud Expenditure: By adhering to strict session teardown discipline via Terraform, all eleven phases were executed for less than 0.20 USD total cloud expenditure, preserving over 159.80 USD in promotional credits.

## 5. Engineering Incidents and Root Cause Analyses Summary
During execution, seven real world production engineering incidents were diagnosed and resolved:
1. Incident 1: FastAPI boot failure resolved by pinning email-validator in requirements.
2. Incident 2: Archive corruption resolved by stripping pseudo TTY minus t flags from binary pg_dump commands.
3. Incident 3: AWS Organizations region lock resolved by diagnosing and realigning infrastructure to Primary Region (Stockholm).
4. Incident 4: Interrupted provisioning crash resolved by state reconciliation via terraform import.
5. Incident 5: State import master password desync resolved using aws rds modify-db-instance with apply-immediately.
6. Incident 6: Transport encryption enforcement resolved by configuring sslmode=require on connection pools.
7. Incident 7: Database role ownership collisions resolved by using pg_restore minus minus no-owner and dynamic role creation.

## 6. Conclusion
The Sabay Premium Bank migration demonstrates that enterprise cloud transformations succeed when infrastructure is declared immutably as code, security boundaries are enforced by default, database migrations are mathematically validated, and application modernization is driven by measured business requirements.
