# Architecture Decision Record 003

## Title
Zero Open Port Administration via AWS Systems Manager Session Manager

## Status
Accepted

## Context
Sabay Premium Bank operates an application compute layer running on Amazon EC2. Traditional server administration requires opening inbound TCP port 22 for Secure Shell (SSH) access, often necessitating public IP assignment, bastion jump boxes, and SSH private key distribution. Financial regulators and security auditors consider open inbound management ports a critical vulnerability that increases attack surface.

## Decision Drivers
1. Eliminate Inbound Attack Surface: Prevent brute force and automated port scan attacks against port 22.
2. Centralize Identity and Access Management: Enforce fine grained access through AWS IAM without sharing SSH private keys.
3. Full Auditability: Capture every interactive shell session and command execution in Amazon CloudWatch and AWS CloudTrail.
4. Reduce Operational Cost: Avoid deploying and maintaining dedicated bastion jump hosts.

## Evaluated Alternatives
1. Traditional SSH on Port 22 with Bastion Host: Rejected because maintaining an internet facing bastion host adds unnecessary EC2 runtime costs, requires key rotation management, and exposes an inbound port to the internet.
2. VPN Gateway with SSH: Rejected due to substantial AWS Client VPN hourly charges and complex client software configuration during development phases.
3. AWS Systems Manager Session Manager: Selected. SSM utilizes an outbound HTTPS connection over port 443 initiated from the EC2 instance to the AWS Systems Manager endpoint. Inbound port 22 remains completely closed.

## Consequences
Positive:
1. Zero open inbound ports required on the EC2 security group.
2. Shell access permissions controlled strictly through IAM policies.
3. Every session invocation generates immutable audit logs in AWS CloudTrail.
4. Eliminates the risk of leaked private SSH keys.

Negative:
1. Requires the AWS Systems Manager agent pre installed on the target machine image.
2. Outbound network path to AWS service endpoints must exist.
