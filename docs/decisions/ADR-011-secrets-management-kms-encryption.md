# Architecture Decision Record 011

## Title
Cryptographic Secrets Management: AWS Secrets Manager with KMS Envelope Encryption

## Status
Accepted

## Context
The core ledger requires high entropy credentials to authenticate against Amazon RDS PostgreSQL. Financial regulators strictly prohibit hardcoding passwords in application source code, storing credentials in plaintext files on disk, or committing secrets into version control systems.

## Decision Drivers
1. Zero Plaintext Exposure: Passwords must never touch disk configuration files or git commits.
2. Dynamic In-Memory Retrieval: Application containers must fetch credentials into memory at runtime.
3. Automated Credential Rotation Readiness: Architecture must support automated password rotation without rebuilding container images.
4. Cryptographic Envelope Protection: Secrets must be encrypted using customer managed or AWS managed keys in AWS Key Management Service (KMS).

## Evaluated Alternatives
1. Plaintext Environment Configuration (.env files): Rejected. Files on disk are vulnerable to unauthorized host inspection, container snapshot leakage, and accidental git commits.
2. AWS Systems Manager Parameter Store: Evaluated as a low cost alternative but lacks built in automated rotation workflows for relational databases.
3. AWS Secrets Manager with KMS Encryption: Selected. Provides native integration with Amazon RDS, automated recovery windows, fine grained IAM execution policies, and dynamic runtime retrieval.

## Consequences
Positive:
1. Zero credentials committed to git or stored in plaintext configuration files.
2. Passwords inject directly into container memory via AWS CLI and Python runtime drivers.
3. Full audit logging in AWS CloudTrail for every secret read operation.

Negative:
1. AWS Secrets Manager incurs an ongoing cost of forty cents per secret monthly plus API call charges.
