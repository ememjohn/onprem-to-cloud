#!/usr/bin/env python3
import sys
import json
import time
import base64
import subprocess
from pathlib import Path

REGION = "eu-north-1"
SECRET_ID = "sabay-bank-dev-db-credentials"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Error: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

print("[*] Locating latest uncorrupted database backup archive...")
backup_files = sorted(Path("backups").glob("*.dump"), key=lambda p: p.stat().st_mtime, reverse=True)
if not backup_files:
    print("[!] No backup dump file found in backups/ directory.")
    sys.exit(1)

latest_dump = backup_files[0]
print(f"[*] Selected Dump: {latest_dump} ({latest_dump.stat().st_size} bytes)")

print("[*] Retrieving RDS connection parameters from Secrets Manager...")
secret_raw = run_cmd(f"aws secretsmanager get-secret-value --secret-id {SECRET_ID} --region {REGION} --query SecretString --output text")
secret = json.loads(secret_raw)

db_host = secret["host"]
db_user = secret["username"]
db_pass = secret["password"]
db_name = secret["database"]

print("[*] Identifying EC2 application host for migration execution...")
instance_id = run_cmd(f"aws ssm describe-instance-information --region {REGION} --query 'InstanceInformationList[0].InstanceId' --output text")
print(f"[*] Target Instance: {instance_id}")

dump_b64 = base64.b64encode(latest_dump.read_bytes()).decode("utf-8")

remote_bash = f"""#!/bin/bash
set -e

echo "{dump_b64}" | base64 -d > /tmp/migration_source.dump

echo "[*] Restoring schema and records into Amazon RDS PostgreSQL..."
docker run --rm \\
  -v /tmp/migration_source.dump:/tmp/source.dump \\
  -e PGPASSWORD="{db_pass}" \\
  postgres:16-alpine \\
  pg_restore -h "{db_host}" -U "{db_user}" -d "{db_name}" --clean --if-exists /tmp/source.dump || true

echo "[*] Synchronizing primary key sequences on Amazon RDS..."
docker run --rm \\
  -e PGPASSWORD="{db_pass}" \\
  postgres:16-alpine \\
  psql -h "{db_host}" -U "{db_user}" -d "{db_name}" -c "
    SELECT setval('customers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM customers));
    SELECT setval('orders_id_seq', (SELECT COALESCE(MAX(id), 1) FROM orders));
  "

echo "[*] Verifying record counts on Amazon RDS..."
docker run --rm \\
  -e PGPASSWORD="{db_pass}" \\
  postgres:16-alpine \\
  psql -h "{db_host}" -U "{db_user}" -d "{db_name}" -c "
    SELECT 
      (SELECT COUNT(*) FROM customers) AS rds_customers,
      (SELECT COUNT(*) FROM orders) AS rds_orders;
  "

rm -f /tmp/migration_source.dump
echo "[✓] Database migration and sequence alignment complete."
"""

b64_wrapper = base64.b64encode(remote_bash.encode("utf-8")).decode("utf-8")
ssm_cmd = f"echo '{b64_wrapper}' | base64 -d | bash"

print("[*] Dispatching migration payload to EC2 via AWS Systems Manager...")
payload = json.dumps({"commands": [ssm_cmd]})
cmd_id = run_cmd(f"aws ssm send-command --region {REGION} --instance-ids '{instance_id}' --document-name 'AWS-RunShellScript' --parameters '{payload}' --query 'Command.CommandId' --output text")

print(f"[*] Migration Task ID: {cmd_id}. Polling execution...")

for attempt in range(24):
    time.sleep(5)
    status_raw = run_cmd(f"aws ssm get-command-invocation --region {REGION} --command-id '{cmd_id}' --instance-id '{instance_id}' --query 'Status' --output text")
    print(f"    Migration status: {status_raw} (elapsed: {(attempt + 1) * 5}s)")
    if status_raw in ["Success", "Failed", "TimedOut"]:
        break

output = run_cmd(f"aws ssm get-command-invocation --region {REGION} --command-id '{cmd_id}' --instance-id '{instance_id}' --query 'StandardOutputContent' --output text")
print("\n" + "=" * 70)
print("  DATABASE MIGRATION EXECUTION OUTPUT")
print("=" * 70)
print(output)
print("=" * 70)
