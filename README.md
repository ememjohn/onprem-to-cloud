# Apex Retail OMS: On-Premises to AWS Migration

This project implements an enterprise-grade migration and modernization of an on-premises Order Management System (OMS) to AWS.

## Architecture Path
- **Phase 1:** On-Premises Baseline (FastAPI + PostgreSQL on Docker Compose)
- **Phase 2–4:** Replatform to AWS EC2 compute + Amazon RDS for PostgreSQL
- **Phase 5–6:** Database replication and cutover using AWS DMS
- **Phase 7:** Observability and operations (Amazon CloudWatch)
- **Phase 8–9:** Application modernization to microservices on Amazon EKS
- **Phase 10:** Multi-Region Disaster Recovery (RTO/RPO validation)
