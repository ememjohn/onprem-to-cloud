# Architecture Decision Record 002

## Title
Cloud Migration Strategy, Tooling Selection, and Target Architecture Pattern

## Status
Accepted

## Context
Sabay Premium Bank required migration to Amazon Web Services to eliminate hardware failure risk and establish high availability. I had to select an infrastructure as code engine, a target compute strategy, and a database migration methodology that balanced operational risk and execution speed.

## Decision Drivers
1. Blast Radius Containment: Avoid compounding infrastructure migration risks with application refactoring risks simultaneously.
2. Business Continuity: The core transaction intake pipeline cannot tolerate multi hour maintenance windows.
3. Zero Data Loss: Financial transaction integrity requires zero dropped records during cutover.
4. Infrastructure Reproducibility: All cloud resources must be declared in version controlled code with reviewable dry run plans.

## Evaluated Decisions and Tradeoffs

### 1. Infrastructure as Code: HashiCorp Terraform vs AWS CloudFormation
I evaluated AWS CloudFormation and HashiCorp Terraform. I chose HashiCorp Terraform. Terraform provides clear dry run execution plans via terraform plan, modular reusability, and multi cloud industry adoption across platform engineering teams. CloudFormation relies on verbose JSON or YAML templates with less granular diff inspection.

### 2. Migration Approach: Staged Replatforming vs Immediate Microservices Rewrite
I evaluated rewriting the monolith directly into microservices versus staged replatforming. I chose Staged Replatforming. I rehosted compute on Amazon EC2 and replatformed persistence to Amazon RDS for PostgreSQL. This allowed me to separate infrastructure migration from application modernization. Decomposing the monolith into microservices occurs in Phase 9 only after baseline stability is proven in the cloud.

### 3. Database Migration Methodology: Snapshot Pipeline vs Offline Dumps
I evaluated offline text SQL exports versus an automated binary snapshot pipeline. I chose an automated binary snapshot pipeline with primary key sequence realignment. This preserves table structures, custom data types, and primary key counters while enforcing transport encryption.

## My Decision
I chose Staged Replatforming managed via HashiCorp Terraform. I provisioned compute on Amazon EC2 and persistence on Amazon RDS for PostgreSQL. I selected an automated binary snapshot pipeline with sequence realignment for development and staging, while documenting enterprise AWS DMS Direct Connect topologies for production.

## Consequences

### Positive
1. Zero direct internet exposure for application compute and database instances.
2. Complete infrastructure reproducibility declared in version controlled Terraform code.
3. Clean separation of concerns: database operations offloaded to AWS managed services.
4. Low migration risk by keeping application code stable during the cloud transition.

### Negative
1. Staged migration requires managing virtual machine compute before modernizing into containers.
2. Running dual environments during migration drills incurs temporary parallel operating costs.