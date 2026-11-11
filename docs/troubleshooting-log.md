 Engineering Incident Post Mortem and Troubleshooting Log

## Executive Overview
This document records the technical incidents I encountered and resolved during the Sabay Premium Bank core ledger cloud migration. Each entry documents the exact error traceback, my root cause analysis, and the exact code fixes and commands I executed to restore operational health.

---

## Incident 1: ASGI Worker Boot Failure via Missing Validation Dependency
### Severity
High (Application container entered continuous crash restart loop)

### Error Traceback
```text
ImportError: email-validator is not installed, run pip install pydantic[email]
My Root Cause Analysis
I used Pydantic EmailStr in schemas.py to validate corporate customer email addresses. In modern Pydantic distributions, email validation logic resides in an optional library named email-validator. Because requirements.txt omitted this dependency, Python import mechanics terminated during FastAPI startup.
How I Fixed It
I added email-validator and pydantic[email] to app/requirements.txt:
Text
pydantic[email]>=2.6.4,<3.0.0
email-validator>=2.1.0,<3.0.0
I rebuilt the application container image:
Bash
docker compose -f source/compose.yaml up -d --build app
Incident 2: Archive Corruption During Custom Format Database Restoration
Severity
High (Data recovery failure)
Error Traceback
Text
pg_restore: error: could not read from input file: end of file
My Root Cause Analysis
I invoked pg_dump inside the database container using docker exec with the pseudo terminal allocation flag minus t. In Linux environments, pseudo terminal drivers automatically convert bare line feed bytes into carriage return line feed byte pairs. Because PostgreSQL custom format archives contain compressed binary data, carriage return injection corrupted internal file offsets and magic headers.
How I Fixed It
I stripped the minus t flag from scripts/backup_source_db.sh, executing docker exec purely in raw binary stream mode:
Bash
docker exec bank_source_db pg_dump -U app_user -d orders_db -Fc > "${BACKUP_FILE}"
I regenerated the snapshot and verified clean restoration without byte mangling:
Bash
./scripts/backup_source_db.sh
./scripts/restore_source_db.sh backups/orders_db_clean.dump
Incident 3: Regional Service Control Policy Deny in AWS Organizations
Severity
High (Complete API block across default regions)
Error Traceback
Text
An error occurred (UnauthorizedOperation) when calling the DescribeVpcs operation:
User: arn:aws:iam::<AWS_ACCOUNT_ID>:user/terraform-admin is not authorized to perform: ec2:DescribeVpcs
with an explicit deny in a service control policy: arn:aws:organizations::<MGMT_ACCOUNT_ID>:policy/<ORGANIZATION_ID>/service_control_policy/<SCP_POLICY_ID>
My Root Cause Analysis
My newly provisioned AWS Builder account operated under automated organization guardrails. AWS attached a default Service Control Policy locking new projects strictly to an assigned geographic region based on account registration country. Probing regional endpoints revealed that us-east-1 was blocked, while eu-north-1 (Stockholm) held an active default VPC and full API permissions.
How I Fixed It
I probed regional endpoints to discover the permitted region, and updated terraform/environments/dev/variables.tf to target Stockholm:
Hcl
variable "aws_region" {
  description = "Target AWS Region for deployment"
  type        = string
  default     = "eu-north-1"
}
Incident 4: Interrupted State Reconciliation via Terraform Import
Severity
High (State desynchronization following host power loss)
Error Traceback
Text
Error: creating RDS DB Instance (sabay-bank-dev-postgres):
api error DBInstanceAlreadyExists: DB instance already exists
My Root Cause Analysis
During an active terraform apply run, my host laptop experienced an unexpected power shutdown. AWS had already initialized the Amazon RDS database instance in the cloud, but my local terraform.tfstate file was never updated with the resource ID. Subsequent execution attempts failed because Terraform attempted to create a resource that already existed in AWS.
How I Fixed It
I reconciled my local state file with the live AWS resource using terraform import:
Bash
cd ~/onprem-to-cloud/terraform/environments/dev
terraform import module.database.aws_db_instance.postgres sabay-bank-dev-postgres
terraform plan
Incident 5: State Import Master Password Desynchronization
Severity
High (Database authentication failure)
Error Traceback
Text
HTTP/1.1 503 Service Unavailable
FATAL: password authentication failed for user "dbadmin"
My Root Cause Analysis
Because Terraform state was reconstructed after the workstation power cut, Terraform generated a brand new random password in Secrets Manager. However, the pre-existing Amazon RDS instance in AWS was still configured with the original password generated prior to the crash.
How I Fixed It
I extracted the password from Secrets Manager and updated Amazon RDS directly using the AWS CLI with apply-immediately:
Bash
SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id "sabay-bank-dev-db-credentials" --region eu-north-1 --query "SecretString" --output text)
DB_PASS=$(python3 -c "import json; print(json.loads('''$SECRET_JSON''')['password'])")

aws rds modify-db-instance \
  --region eu-north-1 \
  --db-instance-identifier "sabay-bank-dev-postgres" \
  --master-user-password "${DB_PASS}" \
  --apply-immediately
Incident 6: Transport Encryption Requirement on Managed RDS
Severity
Medium (Database handshake rejection)
Error Traceback
Text
connection to server at "<RDS_ENDPOINT>" port 5432 failed:
FATAL: no pg_hba.conf entry for host "<EC2_PRIVATE_IP>", user "dbadmin", database "orders_db", no encryption
My Root Cause Analysis
Amazon RDS PostgreSQL parameter groups enforce transport layer encryption by default. Plain unencrypted TCP connections lacking TLS negotiation are automatically dropped at the network socket layer.
How I Fixed It
I configured SSL mode requirement on both application connection strings and migration tooling, and downloaded the Amazon RDS global CA bundle:
Bash
DATABASE_URL="postgresql://dbadmin:<SECURE_PASSWORD>@<RDS_ENDPOINT>:5432/orders_db?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-ca-bundle.pem"
export PGSSLMODE="require"
Incident 7: Database Role Ownership Collision on Snapshot Restoration
Severity
High (Schema restoration abort)
Error Traceback
Text
pg_restore: error: could not execute query: ERROR: role "app_user" does not exist
Command was: ALTER TABLE public.customers OWNER TO app_user;
Command was: ALTER TABLE public.orders OWNER TO app_user;
My Root Cause Analysis
The on premises database snapshot preserved table ownership under the role app_user. The target Amazon RDS instance was provisioned with the administrative master user dbadmin. When pg_restore attempted to assign ownership to a non-existent role, execution halted.
How I Fixed It
I provisioned the app_user role on Amazon RDS, passed the no-owner flag to pg_restore, and granted schema privileges:
SQL
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user WITH LOGIN PASSWORD '<SECURE_PASSWORD>';
  END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE orders_db TO app_user;
Restoration command executed with no-owner:
Bash
pg_restore -h "<RDS_ENDPOINT>" -U "dbadmin" -d "orders_db" --no-owner --clean --if-exists /tmp/source.dump
Incident 8: Load Balancer HTTPS Listener Rejection via Pending Certificate
Severity
High (Perimeter SSL deployment blocked)
Error Traceback
Text
Error: creating ELBv2 Listener: api error UnsupportedCertificate:
The certificate must have a fully-qualified domain name, a supported signature, and a supported key size.
My Root Cause Analysis
I attempted to attach an ACM certificate for bank.saphigen.com to the Application Load Balancer port 443 listener in the same Terraform apply execution that requested the certificate. The AWS ELB API rejects attaching any certificate that is in status PENDING_VALIDATION.
How I Fixed It
I decoupled the port 443 listener temporarily, exported the ACM DNS validation CNAME records, and added the CNAME to Cloudflare DNS. Once the certificate transitioned to ISSUED status, I attached the port 443 listener with policy ELBSecurityPolicy-TLS13-1-2-2021-06 and configured the port 80 redirect.
Incident 9: Point in Time Restore Infinite Polling Loop via Future Timestamp
Severity
Medium (Automated drill script hung for 87 minutes)
Error Traceback
Text
InvalidParameterValue: RestoreTime must be between EarliestRestorableTime and LatestRestorableTime.
My Root Cause Analysis
My initial test script passed the current timestamp (now) to restore-db-instance-to-point-in-time. Amazon RDS transaction log archiving lags several minutes behind real time, so current time was rejected as an unarchived future timestamp. Because the script discarded standard error, it entered an infinite polling loop checking a database that was never created.
How I Fixed It
I updated scripts/execute_pitr_drill.py to query the exact LatestRestorableTime parameter from describe-db-instances and pass that verified timestamp to the restoration command. The drill completed successfully in 452 seconds.
