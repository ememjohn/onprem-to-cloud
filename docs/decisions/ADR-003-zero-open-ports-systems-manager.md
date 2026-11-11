# Architecture Decision Record 003

## Title
Zero Open Port Administration via AWS Systems Manager Session Manager

## Status
Accepted

## Context
Traditional server administration requires opening inbound TCP port 22 for SSH access. Financial regulators and security auditors consider open inbound management ports an unacceptable vulnerability that increases attack surface.

## Decision Drivers
1. Attack Surface Elimination: Prevent automated port scans and brute force credential attacks against port 22.
2. Centralized Identity Management: Control shell access through AWS IAM policies rather than static SSH private keys.
3. Complete Auditability: Record every interactive shell session and command execution in AWS CloudTrail.
4. Cost Optimization: Avoid deploying and paying for dedicated bastion jump hosts.

## Evaluated Alternatives

### 1. Traditional SSH on Port 22 with Bastion Jump Host
I rejected this approach. Maintaining an internet facing bastion host adds standing EC2 compute costs, requires SSH key distribution and rotation, and exposes a public management port to the internet.

### 2. Client VPN Gateway with SSH
I rejected this approach. AWS Client VPN incurs substantial hourly connection charges and endpoint fees during development phases.

### 3. AWS Systems Manager Session Manager
I selected AWS Systems Manager Session Manager. The SSM agent initiates an outbound HTTPS connection over port 443 from the EC2 instance to AWS Systems Manager endpoints. Inbound port 22 remains completely closed.

## My Decision
I chose AWS Systems Manager Session Manager. I closed TCP port 22 completely in all security groups. I attached the AmazonSSMManagedInstanceCore policy to the EC2 IAM Instance Profile. All administrative shell executions operate across an encrypted HTTPS channel governed by AWS IAM.

## Consequences

### Positive
1. Zero open inbound administrative ports on the compute host.
2. Shell access permissions controlled strictly through IAM policies.
3. Eliminates the risk of lost or leaked SSH private keys.
4. Every session invocation generates immutable audit logs in AWS CloudTrail.

### Negative
1. Requires the AWS Systems Manager agent pre installed on the machine image.
2. The compute host requires an outbound HTTPS network path to reach AWS service endpoints.