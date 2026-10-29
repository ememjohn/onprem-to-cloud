# Engineering Incident Post Mortem Report

## Incident Summary Matrix
| Incident Reference | Root Cause Category | Impacted Subsystem | Resolution Time | Final Status |
| :--- | :--- | :--- | :--- | :--- |
| INC-BOOT-01 | Missing Runtime Python Dependency | Application Container (oms_source_app) | 5 Minutes | Resolved |
| INC-DUMP-02 | Pseudo TTY Binary Stream Corruption | Storage Restoration Pipeline (pg_restore) | 10 Minutes | Resolved |

## Detailed Post Mortem: INC-BOOT-01
### Symptom
Application container terminated immediately upon startup, reporting status Restarting 1 in Docker Compose.

### Root Cause Analysis
The FastAPI schema definition utilizes Pydantic EmailStr for request parameter validation. Modern Pydantic distributions delegate email parsing to an optional third party library named email-validator. Because requirements.txt omitted this explicit requirement, the Python runtime raised an unhandled ImportError during module import.

### Remediation Action
1. Appended email-validator version 2.1.0 and pydantic[email] version 2.6.4 to app/requirements.txt.
2. Executed docker compose build app to compile an updated container image.
3. Probed /healthz endpoint, confirming HTTP 200 response.

## Detailed Post Mortem: INC-DUMP-02
### Symptom
Database restoration drill failed with critical error: pg_restore error could not read from input file end of file.

### Root Cause Analysis
The automated backup routine invoked pg_dump via docker exec using the pseudo TTY allocation flag minus t. In Linux environments, pseudo TTY drivers translate bare newline characters into carriage return line feed pairs. Because PostgreSQL custom format archives (-Fc) contain compressed binary data, carriage return injection altered internal file offsets and corrupted header blocks. The restoration utility terminated when calculated offsets exceeded physical file boundaries.

### Remediation Action
1. Stripped the minus t flag from scripts/backup_source_db.sh, executing docker exec purely in raw binary stream mode.
2. Regenerated database snapshot archive orders_db.dump.
3. Executed restoration drill against temporary test database. Restoration utility restored all tables, sequences, and five records with zero corruption.
