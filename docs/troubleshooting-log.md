 Engineering Incident Post Mortem and Troubleshooting Log

## Executive Overview
This document records the technical incidents I encountered and resolved during the Sabay Premium Bank core ledger cloud migration. Each entry documents the exact error traceback, my root cause analysis, and the exact code fixes and commands I executed to restore operational health.

---

## Incident 1: ASGI Worker Boot Failure via Missing Validation Dependency
### Severity
High (Application container entered continuous crash restart loop)

## Incident index
 
| # | Incident | Severity | Area |
|---|----------|----------|------|
| 1 | [Missing email-validator dependency at startup](#incident-1-missing-email-validator-dependency-at-startup) | High | Application |
| 2 | [Archive corruption during custom format restore](#incident-2-archive-corruption-during-custom-format-restore) | High | Data recovery |
| 3 | [Regional service control policy deny](#incident-3-regional-service-control-policy-deny) | High | AWS Organizations |
| 4 | [Interrupted Terraform state after power loss](#incident-4-interrupted-terraform-state-after-power-loss) | High | Terraform |
| 5 | [RDS master password desynchronization](#incident-5-rds-master-password-desynchronization) | High | Database access |
| 6 | [Transport encryption requirement on RDS](#incident-6-transport-encryption-requirement-on-rds) | Medium | Database access |
| 7 | [Role ownership collision on snapshot restore](#incident-7-role-ownership-collision-on-snapshot-restore) | High | Data migration |
| 8 | [HTTPS listener rejected by pending certificate](#incident-8-https-listener-rejected-by-pending-certificate) | High | Load balancer |
| 9 | [PITR drill hung on future timestamp](#incident-9-pitr-drill-hung-on-future-timestamp) | Medium | Recovery testing |
 
---
 
## Incident 1: Missing email-validator dependency at startup
 
**Severity:** High (application startup failure)
 
### Error
 
```text
ImportError: email-validator is not installed, run pip install pydantic[email]
```
 
### Root cause
 
I used Pydantic `EmailStr` in `schemas.py` to validate corporate customer email addresses. In modern Pydantic releases, email validation lives in an optional library named `email-validator`. `requirements.txt` did not list that dependency, so Python stopped the import during FastAPI startup.
 
### Fix
 
1. Add both packages to `app/requirements.txt`:
```text
pydantic[email]>=2.6.4,<3.0.0
email-validator>=2.1.0,<3.0.0
```
 
2. Rebuild the application container image:
```bash
docker compose -f source/compose.yaml up -d --build app
```
 
---
 
## Incident 2: Archive corruption during custom format restore
 
**Severity:** High (data recovery failure)
 
### Error
 
```text
pg_restore: error: could not read from input file: end of file
```
 
### Root cause
 
I ran `pg_dump` inside the database container with `docker exec` and the `-t` flag, which allocates a pseudo terminal. Linux pseudo terminal drivers convert bare line feed bytes into carriage return plus line feed pairs. PostgreSQL custom format archives (`-Fc`) hold compressed binary data, so the injected carriage returns corrupted the internal file offsets and magic headers.
 
### Fix
 
1. Remove the `-t` flag from `scripts/backup_source_db.sh` so `docker exec` streams raw binary:
```bash
docker exec bank_source_db pg_dump -U app_user -d orders_db -Fc > "${BACKUP_FILE}"
```
 
2. Regenerate the snapshot and confirm a clean restore:
```bash
./scripts/backup_source_db.sh
./scripts/restore_source_db.sh backups/orders_db_clean.dump
```
 
---
 
## Incident 3: Regional service control policy deny
 
**Severity:** High (complete API block across default regions)
 
### Error
 
```text
An error occurred (UnauthorizedOperation) when calling the DescribeVpcs operation:
User: arn:aws:iam::<AWS_ACCOUNT_ID>:user/terraform-admin is not authorized to perform: ec2:DescribeVpcs
with an explicit deny in a service control policy: arn:aws:organizations::<MGMT_ACCOUNT_ID>:policy/<ORGANIZATION_ID>/service_control_policy/<SCP_POLICY_ID>
```
 
### Root cause
 
My new AWS Builder account ran under automated organization guardrails. AWS attached a default Service Control Policy (SCP) that locks new projects to one region, chosen from the account registration country. Probing regional endpoints showed `us-east-1` was blocked, while `eu-north-1` (Stockholm) had an active default VPC and full API permissions.
 
### Fix
 
1. Probe regional endpoints to find the permitted region.
2. Set Stockholm as the target in `terraform/environments/dev/variables.tf`:
```hcl
variable "aws_region" {
  description = "Target AWS Region for deployment"
  type        = string
  default     = "eu-north-1"
}
```
 
---
 
## Incident 4: Interrupted Terraform state after power loss
 
**Severity:** High (state desynchronization after host power loss)
 
### Error
 
```text
Error: creating RDS DB Instance (sabay-bank-dev-postgres):
api error DBInstanceAlreadyExists: DB instance already exists
```
 
### Root cause
 
My laptop lost power during an active `terraform apply`. AWS had already created the Amazon RDS instance, but the local `terraform.tfstate` file never recorded the resource ID. The next run tried to create a resource that already existed.
 
### Fix
 
Reconcile the local state with the live AWS resource using `terraform import`, then confirm with a plan:
 
```bash
cd ~/onprem-to-cloud/terraform/environments/dev
terraform import module.database.aws_db_instance.postgres sabay-bank-dev-postgres
terraform plan
```
 
---
 
## Incident 5: RDS master password desynchronization
 
**Severity:** High (database authentication failure)
 
### Error
 
```text
HTTP/1.1 503 Service Unavailable
FATAL: password authentication failed for user "dbadmin"
```
 
### Root cause
 
Terraform rebuilt its state after the power loss in Incident 4 and generated a new random password in Secrets Manager. The existing RDS instance still used the original password from before the crash, so the two no longer matched.
 
### Fix
 
Read the password from Secrets Manager, then set it on the RDS instance with the AWS CLI:
 
```bash
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "sabay-bank-dev-db-credentials" \
  --region eu-north-1 \
  --query "SecretString" \
  --output text)
 
DB_PASS=$(python3 -c "import json; print(json.loads('''$SECRET_JSON''')['password'])")
 
aws rds modify-db-instance \
  --region eu-north-1 \
  --db-instance-identifier "sabay-bank-dev-postgres" \
  --master-user-password "${DB_PASS}" \
  --apply-immediately
```
 
---
 
## Incident 6: Transport encryption requirement on RDS
 
**Severity:** Medium (database handshake rejection)
 
### Error
 
```text
connection to server at "<RDS_ENDPOINT>" port 5432 failed:
FATAL: no pg_hba.conf entry for host "<EC2_PRIVATE_IP>", user "dbadmin", database "orders_db", no encryption
```
 
### Root cause
 
Amazon RDS PostgreSQL parameter groups enforce transport encryption. RDS drops plain TCP connections that do not negotiate TLS.
 
### Fix
 
1. Download the Amazon RDS global CA bundle to `/etc/ssl/certs/rds-ca-bundle.pem`.
2. Require TLS in the application connection string and the migration tooling:
```bash
DATABASE_URL="postgresql://dbadmin:<SECURE_PASSWORD>@<RDS_ENDPOINT>:5432/orders_db?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-ca-bundle.pem"
export PGSSLMODE="require"
```
 
---
 
## Incident 7: Role ownership collision on snapshot restore
 
**Severity:** High (schema restoration abort)
 
### Error
 
```text
pg_restore: error: could not execute query: ERROR: role "app_user" does not exist
Command was: ALTER TABLE public.customers OWNER TO app_user;
Command was: ALTER TABLE public.orders OWNER TO app_user;
```
 
### Root cause
 
The on-premises snapshot records table ownership under the role `app_user`. I created the RDS instance with the master user `dbadmin`, so `app_user` did not exist. When `pg_restore` tried to assign ownership to a missing role, it stopped.
 
### Fix
 
1. Create the `app_user` role on RDS and grant it database privileges:
```sql
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user WITH LOGIN PASSWORD '<SECURE_PASSWORD>';
  END IF;
END
$$;
 
GRANT ALL PRIVILEGES ON DATABASE orders_db TO app_user;
```
 
2. Restore with `--no-owner` so `pg_restore` skips ownership assignment:
```bash
   pg_restore -h "<RDS_ENDPOINT>" -U "dbadmin" -d "orders_db" --no-owner --clean --if-exists /tmp/source.dump
```
 
---
 
## Incident 8: HTTPS listener rejected by pending certificate
 
**Severity:** High (perimeter SSL deployment blocked)
 
### Error
 
```text
Error: creating ELBv2 Listener: api error UnsupportedCertificate:
The certificate must have a fully-qualified domain name, a supported signature, and a supported key size.
```
 
### Root cause
 
I tried to attach an ACM certificate to the Application Load Balancer port 443 listener in the same `terraform apply` that requested the certificate. The ELB API rejects any certificate in `PENDING_VALIDATION` status.
 
### Fix
 
1. Remove the port 443 listener from the first apply.
2. Export the ACM DNS validation CNAME records.
3. Add the CNAME records to Cloudflare DNS.
4. Wait for the certificate status to change to `ISSUED`.
5. Attach the port 443 listener with the policy `ELBSecurityPolicy-TLS13-1-2-2021-06`.
6. Configure the port 80 listener to redirect to HTTPS.
---
 
## Incident 9: PITR drill hung on future timestamp
 
**Severity:** Medium (automated drill script hung for 87 minutes)
 
### Error
 
```text
InvalidParameterValue: RestoreTime must be between EarliestRestorableTime and LatestRestorableTime.
```
 
### Root cause
 
My first test script passed the current timestamp to `restore-db-instance-to-point-in-time`. RDS transaction log archiving runs a few minutes behind real time, so RDS rejected the current time as a future timestamp. The script discarded standard error, so it polled forever for a database that never existed.
 
### Fix
 
1. Update `scripts/execute_pitr_drill.py` to read `LatestRestorableTime` from `describe-db-instances`.
2. Pass that verified timestamp to the restore command.
The drill then completed in 452 seconds.
