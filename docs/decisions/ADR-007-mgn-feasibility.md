# Architecture Decision Record 007

## Title
Evaluation of AWS Application Migration Service (MGN) vs Automated Container Rebuilding

## Status
Accepted

## Context
Sabay Premium Bank operates an on premises core banking ledger running on a physical Linux server. As part of the cloud transformation roadmap, I evaluated server level rehosting using AWS Application Migration Service (AWS MGN) compared to my implemented strategy of automated container deployment via HashiCorp Terraform and Amazon Linux 2023.

## Decision Drivers
1. Operating System Hygiene: Avoid transferring legacy operating system clutter, outdated packages, and unpatched CVEs into AWS.
2. Infrastructure as Code Alignment: Maintain 100 percent of cloud infrastructure inside reviewable, version controlled Terraform code.
3. Attack Surface Reduction: Avoid replicating legacy SSH keys and configuration files.
4. Workstation Safety: Avoid installing block level kernel drivers on developer workstations.

## Evaluated Alternatives

### 1. Block Level Server Rehosting via AWS MGN
I evaluated AWS MGN. It provides continuous block level disk replication by installing an agent into the source Linux kernel. During cutover, it launches an exact clone of the source server on EC2. However, installing the agent on my workstation would have attempted to mirror my entire physical hard drive to AWS EBS volumes, costing substantial storage fees. Furthermore, block level cloning transfers legacy operating system technical debt directly into the cloud.

### 2. Automated Container Rebuilding on Amazon EC2
I selected automated container rebuilding. Because the core ledger application was already cleanly containerized and its relational state was isolated into PostgreSQL, moving the entire physical server disk was unnecessary. Container rebuilding provides immutability, cleaner security boundaries, and immediate alignment with our Kubernetes modernization roadmap.

## My Decision
I rejected block level server rehosting via AWS MGN in favor of automated container rebuilding on Amazon EC2 with Terraform.

I provisioned a clean minimal Amazon Linux 2023 instance using Terraform. I deployed the application container via AWS Systems Manager without open SSH ports, and replatformed persistence to Amazon RDS PostgreSQL.

## Consequences

### Positive
1. Zero legacy operating system technical debt transferred into AWS.
2. Complete infrastructure reproducibility declared in version controlled Terraform code.
3. Avoided continuous EBS staging volume costs and dedicated replication server overhead.
4. Clean progression toward microservices modernization on Kubernetes.

### Negative
1. Rebuilding requires maintaining application Dockerfiles and deployment automation scripts rather than performing automated disk imaging.