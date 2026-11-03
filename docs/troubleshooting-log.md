# Engineering Incident Post Mortem Report

## Incident Summary Matrix
| Incident Reference | Root Cause Category | Impacted Subsystem | Resolution Time | Final Status |
| :--- | :--- | :--- | :--- | :--- |
| INC-BOOT-01 | Missing Runtime Python Dependency | Application Container (bank_source_app) | 5 Minutes | Resolved |
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


## Incident 3: Regional Service Control Policy Deny in AWS Organizations
### Severity
High (Complete API block across default regions)

### Technical Analysis
Initial Terraform planning targeting us-east-1 failed with an explicit authorization denial:
UnauthorizedOperation: User is not authorized to perform ec2:DescribeVpcs with an explicit deny in a service control policy.

Investigation identified that new AWS Builder accounts operate under automated organization guardrails. AWS attaches a default Service Control Policy locking new projects strictly to an assigned geographic region. Probing regional endpoints revealed that while us-east-1 was explicitly blocked, Primary Region (Stockholm) (Stockholm) held an active default VPC and full API permissions.

### Remediation Action
1. Updated Terraform variables to target region Primary Region (Stockholm) with availability zones Primary Region (Stockholm)a and Primary Region (Stockholm)b.
2. Verified API permissions using AWS CLI, confirming zero permission barriers in the Stockholm region.

---

## Incident 4: Interrupted State Reconciliation via Terraform Import
### Severity
High (State desynchronization following host power loss)

### Technical Analysis
During an active terraform apply run, the host workstation experienced an unexpected power shutdown. AWS had already initialized the Amazon RDS database instance in the cloud, but the local terraform.tfstate file was never updated with the resource ID. Subsequent execution attempts failed with an explicit cloud conflict:
DBInstanceAlreadyExists: DB instance already exists.

### Remediation Action
1. Queried the AWS RDS API to verify the instance was running and healthy.
2. Executed terraform import module.database.aws_db_instance.postgres sabay-bank-dev-postgres.
3. Reconciled the local state file with real cloud infrastructure, enabling Terraform to resume management without deleting or recreating the database.

---

## Incident 5: State Import Master Password Desynchronization
### Severity
High (Database authentication failure)

### Technical Analysis
Following the database state import, the application container failed healthcheck verification, returning HTTP 503. Log inspection revealed:
FATAL: password authentication failed for user "dbadmin".

Because Terraform state was reconstructed after the workstation power cut, Terraform generated a fresh random master password in Secrets Manager. However, the pre-existing Amazon RDS instance in AWS was still configured with the original password generated prior to the crash.

### Remediation Action
1. Extracted the active password string from AWS Secrets Manager.
2. Invoked aws rds modify-db-instance with the master user password parameter and the apply-immediately flag.
3. Restarted the application container on EC2, restoring database authentication.

---

## Incident 6: Transport Encryption Requirement on Managed RDS
### Severity
Medium (Database handshake rejection)

### Technical Analysis
Database migration execution aborted with a PostgreSQL security error:
FATAL: no pg_hba.conf entry for host, user "dbadmin", database "orders_db", no encryption.

Amazon RDS PostgreSQL parameter groups enforce transport layer encryption by default. Plain TCP connections lacking TLS negotiation are automatically dropped at the network socket layer.

### Remediation Action
1. Appended sslmode=require to the application database connection string.
2. Configured PGSSLMODE=require inside the containerized migration environment.
3. Successfully completed the TLS handshake, establishing an encrypted transport tunnel.

---

## Incident 7: Database Role Ownership Collision on Snapshot Restoration
### Severity
High (Schema restoration abort)

### Technical Analysis
Database restoration failed during table generation with the following error:
pg_restore: error: role "app_user" does not exist. Command was: ALTER TABLE public.customers OWNER TO app_user.

The source database snapshot preserved on premises table ownership under the role app_user. The target Amazon RDS instance was provisioned with the administrative master user dbadmin. When pg_restore attempted to assign ownership to a non-existent role, execution halted.

### Remediation Action
1. Executed a dynamic SQL pre-check creating the app_user role on Amazon RDS if not present.
2. Invoked pg_restore with the flag no-owner, allowing tables to restore under the active connection user dbadmin.
3. Granted table and sequence privileges across the public schema to app_user, ensuring the application container retains full read and write permissions.
