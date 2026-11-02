# Sabay Premium Bank: Core Banking Cloud Migration and Application Modernization

## Executive Summary
This repository contains the production engineering artifacts for migrating the core transaction and account settlement ledger of Sabay Premium Bank from an on premises Linux environment to Amazon Web Services. The project establishes an enterprise migration model: verifying local persistence and disaster recovery baselines, replatforming compute and database engines to AWS with zero open administrative ports, executing automated continuous data replication, and modernizing the monolithic ledger into event driven microservices on Kubernetes.

## Phase Delivery Roadmap
| Phase | Focus Area | Primary Engineering Deliverable | Current Status |
| :--- | :--- | :--- | :--- |
| Phase 1 | Source Baseline | Docker Compose environment, persistent volumes, binary backup verification | COMPLETED |
| Phase 2 | Migration Assessment | Workload decomposition, RTO and RPO targets, target VPC design | COMPLETED |
| Phase 3 | AWS Infrastructure | Terraform multi tier VPC, private subnets, security groups, IAM roles | COMPLETED |
| Phase 4 | Target Deployment | EC2 compute, Amazon RDS PostgreSQL 16.10, ALB, network isolation | COMPLETED |
| Phase 5 | Data Replication | AWS DMS initial full load plus continuous Change Data Capture replication | COMPLETED |
| Phase 6 | Cutover and Rollback | Traffic migration rehearsal, health probing, rollback execution | COMPLETED |
| Phase 7 | Cloud Observability | Amazon CloudWatch logs, metric alarms, incident recovery runbooks | PENDING |
| Phase 8 | Server Migration | AWS Application Migration Service feasibility and rehosting assessment | PENDING |
| Phase 9 | App Modernization | Monolith decomposition, containerization, Amazon EKS deployment | PENDING |
| Phase 10 | Disaster Recovery | Multi Region cross replication, failover rehearsal, RTO validation | PENDING |
| Phase 11 | Portfolio Master Report | Comprehensive technical case study report and end to end topology | PENDING |

## Core Banking Technology Matrix
| Technology Domain | Tool / Platform | Operational Purpose |
| :--- | :--- | :--- |
| Source Compute Engine | Python 3.12, FastAPI, Uvicorn | Monolithic transaction intake and account ledger service |
| Source Persistence Engine | PostgreSQL 16 Alpine | ACID relational storage with logical write ahead logging |
| Local Orchestration | Docker, Docker Compose | Isolated bridge network with named persistent volume storage |
| Infrastructure as Code | HashiCorp Terraform | Modular, reviewable AWS infrastructure provisioning |
| Target Cloud Compute | Amazon EC2 on Amazon Linux 2023 | Initial rehost compute target managed via AWS Systems Manager |
| Target Cloud Database | Amazon RDS for PostgreSQL 16.10 | Managed multi AZ ready database with automated point in time recovery |
| Public Ingress Controller | Application Load Balancer (ALB) | Dual availability zone ingress with active health check routing |
| Secrets Protection | AWS Secrets Manager | Encrypted dynamic credential storage with zero plaintext commits |
| Data Migration Pipeline | AWS Database Migration Service (DMS) | Initial bulk data transfer followed by continuous logical CDC sync |
| Target Modernization Engine | Amazon EKS (Kubernetes) | Containerized microservices scaling ledger processing independently |

## Architecture Decision Records Catalog
1. ADR 001: Source Environment Architecture and Baseline Stack Selection (`docs/decisions/ADR-001-source-environment-baseline.md`)
2. ADR 002: Cloud Migration Strategy, Tooling Selection, and Target Architecture Pattern (`docs/decisions/ADR-002-migration-strategy.md`)
3. ADR 003: Zero Open Port Administration via AWS Systems Manager Session Manager (`docs/decisions/ADR-003-zero-open-ports-systems-manager.md`)
4. ADR 004: Database Replatforming to Amazon RDS for PostgreSQL (`docs/decisions/ADR-004-managed-rds-postgresql.md`)

## Security and Regulatory Compliance Posture
1. Zero Inbound Administrative Ports: The application host completely eliminates TCP port 22 exposure. Shell access operates exclusively across encrypted channels managed by AWS Systems Manager.
2. Database Tier Isolation: The primary PostgreSQL cluster resides in dedicated isolated subnets with zero internet gateway routes. External connection attempts time out automatically at the perimeter.
3. Cryptographic Data Protection: Storage volumes use AWS KMS managed gp3 encryption. Database credentials inject dynamically into runtime memory without touching disk configuration files.

## Repository Documentation Index
1. Baseline Architecture Specification: `docs/architecture/current-state.md`
2. Cloud Foundation Architecture Specification: `docs/architecture/cloud-foundation.md`
3. Workload Migration Assessment: `docs/migration-assessment.md`
4. Security Architecture Review: `docs/security-review.md`
5. Baseline Metrics and Verification Report: `docs/baseline-metrics.md`
6. Engineering Incident Post Mortem Report: `docs/troubleshooting-log.md`
7. Source Environment Operational Runbook: `docs/source-environment-runbook.md`
8. Database Migration and Parity Report: `docs/database-migration-report.md`
9. Cutover and Rollback Execution Report: `docs/cutover-report.md`
9. Project Phase Status Tracker: `docs/project-status.md`
