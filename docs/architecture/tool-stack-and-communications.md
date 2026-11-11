# Comprehensive Tool Stack and Communication Mapping

## 1. Executive Summary
This specification documents the complete technology stack deployed for the Sabay Premium Bank core ledger cloud migration. It defines every tool, its operational purpose, its networking protocol, and its bidirectional communication flow across system boundaries.

## 2. Infrastructure as Code and Cloud Provisioning
| Tool | Specification | Operational Role | Communication Target | Protocol & Port |
| :--- | :--- | :--- | :--- | :--- |
| HashiCorp Terraform | Version 1.15+ | Declares and reconciles all AWS cloud infrastructure | AWS Regional API Endpoints | HTTPS Port 443 (TLS 1.3) |
| AWS CLI | Version 2.34+ | Terminal command line interface for diagnostics and automation | AWS Regional API Endpoints | HTTPS Port 443 (TLS 1.3) |
| Cloudflare DNS | DNS Host | Authoritative nameserver routing bank.saphigen.com | AWS Application Load Balancer | DNS CNAME Resolution |

## 3. Network and Edge Ingress Tier
| Component | Identifier | Security Rules | Communication Flow | Protocol & Port |
| :--- | :--- | :--- | :--- | :--- |
| AWS Internet Gateway | Custom VPC Gateway | Attached to VPC perimeter | Routes public traffic to public subnets | Inbound / Outbound IPv4 |
| Application Load Balancer | sabay-bank-dev-alb | Security Group: alb-sg | Receives public HTTPS traffic, redirects port 80 to 443 | Port 80 (HTTP Redirect), Port 443 (HTTPS) |
| AWS Certificate Manager | bank.saphigen.com | RSA 2048-bit Certificate | Provides SSL termination on Application Load Balancer | Ingress TLS 1.3 Handshake |
| ALB Target Group | sabay-bank-dev-app-tg | Port 8000 target registration | Probes /healthz every 15 seconds, forwards traffic to EC2 | HTTP Port 8000 |

## 4. Application Compute Tier
| Component | Identifier | Security Rules | Communication Flow | Protocol & Port |
| :--- | :--- | :--- | :--- | :--- |
| Amazon EC2 Host | sabay-bank-dev-app-host | Security Group: app-sg | Runs containerized FastAPI application core | Ingress Port 8000 strictly from alb-sg |
| Amazon Linux 2023 | Minimal AMI x86_64 | IMDSv2 Enforced | Host operating system running Docker runtime | Outbound HTTPS Port 443 to AWS APIs |
| AWS Systems Manager | SSM Session Manager | IAM Role Attached | Encrypted administrative shell channel, port 22 closed | Outbound HTTPS Port 443 to SSM Endpoints |
| FastAPI Application | Version 0.110+ | Uvicorn ASGI Server | Serves luxury banking console and JSON REST API | Inbound HTTP Port 8000 |

## 5. Persistence and Data Layer
| Component | Identifier | Security Rules | Communication Flow | Protocol & Port |
| :--- | :--- | :--- | :--- | :--- |
| Amazon RDS PostgreSQL | sabay-bank-dev-postgres | Security Group: db-sg | Primary relational storage engine for banking ledger | Ingress Port 5432 strictly from app-sg |
| Storage Volume | 20 GB gp3 SSD | AWS KMS Encryption | Stores table disk blocks with baseline 3000 IOPS | Internal Block Storage I/O |
| Database CA Certificate | global-bundle.pem | Enforced on Client | Authenticates Amazon RDS identity to client container | TLS 1.3 with verify-full SSL mode |
| AWS Secrets Manager | sabay-bank-dev-db-credentials | KMS Key Encrypted | Stores database master credentials with zero git commits | Dynamic In-Memory Retrieval via API |

## 6. SRE Observability and Incident Alerting
| Component | Identifier | Evaluation Window | Operational Flow | Action Target |
| :--- | :--- | :--- | :--- | :--- |
| CloudWatch Log Group | /aws/ec2/sabay-bank-dev-core | 7 Day Retention | Aggregates container stdout and stderr runtime logs | SRE Log Inspection |
| CloudWatch Alarm (5XX) | sabay-bank-dev-high-5xx-errors | 60 Second Period | Evaluates HTTPCode_Target_5XX_Count >= 1 | Amazon SNS Topic Alerts |
| CloudWatch Alarm (Health) | sabay-bank-dev-unhealthy-hosts | 60 Second Period | Evaluates UnHealthyHostCount >= 1 | Amazon SNS Topic Alerts |
| CloudWatch Alarm (DB) | sabay-bank-dev-rds-zero-connections | 300 Second Period | Evaluates DatabaseConnections < 1 during active load | Amazon SNS Topic Alerts |
| Amazon SNS Topic | sabay-bank-dev-alerts | Immediate Dispatch | Dispatches automated email incident notifications | officialememjohn@gmail.com |

## 7. Migration and Security Quality Assurance Tooling
| Tool | Scope | Implementation | Verification Outcome |
| :--- | :--- | :--- | :--- |
| Gitleaks | Git History & Tree | Automated pattern scanner | 46 commits scanned with zero secret leaks |
| SHA-256 Validation Engine | Data Parity Audit | Row level cryptographic hashing | Exact match across 100,000 relational records |
| PostgreSQL Client Utilities | pg_dump and pg_restore | Custom format binary pipelines | Schema restoration executed with no-owner flag |
| OpenSSL Client | SSL Audit Tool | Handshake inspection | Confirmed TLS 1.3 protocol and TLS_AES cipher |

