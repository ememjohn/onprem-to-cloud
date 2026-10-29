# On-Prem to Cloud: Enterprise Migration & Modernization

A production-grade, staged migration of an on-premises Order Management System (OMS) to the Cloud (AWS implementation).

## Architectural Path
- **Phase 1:** On-Premises Baseline (FastAPI + PostgreSQL on Docker Compose)
- **Phase 2–4:** Replatform to AWS Compute (EC2) & Managed Database (RDS PostgreSQL)
- **Phase 5–6:** Database Replication & Zero-Downtime Cutover (AWS DMS)
- **Phase 7:** Enterprise Observability & Operations (CloudWatch)
- **Phase 8–9:** Application Modernization into Microservices (Amazon EKS)
- **Phase 10:** Multi-Region Disaster Recovery (RTO/RPO validation)
