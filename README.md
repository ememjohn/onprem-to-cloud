# On Premises to Cloud: Enterprise Migration and Application Modernization

## Project Executive Summary
This repository contains the end to end engineering artifacts for migrating an on premises retail Order Management System (OMS) to Amazon Web Services. The project demonstrates a phased enterprise cloud transition: establishing a local source baseline, executing automated database replication with near zero downtime, replatforming compute to AWS, and modernizing the monolithic architecture into microservices on Kubernetes.

## Phase Delivery Roadmap
| Phase | Focus Area | Primary Engineering Deliverable | Current Status |
| :--- | :--- | :--- | :--- |
| Phase 1 | Source Baseline | Docker Compose environment, persistent volumes, backup verification | COMPLETED |
| Phase 2 | Migration Assessment | 6 Rs migration strategy, RTO RPO definitions, DMS analysis | IN PROGRESS |
| Phase 3 | AWS Infrastructure | Terraform VPC, private subnets, security groups, IAM policies | PENDING |
| Phase 4 | Target Deployment | EC2 application instance, Amazon RDS PostgreSQL cluster | PENDING |
| Phase 5 | Data Replication | AWS DMS full load plus Change Data Capture (CDC) replication | PENDING |
| Phase 6 | Cutover and Rollback | Traffic migration rehearsal, DNS cutover, rollback criteria | PENDING |
| Phase 7 | Cloud Observability | Amazon CloudWatch logs, error alarms, system metrics | PENDING |
| Phase 8 | Server Migration | AWS Application Migration Service (MGN) evaluation | PENDING |
| Phase 9 | App Modernization | Monolith decomposition, containerization, Amazon EKS deployment | PENDING |
| Phase 10 | Disaster Recovery | Multi Region cross replication, failover rehearsal, RTO validation | PENDING |

## Technology Matrix
| Technology Domain | Tool / Platform | Operational Purpose |
| :--- | :--- | :--- |
| Source Compute | Python 3.12, FastAPI, Uvicorn | Monolithic order intake and customer management service |
| Source Database | PostgreSQL 16 Alpine | Relational storage engine with WAL replication logging |
| Local Orchestration | Docker, Docker Compose | Isolated bridge network with named persistent volume storage |
| Infrastructure as Code | Terraform | Modular, reviewable AWS infrastructure provisioning |
| Target Cloud Compute | Amazon EC2, Amazon EKS | Initial rehosting target progressing to managed Kubernetes |
| Target Cloud Database | Amazon RDS for PostgreSQL | Managed relational database engine with automated snapshots |
| Data Migration Engine | AWS Database Migration Service (DMS) | Initial bulk data load followed by continuous logical CDC |
| Cloud Observability | Amazon CloudWatch | Centralized application log aggregation and availability alarms |

## Repository Architecture Navigation
1. System Architecture Specification: `docs/architecture/current-state.md`
2. Baseline Metrics and Test Evidence: `docs/baseline-metrics.md`
3. Incident Post Mortem Report: `docs/troubleshooting-log.md`
4. Operational Runbook: `docs/source-environment-runbook.md`
