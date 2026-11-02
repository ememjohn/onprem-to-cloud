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
| Phase 7 | Cloud Observability | Amazon CloudWatch logs, metric alarms, incident recovery runbooks | COMPLETED |
| Phase 8 | Server Migration | AWS Application Migration Service feasibility and rehosting assessment | COMPLETED |
| Phase 9 | App Modernization | Monolith decomposition, containerization, Amazon EKS deployment | COMPLETED |
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

## Architecture Decision Records (ADRs)
| ADR Identifier | Architectural Scope | Evaluated Tradeoffs | Selected Approach | Decision Record |
| :--- | :--- | :--- | :--- | :--- |
| **ADR 001** | Baseline Source Stack | FastAPI vs Django / SQLite vs PostgreSQL | FastAPI and PostgreSQL 16 on Docker Compose | [View Record](docs/decisions/ADR-001-source-environment-baseline.md) |
| **ADR 002** | Cloud Migration Strategy | Terraform vs CloudFormation / Rehost vs Replatform | Staged Replatforming managed via Terraform | [View Record](docs/decisions/ADR-002-migration-strategy.md) |
| **ADR 003** | Zero Open Port Administration | SSH Bastion Hosts vs AWS Systems Manager | Zero open port 22 via AWS SSM Session Manager | [View Record](docs/decisions/ADR-003-zero-open-ports-systems-manager.md) |
| **ADR 004** | Managed Persistence Replatforming | Self Managed EC2 PostgreSQL vs Amazon RDS | Managed Amazon RDS PostgreSQL with automated PITR | [View Record](docs/decisions/ADR-004-managed-rds-postgresql.md) |
| **ADR 005** | Database Replication Methodology | AWS DMS Full Load and CDC vs Native Snapshot Pipe | Cryptographic snapshot pipeline and sequence alignment | [View Record](docs/decisions/ADR-005-database-migration-strategy.md) |
| **ADR 006** | Observability Architecture | Native CloudWatch vs Standalone Splunk SIEM Cluster | Native CloudWatch Alarms with SIEM Firehose Streaming | [View Record](docs/decisions/ADR-006-observability-tooling-cloudwatch-vs-splunk.md) |
| **ADR 007** | Server Migration Methodology | AWS MGN Block Rehosting vs Automated Container Rebuild | Clean Container Rebuilding with Terraform | [View Record](docs/decisions/ADR-007-mgn-feasibility.md) |
| **ADR 008** | Modernization Architecture | Modular Monolith vs ECS Fargate vs Amazon EKS | Managed Kubernetes on Amazon EKS with HPA | [View Record](docs/decisions/ADR-008-modernization-eks-vs-modular-monolith.md) |

## Repository Technical Documentation Matrices

### System Blueprints and Cloud Architecture Specifications
| Specification Document | Engineering Domain | Architectural Deliverable | Direct Access |
| :--- | :--- | :--- | :--- |
| **Baseline Architecture Specification** | On Premises Source | Single host Linux Docker Compose topology and persistence model | [Open Specification](docs/architecture/current-state.md) |
| **Cloud Foundation Specification** | AWS Landing Zone | Multi tier VPC, dual AZ subnets, route tables, and security groups | [Open Specification](docs/architecture/cloud-foundation.md) |
| **Workload Migration Assessment** | Migration Planning | Stateless vs stateful decomposition, RTO and RPO targets | [Open Assessment](docs/migration-assessment.md) |
| **Modernized Architecture Specification** | Kubernetes Modernization | Amazon EKS cluster architecture, pod boundaries, HPA scaling | [Open Specification](docs/architecture/modernized-state.md) |
| **Security Architecture Review** | Compliance and Hardening | Zero open port 22 audit, private RDS isolation, secrets protection | [Open Audit](docs/security-review.md) |

### Operational Runbooks and Production Incident Analysis
| Operational Document | Operational Domain | Practical Value and Scope | Direct Access |
| :--- | :--- | :--- | :--- |
| **Engineering Incident Post Mortems** | SRE and Failure Analysis | Root cause analyses and exact code fixes for 7 production crashes | [Open Post Mortems](docs/troubleshooting-log.md) |
| **Cloud Operations Runbook** | Site Reliability Engineering | SOP for handling ALB 5XX alerts and database connection drops | [Open Runbook](docs/operations-runbook.md) |
| **Source Environment Runbook** | Operations SOP | Command reference for building, testing, backing up, and restoring | [Open Runbook](docs/source-environment-runbook.md) |
| **Project Delivery Status Tracker** | Governance and Milestones | Real time phase sign offs and completion evidence across all phases | [Open Status](docs/project-status.md) |

### Migration Execution Reports and Validation Evidence
| Migration Report | Verification Domain | Quantitative Evidence and Result | Direct Link |
| :--- | :--- | :--- | :--- |
| **Baseline Verification Metrics** | Source QA Testing | Automated test results and deterministic 3 customer / 5 transaction catalog | [Open Metrics](docs/baseline-metrics.md) |
| **Database Migration Report** | Persistence Migration | PostgreSQL 16.10 replatforming, SSL enforcement, sequence sync | [Open Report](docs/database-migration-report.md) |
| **Cutover and Rollback Execution Report** | Business Continuity | Maintenance window execution, traffic switch, and data reconciliation | [Open Report](docs/cutover-report.md) |
| **Server Migration Feasibility Assessment** | Rehosting Strategy | AWS MGN block level replication evaluation vs container rebuilding | [Open Assessment](docs/mgn-feasibility-assessment.md) |
