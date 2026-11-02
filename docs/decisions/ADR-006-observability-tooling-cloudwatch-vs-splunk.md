# Architecture Decision Record 006

## Title
Observability Architecture: Native Amazon CloudWatch Telemetry and SIEM Integration Pattern

## Status
Accepted

## Context
Sabay Premium Bank requires real time operational monitoring and security alerting across its migrated cloud infrastructure. The bank must detect service degradation, capture application runtime logs, and track database connection health. The engineering team evaluated whether to deploy a dedicated enterprise SIEM platform (such as Splunk Enterprise) directly inside the workload VPC or utilize native Amazon CloudWatch with external streaming.

## Decision Drivers
1. Low Latency Metric Evaluation: Detect and alert on Application Load Balancer 5XX errors and database drops within sixty seconds.
2. Zero Compute Overhead: Eliminate the need to provision dedicated heavy compute instances for observability collectors.
3. Cost Optimization: Avoid high proprietary licensing fees and instance memory costs during development and initial replatforming phases.
4. Compliance and Audit Streaming: Maintain standard mechanisms to export security audit trails to an enterprise Security Operations Center (SOC).

## Evaluated Alternatives
1. Dedicated In-VPC Splunk Cluster: Rejected for primary workload operations. Running a live Splunk indexer cluster requires heavy compute instances with at least sixteen gigabytes of memory, incurring hundreds of dollars in monthly cloud spending.
2. Self-Hosted Prometheus and Grafana on Workload EC2: Evaluated as a strong open source alternative but maintained as a separate standalone project (SignalOps) to preserve clear separation between infrastructure migration and telemetry engineering.
3. Native Amazon CloudWatch with SIEM Subscription Streaming: Selected. Amazon CloudWatch natively collects hypervisor metrics from Amazon RDS and the Application Load Balancer without custom exporter agents. For regulatory compliance, CloudWatch Subscription Filters stream audit logs to external platforms like Splunk via Amazon Kinesis Data Firehose.

## Consequences
Positive:
1. Native integration with AWS managed services (RDS, ALB, and EC2).
2. Serverless telemetry collection with zero RAM overhead on the application compute host.
3. Automated metric alarms evaluate conditions every sixty seconds without custom polling scripts.
4. Clean architectural separation between operational SRE alarms and security SIEM compliance.

Negative:
1. Custom dashboarding capabilities in CloudWatch are less flexible than Grafana or Splunk SPL queries.
2. High volume log retention beyond seven days incurs storage charges if retention policies are unmanaged.
