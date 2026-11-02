# Disaster Recovery Plan: Sabay Premium Bank Core Ledger

## 1. Executive Summary
This document defines the disaster recovery framework for Sabay Premium Bank. The plan establishes recovery metrics, architectural failover sequences, and post disaster data reconciliation when transferring primary operations from eu-north-1 (Stockholm) to a paired recovery region.

## 2. Recovery Objectives Matrix
| Recovery Metric | Regulatory Requirement | Target Architecture SLA | Validation Mechanism |
| :--- | :--- | :--- | :--- |
| Recovery Time Objective (RTO) | Maximum 30 Minutes | Under 15 Minutes | Automated RDS replica promotion and container launch |
| Recovery Point Objective (RPO) | Maximum 1 Minute | Under 5 Seconds | Asynchronous WAL streaming replication |
| Failover Threshold | 3 Consecutive Health Probe Failures | Evaluated within 60s | Route 53 automated health check polling |

## 3. Disaster Declaration and Failover Execution Sequence

### Phase 1: Outage Confirmation
1. SRE on call confirms primary region failure via Amazon CloudWatch composite alarms and AWS Health Dashboard.
2. Formally declare disaster state and initiate failover runbook.

### Phase 2: Database Failover (Promote Standby Replica)
Promote the cross region read replica to a standalone read write master database:
```bash
aws rds promote-read-replica \
  --db-instance-identifier "sabay-bank-dr-postgres" \
  --region secondary-region
```
Verify the promoted database status changes to available:
```bash
aws rds describe-db-instances \
  --db-instance-identifier "sabay-bank-dr-postgres" \
  --region secondary-region \
  --query "DBInstances[0].DBInstanceStatus"
```

### Phase 3: Compute Activation in Recovery Region
Deploy the application compute layer in the secondary region pointing to the promoted database:
```bash
cd terraform/environments/dr
terraform apply -auto-approve
```

### Phase 4: Ingress Traffic Switch
Update Amazon Route 53 DNS routing policy to shift public traffic to the recovery Application Load Balancer in the secondary region.

### Phase 5: Post Disaster Failback Procedure
Once the primary region (eu-north-1) stabilizes:
1. Quiesce write operations in the recovery region.
2. Establish reverse replication back to eu-north-1.
3. Validate row counts and SHA-256 checksums using migration/database/validate_data.py.
4. Shift traffic back to eu-north-1 and re-establish the pilot light replica.
