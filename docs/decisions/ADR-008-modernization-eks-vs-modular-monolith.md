# Architecture Decision Record 008

## Title
Application Modernization Strategy: Monolith Decomposition and Amazon EKS Orchestration

## Status
Accepted

## Context
Sabay Premium Bank successfully migrated its monolithic core ledger to Amazon EC2 and Amazon RDS. The business requires independent scaling of transaction settlement during peak hours, continuous zero downtime deployments, and container orchestration. The engineering team evaluated remaining on a modular EC2 monolith, adopting AWS ECS on Fargate, or modernizing into microservices on Amazon EKS.

## Evaluated Alternatives

### 1. Maintain Modular Monolith on Amazon EC2
Evaluation:
Running a single container on an EC2 instance provides simple operations and low baseline cost. However, transaction processing spikes consume host CPU and memory, degrading customer account query latency. Scaling requires scaling the entire virtual machine, resulting in inefficient resource allocation.

### 2. Serverless Containers on AWS ECS with AWS Fargate
Evaluation:
AWS ECS with Fargate removes server management, scales containers automatically, and integrates with Application Load Balancers. However, it lacks open source cloud native ecosystem parity (such as Helm charts, Prometheus operators, and standard Kubernetes manifests) required for multi cloud banking portability.

### 3. Container Orchestration via Amazon EKS (Kubernetes)
Evaluation: Selected for long term enterprise modernization.
Amazon EKS provides standard Kubernetes APIs, declarative deployments, automated rolling updates, Horizontal Pod Autoscaling (HPA) based on CPU and memory thresholds, and granular namespace isolation.

## Microservice Decomposition Boundaries
We extract two domain services:
1. Account Service: Responsible for corporate customer profiles, account verification, and read operations.
2. Settlement Service: Responsible for ledger transaction entries, credit and debit processing, and idempotent settlement execution.

## Data Ownership Pattern: Transitional Shared Relational Storage
In true microservices, each service owns an isolated database. During this initial modernization phase, both services connect to Amazon RDS for PostgreSQL using dedicated connection credentials and distinct table ownership. This avoids introducing distributed transactions or eventual consistency lag into the banking ledger while achieving compute decoupling.

## Consequences
Positive:
1. Independent autoscaling of transaction processing without scaling account lookup services.
2. Declarative rolling updates with automated liveness and readiness probe health gating.
3. Industry standard Kubernetes manifests ready for GitOps deployment pipelines.
4. Granular resource limits (CPU and memory) preventing noisy neighbor starvation.

Negative:
1. Increased operational complexity managing Kubernetes manifests, service discovery, and ingress controllers.
2. Amazon EKS control plane incurs an hourly cluster management charge (approximately 73 USD monthly) compared to serverless container alternatives.
