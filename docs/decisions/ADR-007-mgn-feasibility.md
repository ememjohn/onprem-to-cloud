# Architecture Decision Record 007

## Title
Evaluation of AWS Application Migration Service (MGN) vs Automated Container Rebuilding

## Status
Accepted

## Context
Sabay Premium Bank operates an on premises core banking ledger running on a physical Linux server. As part of the cloud transformation roadmap, the engineering team evaluated server level rehosting using AWS Application Migration Service (AWS MGN) compared to our implemented strategy of automated container deployment via HashiCorp Terraform and Amazon Linux 2023.

## Evaluation of AWS Application Migration Service (MGN)

### 1. Architectural Mechanism
AWS MGN provides non disruptive continuous block level replication:
1. An AWS Replication Agent installs directly into the source Linux kernel.
2. The agent intercepts storage I/O at the block layer and streams compressed disk blocks across outbound TCP port 1500 to a dedicated staging VPC area.
3. A lightweight replication instance attaches staging EBS volumes matching each source disk partition.
4. During cutover, AWS MGN creates point in time EBS snapshots and automatically launches the target Amazon EC2 instance with AWS driver injection.

### 2. When AWS MGN is the Optimal Enterprise Choice
1. Legacy Monoliths with Complex Dependencies: Systems with undocumented OS configurations, proprietary binary dependencies, or specialized middleware where rebuilding from code is high risk.
2. Large Scale Datacenter Evacuation: Enterprise migrations moving hundreds or thousands of legacy virtual machines simultaneously under tight datacenter lease exit deadlines.
3. Stateful Compute Servers: Legacy servers where application compute and file system storage cannot be decoupled.

### 3. Tradeoff Comparison Matrix
| Architectural Dimension | Block Level Rehosting (AWS MGN) | Automated Container Rebuilding (Selected) |
| :--- | :--- | :--- |
| OS Hygiene and Security | Replicates legacy operating system bloat, obsolete packages, and unpatched CVEs | Clean minimal Amazon Linux 2023 baseline with zero legacy clutter |
| Infrastructure as Code Alignment | Creates opaque unmanaged EC2 disk clones outside Terraform state | 100 percent declared, reviewable, reproducible Terraform modules |
| Administrative Surface | Replicates legacy SSH keys and configuration files | Zero open SSH ports, managed exclusively via AWS Systems Manager |
| Modernization Readiness | Leaves workload coupled to traditional virtual machine constructs | Prepares services for immediate microservices containerization on EKS |
| Continuous Staging Cost | Requires persistent replication servers and EBS staging volumes | Zero standing replication storage costs |

## Decision
For Sabay Premium Bank, we reject block level server rehosting via AWS MGN in favor of automated container rebuilding on Amazon EC2 with Terraform.

Because the core ledger application is already cleanly containerized and its relational state is isolated into PostgreSQL, moving the entire physical server disk introduces unnecessary operational risk, storage expenses, and legacy technical debt. Container rebuilding provides immutability, cleaner security boundaries, and immediate alignment with our Phase 9 modernization path on Amazon EKS.

## Consequences
Positive:
1. Zero legacy operating system technical debt transferred into AWS.
2. Complete infrastructure reproducibility declared in version controlled Terraform code.
3. Avoided continuous EBS staging volume costs and dedicated replication server overhead.
4. Seamless progression toward microservices modernization on Kubernetes.

Negative:
1. Rebuilding requires maintaining application Dockerfiles and deployment automation scripts rather than performing automated disk imaging.
