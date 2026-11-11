# Architecture Decision Record 011

## Title
Cryptographic Secrets Management: AWS Secrets Manager with KMS Envelope Encryption

## Status
Accepted

## Context
The core banking ledger requires high entropy credentials to authenticate against Amazon RDS PostgreSQL. Financial regulations strictly prohibit hardcoding database passwords in application source code, storing credentials in plaintext files on disk, or committing secrets into version control.

## Decision Drivers
1. Zero Plaintext Exposure: Passwords must never touch disk configuration files or git commits.
2. Dynamic In-Memory Retrieval: Application containers must fetch credentials into memory at runtime.
3. Automated Credential Rotation Readiness: Architecture must support automated password rotation without rebuilding container images.
4. Cryptographic Protection: Secrets must be encrypted using AWS Key Management Service (KMS) managed keys.

## Evaluated Alternatives

### 1. Plaintext Environment Configuration (.env files)
I rejected plaintext configuration files. Files on disk are vulnerable to unauthorized host inspection, container snapshot leakage, and accidental git commits.

### 2. AWS Systems Manager Parameter Store
I evaluated Parameter Store as a low cost alternative. I rejected it because it lacks built in automated rotation workflows for relational databases.

### 3. AWS Secrets Manager with KMS Encryption
I selected AWS Secrets Manager. It provides native integration with Amazon RDS, automated recovery windows, fine grained IAM execution policies, and dynamic runtime retrieval.

## My Decision
I chose AWS Secrets Manager with KMS envelope encryption. I created the secret sabay-bank-dev-db-credentials in Terraform. I authored deployment automation that queries the secret over the AWS CLI and injects credentials directly into container runtime memory without touching disk configuration files.

## Consequences

### Positive
1. Zero credentials committed to git or stored in plaintext configuration files.
2. Passwords inject directly into container memory via AWS CLI and Python runtime drivers.
3. Full audit logging in AWS CloudTrail for every secret read operation.
4. Ready for automated credential rotation without application code modifications.

### Negative
1. AWS Secrets Manager incurs an ongoing cost of forty cents per secret monthly plus API call charges.
2. Application startup depends on network availability to AWS Secrets Manager service endpoints.