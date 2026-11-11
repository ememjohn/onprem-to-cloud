# Architecture Decision Record 001

## Title
Source Environment Architecture and Baseline Stack Selection

## Status
Accepted

## Context
Sabay Premium Bank operates an on premises core banking ledger. Before designing cloud infrastructure, I had to construct a reproducible local replica of the source environment. This allowed me to benchmark response times, prove data persistence, establish baseline backups, and test replication mechanisms without risking real business operations.

## Decision Drivers
1. Complete Reproducibility: Any engineer must be able to boot the entire banking environment locally with one command.
2. Relational Transaction Guarantees: The persistence tier must support ACID transactions and foreign key cascades.
3. Logical Replication Readiness: The database engine must support write ahead log extraction for downstream cloud migration.
4. Memory Efficiency: The baseline stack must run alongside developer tooling without exhausting workstation memory.

## Evaluated Alternatives

### 1. SQLite File Database
I rejected SQLite. It lacks network daemon capabilities, client connection pooling, and write ahead log decoding required for cloud replication.

### 2. Direct Bare Metal Host Installation
I rejected installing PostgreSQL and Python directly on the workstation host without containers. Bare metal installations introduce dependency conflicts across developer environments and prevent clean environment resets.

### 3. Django Framework with Built In Admin
I rejected Django due to administrative overhead and heavy memory footprint. FastAPI provides faster ASGI startup times, lower memory consumption, and native OpenAPI documentation.

## My Decision
I selected Python 3.12 with FastAPI for the application tier, and PostgreSQL 16 on Linux Alpine for the persistence tier, orchestrated via Docker Compose. 

I bound the database container to a named Docker volume identified as bank_source_pgdata to ensure data survives container destruction. I configured the application connection pool using SQLAlchemy with pre ping socket verification to automatically drop broken connections.

## Consequences

### Positive
1. Complete environment parity across any Linux workstation using Docker Compose.
2. Asynchronous non blocking request processing for concurrent client queries.
3. Clean separation between ephemeral application compute and persistent database storage.

### Negative
1. Running container daemons on local workstations consumes baseline host memory.
2. Named Docker volume management requires explicit volume inspection commands.