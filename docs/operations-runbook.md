# Operational Runbook: Incident Triage and Monitoring Procedures

## 1. System Observability Architecture
Sabay Premium Bank relies on Amazon CloudWatch for telemetry collection, metric evaluation, and incident alerting.

| Monitoring Subsystem | Evaluated Telemetry | Evaluation Interval | Alert Threshold |
| :--- | :--- | :--- | :--- |
| Application Ingress | Target 5XX HTTP Status Codes | 60 Seconds | Greater than or equal to 1 error |
| Relational Persistence | Active Database Connections | 60 Seconds | Less than 1 connection |
| Compute Application | Container Logs in /aws/ec2/sabay-bank-dev-core | Continuous Streaming | Unhandled application exceptions |

## 2. Standard Operating Procedures (SOP) for Alarms

### Alarm 1: sabay-bank-dev-high-5xx-errors
Symptom:
Application Load Balancer reports that the backend target returns HTTP 500 or 503 status codes.
Triage Sequence:
1. Check the target group health state:
   `aws elbv2 describe-target-health --target-group-arn <TARGET_GROUP_ARN> --region eu-north-1`
2. Connect to the EC2 host using AWS Systems Manager to inspect container logs:
   `docker logs sabay_app --tail 50`
3. Verify database socket reachability from the container to Amazon RDS on port 5432.
4. If the container crashed, restart the application service:
   `docker restart sabay_app`

### Alarm 2: sabay-bank-dev-rds-zero-connections
Symptom:
Active client connection count on Amazon RDS drops to zero.
Triage Sequence:
1. Verify whether the database is performing automated maintenance or failover:
   `aws rds describe-db-instances --db-instance-identifier sabay-bank-dev-postgres --region eu-north-1`
2. Verify that the EC2 application host is in the running state and healthy:
   `aws ec2 describe-instance-status --instance-ids <INSTANCE_ID> --region eu-north-1`
3. Verify that the application container is active and holding connection pool sockets:
   `docker exec sabay_app python3 -c "from src.database import engine; print(engine.pool.status())"`
