# Security Architecture Review: Sabay Premium Bank Core Ledger

## 1. Executive Summary
This document provides a formal security evaluation of the cloud landing zone and target compute architecture deployed for Sabay Premium Bank. The implementation adheres to strict financial services compliance standards, enforcing defense in depth network isolation, zero open inbound administrative ports, and encrypted secrets management.

## 2. Security Controls Verification Matrix
| Security Domain | Applied Security Control | Verification Test Executed | Audit Outcome |
| :--- | :--- | :--- | :--- |
| Perimeter Protection | Public Application Load Balancer across dual AZs | Probed HTTP port 80 forwarding to port 8000 target group | VERIFIED |
| Network Segmentation | Three tier VPC subnet architecture | Verified compute and database subnets have separate route tables | VERIFIED |
| Compute Bastion Elimination | AWS Systems Manager Session Manager | Verified remote execution on EC2 with port 22 closed | VERIFIED |
| Database Isolation | Dedicated isolated database subnets | Verified direct connection to port 5432 timed out from external host | VERIFIED |
| Secrets Protection | AWS Secrets Manager master credential store | Verified password injected at runtime with zero git commits | VERIFIED |
| Data at Rest Encryption | AWS KMS managed gp3 volume encryption | Verified root volumes and RDS storage use active encryption | VERIFIED |

## 3. Deep Dive: Defense in Depth Implementation

### 3.1 Elimination of Administrative SSH Exposure
Traditional server hosting exposes TCP port 22 to the public internet, exposing servers to brute force attacks and credential stuffing. 
Sabay Premium Bank completely eliminates port 22. The application host operates without SSH keys. Administrative shell execution occurs across an encrypted channel governed by AWS Identity and Access Management (IAM) through the AWS Systems Manager agent.

### 3.2 Database Tier Isolation Proof
The primary PostgreSQL instance operates within isolated database subnets mapped to private IP address 10.0.100.20. 
Direct network probes from public networks fail immediately:
Connection to 10.0.100.20 port 5432 timed out.
The database accepts incoming connections strictly from the application security group, preventing direct data exposure even in the event of an external network breach.

### 3.3 Dynamic Credential Injection
Database credentials reside exclusively within AWS Secrets Manager. The application bootstrap script fetches database connection details dynamically into memory during container startup. Version control systems and local configuration files contain zero plaintext passwords.
