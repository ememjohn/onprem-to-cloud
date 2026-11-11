# Architecture Decision Record 009

## Title
Disaster Recovery Architecture: Cross Region Read Replica Feasibility and Policy Constraints

## Status
Accepted (Designed and Documented. Live deployment blocked by AWS Organization Service Control Policy)

## Context
Sabay Premium Bank required a disaster recovery strategy to protect operations against regional cloud outages. Financial regulatory bodies mandate an audited Recovery Time Objective (RTO) under fifteen minutes and a Recovery Point Objective (RPO) under five seconds.

## Decision Drivers
1. Strict Regulatory Compliance: The core ledger cannot tolerate multi hour service interruptions during a regional disaster.
2. Low Data Loss Tolerance: Maximum acceptable transaction data loss must remain under five seconds.
3. FinOps Cost Governance: Standby infrastructure costs must remain low during normal operations.
4. Organizational Policy Compliance: All cloud infrastructure must comply with parent AWS Organization security boundaries.

## Evaluated Alternatives

### 1. Backup and Restore
I evaluated backing up database snapshots to Amazon S3 and restoring into a secondary region after an outage occurs. I rejected this approach. Provisioning a fresh VPC, launching a new database instance, and restoring storage blocks takes several hours, violating the fifteen minute RTO mandate.

### 2. Pilot Light (Selected Design)
I selected a Pilot Light architecture pairing Stockholm (eu-north-1) with Ireland (eu-west-1). Core persistence mirrors continuously using an Amazon RDS Cross Region Read Replica. Compute resources remain dormant as Terraform code templates until failover occurs.

### 3. Multi Region Active/Active
I evaluated active clusters operating simultaneously across dual regions. I rejected this approach for relational ledger workloads. Distributed synchronous transactions introduce severe cross region network latency penalties on every write operation.

## Organizational Policy Constraint
The AWS account assigned to this project is governed by Service Control Policy p-66jhqpow, which restricts API calls outside eu-north-1. When I attempted to provision an RDS replica in eu-west-1, the AWS API returned AccessDenied with an explicit deny in the service control policy.

## My Decision
I selected the Pilot Light disaster recovery strategy. I documented the complete architectural specification and failover promotion runbook in docs/disaster-recovery-plan.md. 

I confined all live disaster simulation and rollback testing to Stockholm to comply with account guardrails. I did not deploy live resources in eu-west-1 to respect the AWS Organization Service Control Policy.

## Consequences

### Positive
1. Complete disaster recovery runbooks documented and audited against regulatory standards.
2. Zero standing compute charges incurred in a secondary region.
3. Compliance with parent AWS Organization Service Control Policies.
4. Fast promotion path: Amazon RDS read replica promotes to standalone write master in minutes during failover drills.

### Negative
1. Asynchronous replication introduces a small data loss exposure (seconds of lag) during sudden hard regional outages.
2. Live cross region failover drills cannot be executed until account administrators update policy p-66jhqpow to authorize eu-west-1.