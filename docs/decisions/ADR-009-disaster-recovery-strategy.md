# Architecture Decision Record 009

## Title
Disaster Recovery Architecture: Cross Region Read Replica Feasibility and Policy Constraints

## Status
Accepted (Designed and Documented. Live deployment blocked by AWS Organization Service Control Policy)

## Context
Sabay Premium Bank requires a disaster recovery strategy to protect the core accounting ledger against regional cloud outages. Financial regulatory bodies mandate an audited Recovery Time Objective (RTO) under fifteen minutes and a Recovery Point Objective (RPO) under five seconds.

## Evaluated Alternatives
1. Backup and Restore: Backups are stored in S3 and restored into a secondary region after an outage occurs. Rejected because restoration takes hours, breaching RTO limits.
2. Pilot Light (Selected Design): An Amazon RDS Cross Region Read Replica runs continuously in a secondary region. Compute resources remain dormant as Terraform code templates until failover occurs.
3. Multi Region Active/Active: Full production clusters operate simultaneously across dual regions. Rejected because distributed relational transactions introduce severe write latency penalties.

## Organizational Policy Constraint
The AWS account assigned to this project operates inside an AWS Organization governed by Service Control Policy p-66jhqpow. This policy explicitly restricts API calls outside eu-north-1 (Stockholm). When the engineering team attempted to provision an RDS replica in eu-west-1 (Ireland), the AWS API returned AccessDenied with an explicit deny in the service control policy.

## Decision
We maintain the complete architectural specification and failover runbook for the Pilot Light strategy in docs/disaster-recovery-plan.md. We do not deploy live resources in eu-west-1 to comply with account guardrails. All live failover testing remains confined to Stockholm.

## Consequences
Positive:
1. Complete disaster recovery runbooks documented and audited.
2. Zero standing compute charges incurred in a secondary region.
3. Compliance with parent AWS Organization Service Control Policies.

Negative:
1. Live cross region failover drills cannot be executed until account administrators update policy p-66jhqpow to authorize eu-west-1.
