from pathlib import Path

readme_path = Path("README.md")
content = readme_path.read_text(encoding="utf-8")

if "## Architecture Decision Records" in content:
    content = content.split("## Architecture Decision Records")[0]
elif "## Repository Documentation Index" in content:
    content = content.split("## Repository Documentation Index")[0]

advanced_matrices = """## Architecture Decision Records (ADRs)
| ADR Identifier | Architectural Scope | Evaluated Tradeoffs | Selected Approach | Decision Record |
| :--- | :--- | :--- | :--- | :--- |
| **ADR 001** | Baseline Source Stack | FastAPI vs Django / SQLite vs PostgreSQL | FastAPI and PostgreSQL 16 on Docker Compose | [View Record](docs/decisions/ADR-001-source-environment-baseline.md) |
| **ADR 002** | Cloud Migration Strategy | Terraform vs CloudFormation / Rehost vs Replatform | Staged Replatforming managed via Terraform | [View Record](docs/decisions/ADR-002-migration-strategy.md) |
| **ADR 003** | Zero Open Port Administration | SSH Bastion Hosts vs AWS Systems Manager | Zero open port 22 via AWS SSM Session Manager | [View Record](docs/decisions/ADR-003-zero-open-ports-systems-manager.md) |
| **ADR 004** | Managed Persistence Replatforming | Self Managed EC2 PostgreSQL vs Amazon RDS | Managed Amazon RDS PostgreSQL with automated PITR | [View Record](docs/decisions/ADR-004-managed-rds-postgresql.md) |
| **ADR 005** | Database Replication Methodology | AWS DMS Full Load and CDC vs Native Snapshot Pipe | Cryptographic snapshot pipeline and sequence alignment | [View Record](docs/decisions/ADR-005-database-migration-strategy.md) |

## Repository Technical Documentation Matrices

### System Blueprints and Cloud Architecture Specifications
| Specification Document | Engineering Domain | Architectural Deliverable | Direct Access |
| :--- | :--- | :--- | :--- |
| **Baseline Architecture Specification** | On Premises Source | Single host Linux Docker Compose topology and persistence model | [Open Specification](docs/architecture/current-state.md) |
| **Cloud Foundation Specification** | AWS Landing Zone | Multi tier VPC, dual AZ subnets, route tables, and security groups | [Open Specification](docs/architecture/cloud-foundation.md) |
| **Workload Migration Assessment** | Migration Planning | Stateless vs stateful decomposition, RTO and RPO targets | [Open Assessment](docs/migration-assessment.md) |
| **Security Architecture Review** | Compliance and Hardening | Zero open port 22 audit, private RDS isolation, secrets protection | [Open Audit](docs/security-review.md) |

### Operational Runbooks and Production Incident Analysis
| Operational Document | Operational Domain | Practical Value and Scope | Direct Access |
| :--- | :--- | :--- | :--- |
| **Engineering Incident Post Mortems** | SRE and Failure Analysis | Root cause analyses and exact code fixes for 7 production crashes | [Open Post Mortems](docs/troubleshooting-log.md) |
| **Source Environment Runbook** | Operations SOP | Command reference for building, testing, backing up, and restoring | [Open Runbook](docs/source-environment-runbook.md) |
| **Project Delivery Status Tracker** | Governance and Milestones | Real time phase sign offs and completion evidence across all phases | [Open Status](docs/project-status.md) |

### Migration Execution Reports and Validation Evidence
| Migration Report | Verification Domain | Quantitative Evidence and Result | Direct Link |
| :--- | :--- | :--- | :--- |
| **Baseline Verification Metrics** | Source QA Testing | Automated test results and deterministic 3 customer / 5 transaction catalog | [Open Metrics](docs/baseline-metrics.md) |
| **Database Migration Report** | Persistence Migration | PostgreSQL 16.10 replatforming, SSL enforcement, sequence sync | [Open Report](docs/database-migration-report.md) |
| **Cutover and Rollback Execution Report** | Business Continuity | Maintenance window execution, traffic switch, and data reconciliation | [Open Report](docs/cutover-report.md) |
"""

new_readme = content.strip() + "\n\n" + advanced_matrices
readme_path.write_text(new_readme, encoding="utf-8")
print("SUCCESS: README.md updated with executive technical documentation matrices.")
