# Security Architecture Review: Sabay Premium Bank Core Ledger

## 1. Executive Summary
This document provides a formal security audit of the cloud landing zone deployed for Sabay Premium Bank. The implementation enforces defense in depth network isolation, zero open inbound administrative ports, transport layer encryption, token based metadata protection, and automated secret scanning.

## 2. Verified Security Controls Matrix
| Security Control | Technical Implementation | Audit Verification Status | Primary Evidence Source |
| :--- | :--- | :--- | :--- |
| Public Edge Ingress | HTTPS port 443 with TLS 1.3 policy | Verified (HTTP/2 200 via bank.saphigen.com) | docs/evidence/2026-11-08-tls-1-3-proof.txt |
| Insecure Traffic Redirect | ALB port 80 listener 301 redirect to 443 | Verified (HTTP 301 Moved Permanently) | docs/evidence/2026-11-08-tls-1-3-proof.txt |
| Instance Metadata Security | EC2 MetadataOptions HttpTokens required | Verified (HttpTokens required on instance) | docs/evidence/2026-11-08-imdsv2-and-encryption-proof.txt |
| Data at Rest Encryption | AWS KMS gp3 volumes on EBS and RDS | Verified (StorageEncrypted is True) | docs/evidence/2026-11-08-imdsv2-and-encryption-proof.txt |
| Database Transport Security | RDS force_ssl with sslmode=verify-full | Verified (pg_stat_ssl TLS 1.3 verified) | docs/evidence/2026-11-08-rds-ssl-verify-full-proof.txt |
| Zero Open SSH Ports | AWS Systems Manager Session Manager | Verified (Port 22 closed, SSM Online) | docs/evidence/2026-11-08-imdsv2-and-encryption-proof.txt |
| Database Network Isolation | Dedicated isolated subnets | Verified (Direct port 5432 probes timed out) | docs/evidence/2026-11-07-alb-target-health.txt |
| Automated Secret Leak Audit | Gitleaks scanning across full history | Verified (46 commits scanned with 0 leaks) | docs/evidence/2026-11-08-gitleaks-audit-proof.txt |
| SRE Alerting Channel | Amazon SNS topic with email dispatch | Verified (Subscription confirmed to email) | docs/evidence/2026-11-08-alarms-trigger-proof.txt |

## 3. Deep Dive: Defense in Depth Verification

### 3.1 Perimeter HTTPS and TLS 1.3 Enforcement
Public web traffic terminates at the Application Load Balancer using an AWS Certificate Manager RSA 2048-bit certificate issued for bank.saphigen.com. 

The load balancer enforces the ELBSecurityPolicy-TLS13-1-2-2021-06 policy. Inbound port 80 requests receive an immediate HTTP 301 redirect to HTTPS port 443. OpenSSL inspection verified the negotiated handshake protocol is TLSv1.3 with cipher TLS_AES_128_GCM_SHA256.

### 3.2 Elimination of Administrative SSH Exposure
The application compute host operates with zero open inbound management ports. TCP port 22 is omitted from all security groups. 

Administrative access operates across an encrypted channel governed by AWS Identity and Access Management through the AWS Systems Manager agent. All interactive sessions generate immutable audit records in AWS CloudTrail.

### 3.3 Instance Metadata Service Hardening (IMDSv2)
The Amazon EC2 instance enforces IMDSv2 by setting HttpTokens to required. 

This configuration prevents server side request forgery vulnerabilities from harvesting instance profile credentials. Any request lacking a valid session token is rejected by the hypervisor metadata service.

### 3.4 Cryptographic Transport Security to Managed Persistence
Amazon RDS PostgreSQL enforces transport encryption via rds.force_ssl = 1. 

The application container mounts the Amazon RDS global certificate authority bundle at /etc/ssl/certs/rds-ca-bundle.pem. Client connections require sslmode=verify-full, validating both the certificate authority signature and the database server hostname before completing the socket handshake.

### 3.5 Storage Encryption at Rest
All persistent storage volumes utilize AWS KMS encryption:
1. Amazon EC2 root block device: 20 GB gp3 volume encrypted with AWS KMS.
2. Amazon RDS database cluster: 20 GB gp3 volume encrypted with AWS KMS.