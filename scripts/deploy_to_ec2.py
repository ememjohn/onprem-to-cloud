#!/usr/bin/env python3
import sys
import json
import time
import base64
import subprocess

REGION = "eu-north-1"
SECRET_ID = "sabay-bank-dev-db-credentials"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Command failed: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

print("[*] Retrieving database connection credentials from AWS Secrets Manager...")
secret_raw = run_cmd(f"aws secretsmanager get-secret-value --secret-id {SECRET_ID} --region {REGION} --query SecretString --output text")
secret = json.loads(secret_raw)

db_host = secret["host"]
db_user = secret["username"]
db_pass = secret["password"]
db_name = secret["database"]
db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"

print("[*] Identifying active EC2 instance managed by Systems Manager...")
instance_id = run_cmd(f"aws ssm describe-instance-information --region {REGION} --query 'InstanceInformationList[0].InstanceId' --output text")
print(f"[*] Target Instance: {instance_id}")

deploy_bash = f"""#!/bin/bash
set -e
rm -rf /home/ec2-user/onprem-to-cloud
git clone https://github.com/ememjohn/onprem-to-cloud.git /home/ec2-user/onprem-to-cloud
cd /home/ec2-user/onprem-to-cloud/app

docker build -t sabay-bank-core:v1 .

docker stop sabay_app 2>/dev/null || true
docker rm sabay_app 2>/dev/null || true

docker run -d \\
  --name sabay_app \\
  --restart unless-stopped \\
  -p 8000:8000 \\
  -e APP_NAME="Sabay Premium Bank Core Ledger (AWS Target)" \\
  -e APP_ENV="aws-target-dev" \\
  -e DATABASE_URL="{db_url}" \\
  sabay-bank-core:v1

sleep 5
curl -s http://localhost:8000/healthz
"""

b64_script = base64.b64encode(deploy_bash.encode("utf-8")).decode("utf-8")
ssm_wrapper = f"echo '{b64_script}' | base64 -d | bash"

print("[*] Sending remote deployment command via AWS Systems Manager...")
payload = json.dumps({"commands": [ssm_wrapper]})
cmd_id = run_cmd(f"aws ssm send-command --region {REGION} --instance-ids '{instance_id}' --document-name 'AWS-RunShellScript' --parameters '{payload}' --query 'Command.CommandId' --output text")

print(f"[*] Command registered with ID: {cmd_id}")
print("[*] Building container image and starting service on EC2. Polling status...")

for attempt in range(24):
    time.sleep(5)
    status_raw = run_cmd(f"aws ssm get-command-invocation --region {REGION} --command-id '{cmd_id}' --instance-id '{instance_id}' --query 'Status' --output text")
    print(f"    Current status: {status_raw} (elapsed: {(attempt + 1) * 5}s)")
    if status_raw in ["Success", "Failed", "TimedOut"]:
        break

output = run_cmd(f"aws ssm get-command-invocation --region {REGION} --command-id '{cmd_id}' --instance-id '{instance_id}' --query 'StandardOutputContent' --output text")
print("\n" + "=" * 70)
print("  REMOTE DEPLOYMENT EXECUTION LOGS")
print("=" * 70)
print(output)
print("=" * 70)
