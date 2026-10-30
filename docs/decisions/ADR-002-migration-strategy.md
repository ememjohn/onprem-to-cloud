# Architecture Decision Record 002

## Title
Cloud Migration Strategy, Tooling Selection, and Target Architecture Pattern

## Status
Accepted

## Context
Apex Retail Services operates an internal Order Management System running on a single on premises Linux server. The business requires migration to Amazon Web Services to achieve high availability, eliminate hardware failure risk, automate database management, and establish a foundation for microservices modernization. The engineering team must select an infrastructure as code engine, a target compute strategy, and a database migration methodology that balance operational risk, business continuity, and execution speed.

## Decision Drivers
1. Minimize Business Downtime: The order intake pipeline cannot tolerate multi hour maintenance windows.
2. Zero Data Loss: Financial transaction integrity requires zero dropped records during cutover.
3. Industry Standard Infrastructure Management: Tooling must support modular reproducibility, state locking, and multi environment parity.
4. Blast Radius Containment: Avoid compounding application refactoring risks with cloud infrastructure migration risks simultaneously.

## Evaluated Decisions and Tradeoffs

### 1. Infrastructure as Code: HashiCorp Terraform vs AWS CloudFormation
| Evaluation Criteria | HashiCorp Terraform | AWS CloudFormation | Selected Approach |
| :--- | :--- | :--- | :--- |
| Ecosystem Scope | Multi cloud and SaaS provider ecosystem | AWS native ecosystem only | Terraform |
| Language Ergonomics | HashiCorp Configuration Language (HCL) | Verbose JSON or YAML templates | Terraform |
| Plan Inspection | Strict terraform plan preview before execution | Change sets with less granular diff visibility | Terraform |
| State Management | Remote state backend in S3 with DynamoDB lock | Internal AWS managed state engine | Terraform |
| Industry Adoption | Standard across top tier enterprise DevOps teams | Common in AWS exclusive legacy shops | Terraform |

Decision: Selected HashiCorp Terraform. Terraform provides superior modular reusability, clear dry run plan reviews, and industry standard adoption across enterprise platform engineering teams.

### 2. Workload Migration Approach: Staged Replatform vs Immediate Rewrite
| Migration Strategy | Technical Mechanism | Risk Profile | Downtime Impact | Selected Approach |
| :--- | :--- | :--- | :--- | :--- |
| Rehost (Lift and Shift) | Move virtual machine image directly | Low | Medium | Hybrid Foundation |
| Replatform (Lift, Tinker, Shift) | Move compute to EC2, database to RDS | Low to Medium | Low (Near Zero) | SELECTED |
| Refactor / Rearchitect | Decompose monolith into microservices directly | High | High | Deferred to Phase 9 |

Decision: Selected Staged Replatforming. We rehost compute on Amazon EC2 and replatform the database to Amazon RDS for PostgreSQL. This separates infrastructure migration from application modernization. Decomposing the monolith into microservices on Amazon EKS occurs in Phase 9 only after operational baseline stability is proven on AWS.

### 3. Database Migration Methodology: AWS DMS with CDC vs Offline Dump and Restore
| Migration Mechanism | Data Transfer Path | Cutover Window Downtime | Ongoing Sync Capability | Selected Approach |
| :--- | :--- | :--- | :--- | :--- |
| Native pg_dump / pg_restore | Bulk file export over network | High (Full maintenance window required) | None (Source must be frozen) | Fallback / Seeding |
| AWS Database Migration Service | Continuous logical replication via CDC | Low (Minutes for DNS switch) | Continuous write ahead log capture | SELECTED |

Decision: Selected AWS Database Migration Service (AWS DMS) utilizing full load plus Change Data Capture (CDC). DMS replicates initial data blocks and streams ongoing transactional changes from PostgreSQL write ahead logs directly into Amazon RDS. This reduces business downtime to the duration of the final DNS cutover.

### 4. Target Ingress and Compute Architecture
| Infrastructure Component | Selected AWS Service | Architectural Justification |
| :--- | :--- | :--- |
| Network Perimeter | Application Load Balancer (ALB) | Dual availability zone ingress, TLS termination, health check probing |
| Application Compute | Amazon EC2 in Private Subnet | Direct runtime parity with source, zero direct internet exposure |
| Database Target | Amazon RDS for PostgreSQL | Automated point in time recovery, automated patching, multi AZ standby ready |
| Host Administration | AWS Systems Manager Session Manager | Eliminates SSH port 22 exposure and avoids static bastion hosts |

## Consequences
Positive:
1. Zero direct internet exposure for application compute and database instances.
2. Near zero downtime migration path through continuous database CDC replication.
3. Modular, reviewable infrastructure managed through version controlled Terraform code.
4. Clean separation of concerns: database operations offloaded to AWS managed services.

Negative:
1. Running dual environments during CDC replication incurs temporary parallel operating costs.
2. AWS DMS requires PostgreSQL source configuration changes to enable logical replication logging.
