# Architecture Decision Record 006

## Title
Observability Architecture: Native Amazon CloudWatch Telemetry and SIEM Integration

## Status
Accepted

## Context
Sabay Premium Bank requires real time operational monitoring and security alerting across its migrated cloud infrastructure. The bank must detect service degradation, capture application runtime logs, and track database connection health. I evaluated whether to deploy an in VPC Splunk cluster versus utilizing native Amazon CloudWatch.

## Decision Drivers
1. Sub Minute Metric Evaluation: Detect and alert on Application Load Balancer 5XX errors and database drops within sixty seconds.
2. Zero Compute RAM Overhead: Eliminate the need to provision dedicated heavy compute instances for observability collectors.
3. FinOps Cost Governance: Avoid high proprietary licensing fees and instance memory costs during development phases.
4. Compliance and Audit Streaming: Maintain standard mechanisms to export security audit trails to an external Security Operations Center.

## Evaluated Alternatives

### 1. Dedicated In-VPC Splunk Enterprise Cluster
I rejected running a dedicated Splunk cluster inside the workload VPC. Splunk requires heavy compute instances with at least sixteen gigabytes of memory, incurring substantial monthly cloud spending that would quickly deplete promotional credits.

### 2. Self Hosted Prometheus and Grafana on Workload EC2
I evaluated this open source stack. I maintain this toolset as a separate standalone project (SignalOps) to preserve a clear portfolio boundary between infrastructure migration and custom telemetry engineering.

### 3. Native Amazon CloudWatch with SIEM Subscription Streaming
I selected Amazon CloudWatch. CloudWatch natively captures hypervisor metrics from Amazon RDS and the Application Load Balancer without custom exporter agents. For regulatory compliance, CloudWatch Subscription Filters stream audit logs to external platforms like Splunk via Amazon Kinesis Data Firehose.

## My Decision
I chose native Amazon CloudWatch for low latency infrastructure telemetry. I configured metric alarms evaluating Application Load Balancer 5XX errors and database connection drops. I wired alarm actions to an Amazon SNS topic for immediate email notification dispatch. I designed the external SIEM streaming path using CloudWatch Subscription Filters for long term compliance archiving.

## Consequences

### Positive
1. Native integration with AWS managed services (RDS, ALB, and EC2).
2. Serverless telemetry collection with zero RAM overhead on the application compute host.
3. Automated metric alarms evaluate conditions every sixty seconds without custom polling scripts.
4. Clean architectural separation between operational alarms and security SIEM compliance.

### Negative
1. Custom dashboarding capabilities in CloudWatch are less flexible than Grafana or Splunk SPL queries.
2. High volume log retention beyond seven days incurs storage charges if retention policies are unmanaged.