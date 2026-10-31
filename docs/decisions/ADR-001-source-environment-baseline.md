# Architecture Decision Record 001

## Title
Source Environment Architecture and Baseline Stack Selection

## Status
Accepted

## Context
Sabay Premium Bank operates an internal Order Management System. The current production setup runs on an on premises Linux server. The business intends to migrate this workload to AWS to improve reliability and prepare for microservices modernization. Before planning any cloud infrastructure, engineering must construct a reproducible local replica of the source environment. This replica allows us to benchmark response times, prove data persistence, establish baseline backups, and test replication mechanisms without risking business operations.

## Decision
We select the following baseline architecture:
1. Application Runtime: Python 3.12 with FastAPI. FastAPI provides strict schema validation through Pydantic, asynchronous performance, and standard OpenAPI documentation.
2. Database Engine: PostgreSQL 16 on Linux Alpine. PostgreSQL gives us enterprise relational guarantees, ACID compliance, and standard write ahead log replication capabilities required for AWS Database Migration Service.
3. Compute Orchestration: Docker Compose with a dedicated bridge network.
4. Storage Strategy: Named Docker volume named oms_source_pgdata. Database files reside on the host disk independently of container lifecycle events.

## Alternatives Considered
1. SQLite: Rejected because SQLite lacks network daemon capabilities, connection pooling, and AWS Database Migration Service change data capture support.
2. Direct Host Installation: Installing PostgreSQL and Python directly on the workstation host without containers was rejected because it causes dependency conflicts across developer environments and prevents clean teardowns.
3. Django Framework: Rejected due to unnecessary administrative overhead. FastAPI provides a lighter memory footprint and faster boot times.

## Consequences
Positive:
1. Complete reproducibility across any Linux workstation.
2. Fast test cycles using Docker Compose.
3. Clean separation between application configuration and database storage.

Negative:
1. Docker desktop or daemon overhead on the host workstation.
2. Requires explicit handling of Unix file permissions for container volume mounts.
