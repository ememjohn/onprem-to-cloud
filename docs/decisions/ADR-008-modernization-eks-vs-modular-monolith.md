# Architecture Decision Record 008

## Title
Application Modernization Strategy: Monolith Decomposition and Amazon EKS Orchestration

## Status
Accepted

## Context
Sabay Premium Bank successfully migrated its monolithic core ledger to Amazon EC2 and Amazon RDS. The bank required independent scaling of transaction settlement during peak hours, continuous zero downtime deployments, and container orchestration. I evaluated remaining on a modular EC2 monolith, adopting AWS ECS on Fargate, or modernizing into microservices on Amazon EKS.

## Decision Drivers
1. Asymmetric Scaling: Transaction settlement experiences severe peak volume spikes, requiring rapid independent scaling. Customer account queries remain steady.
2. Fault Isolation: A surge in transaction processing must never starve memory or crash customer account lookup services.
3. Declarative Governance: Microservices must run with strict CPU and memory resource limits.
4. Cloud Native Portability: Manifests must adhere to standard open source Kubernetes specifications.

## Evaluated Alternatives

### 1. Maintain Modular Monolith on Amazon EC2
I evaluated keeping the application as a single container on an EC2 instance. It provides simple operations and low baseline cost. However, transaction settlement spikes consume host CPU and memory, degrading customer account query latency. Scaling requires scaling the entire virtual machine, resulting in inefficient resource allocation.

### 2. Serverless Containers on AWS ECS with Fargate
I evaluated AWS ECS with Fargate. It removes server management and scales containers automatically. However, it lacks open source cloud native ecosystem parity (such as Helm charts, Prometheus operators, and standard Kubernetes manifests) required for multi cloud banking portability.

### 3. Container Orchestration via Amazon EKS (Kubernetes)
I selected Amazon EKS. EKS provides standard Kubernetes APIs, declarative deployments, automated rolling updates, Horizontal Pod Autoscaling (HPA) based on CPU and memory thresholds, and granular namespace isolation.

## My Decision
I chose Amazon EKS (Kubernetes) for long term modernization. I decomposed the monolith into two microservices:
1. Account Service: Responsible for customer profiles, account verification, and KYC lookups on port 8001.
2. Settlement Service: Responsible for ledger transaction entries, credit and debit processing, and idempotent settlement on port 8002 with Horizontal Pod Autoscaling.

I authored the complete set of declarative Kubernetes manifests (Namespace, Deployments, ClusterIP Services, Ingress, and HPA) inside the kubernetes directory.

## Consequences

### Positive
1. Independent autoscaling of transaction settlement pods from 2 to 8 replicas without scaling account lookup services.
2. Declarative rolling updates with automated liveness and readiness probe health gating.
3. Industry standard Kubernetes manifests ready for GitOps deployment pipelines.
4. Granular resource limits (CPU and memory) preventing noisy neighbor starvation.

### Negative
1. Increased operational complexity managing Kubernetes manifests, service discovery, and ingress controllers.
2. Amazon EKS control plane incurs an hourly cluster management charge (approximately 73 USD monthly) compared to virtual machine compute.