# System Architecture Specification: On Premises Source Environment

## Executive Briefing
| Attribute | Specification | Operational Target |
| :--- | :--- | :--- |
| Workload Classification | Enterprise Order Management System (OMS) | Internal Retail Procurement |
| Current Hosting Model | Single Host Linux Server (Docker Compose) | Target: AWS Cloud Replatforming |
| Primary SLA Target | 99.9 Percent Availability | Zero Data Loss (RPO Zero for Orders) |
| Active Compute Engine | Python 3.12 with FastAPI Framework | Asynchronous ASGI Worker Model |
| Active Database Engine | PostgreSQL 16 Alpine Distribution | ACID Relational Model |

```mermaid
graph TD
    Client[HTTP Client: Port 8000] -->|ASGI HTTP Request| AppService[FastAPI Application: oms_source_app]
    
    subgraph Host Infrastructure: Linux Server
        AppService -->|SQLAlchemy Connection Pool: Port 5432| DBService[(PostgreSQL 16: oms_source_db)]
        DBService -->|Direct Block I/O: Mount /var/lib/postgresql/data| DataVolume[(Named Docker Volume: oms_source_pgdata)]
        OpsTooling[Backup Automation: pg_dump] -.->|Direct Binary Stream| DBService
    end

    subgraph Storage Subsystem
        OpsTooling --> BackupStorage[Local Backup Archive: backups/*.dump]
    end
Layer Specifications Matrix
Compute Subsystem
Parameter	Configuration	Technical Justification
ASGI Web Server	Uvicorn Standard	Asynchronous non blocking socket processing
API Framework	FastAPI 0.110.0	High performance request validation and OpenAPI automation
Object Relational Mapper	SQLAlchemy 2.0 Core	Thread safe connection pooling with pre ping validation
Connection Pool Ceiling	10 persistent sockets, 20 overflow sockets	Protects PostgreSQL from connection exhaustion
Healthcheck Mechanism	Active Database Query (SELECT 1)	Prevents routing traffic to unhealthy application instances
Persistence Subsystem
Parameter	Configuration	Technical Justification
Database Engine	PostgreSQL 16.4 Alpine	Standards compliant relational engine with logical decoding
Storage Architecture	Named Docker Volume: oms_source_pgdata	Isolates database files from container lifecycle events
Foreign Key Policies	ON DELETE CASCADE	Enforces referential integrity between customers and orders
Sequence Alignment	Explicit setval invocation at startup	Prevents primary key collisions during post migration writes
Binary Backup Tooling	pg_dump custom format (-Fc)	Compressed point in time snapshots with checksum validation
Network and Ingress Topology
Network Identifier	Driver Type	Exposed Endpoints	Security Scope
oms_source_network	Linux Bridge	Port 8000 (App), Port 5432 (DB)	Isolated internal subnet
Host Interface	IPv4 Loopback and Interface Binding	0.0.0.0:8000, 0.0.0.0:5432	Development testing and monitoring access
