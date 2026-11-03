# Architecture Decision Record 009

## Title
Multi Region Disaster Recovery Strategy: Pilot Light with Amazon RDS Cross Region Replication

## Status
Accepted

## Context
Sabay Premium Bank requires a disaster recovery strategy to protect core banking operations against regional cloud outages. Financial regulatory bodies require an audited Recovery Time Objective (RTO) and Recovery Point Objective (RPO) ensuring business continuity in the event of a catastrophic failure in our primary AWS region (Primary Region (Stockholm) Stockholm).

## Evaluated Alternatives

### 1. Backup and Restore
Evaluation:
Backups are archived into Amazon S3 and restored into a secondary region only after a disaster occurs.
RTO: Several hours (rebuilding VPC, RDS instance, and restoring disk pages).
RPO: Several hours (data loss back to the last snapshot).
Verdict: Rejected. The bank cannot tolerate multi hour service interruptions or transaction loss.

### 2. Pilot Light (Selected Approach)
Evaluation:
Core persistence runs continuously in the secondary region (Secondary DR Region (Ireland) Ireland) using an asynchronous Amazon RDS Cross Region Read Replica. Compute infrastructure (Terraform modules and container images) is maintained as dormant code templates ready for immediate provisioning or low scale standby.
RTO: Under fifteen minutes (promoting replica to standalone write master and scaling compute).
RPO: Under five seconds (asynchronous WAL streaming lag).
Verdict: Selected. Balances strict financial availability requirements with sensible cloud cost governance.

### 3. Warm Standby
Evaluation:
A scaled down version of the full production environment runs continuously in the secondary region.
RTO: Under five minutes.
RPO: Under five seconds.
Verdict: Deferred to future scale. Running live idle compute clusters in dual regions doubles baseline operational expenditure.

### 4. Multi-Region Active/Active
Evaluation:
Full production clusters operate simultaneously across both regions handling live traffic.
RTO: Near zero.
RPO: Near zero.
Verdict: Rejected for relational ledger workloads. Enforcing cross region synchronous ACID distributed transactions introduces extreme latency penalties and complex write conflict resolution risks.

## Consequences
Positive:
1. Meets audited financial RTO under fifteen minutes and RPO under five seconds.
2. Low baseline standby cost: only the dormant cross region read replica incurs continuous runtime charges.
3. Declarative failover automation declared in Terraform and AWS CLI runbooks.
4. Clean promotion path: RDS read replica promotes to primary read write master in minutes.

Negative:
1. Asynchronous replication introduces a microscopic data loss exposure (seconds of lag) during sudden hard regional outages.
2. Cross region data transfer incurs minor network egress bandwidth charges.
