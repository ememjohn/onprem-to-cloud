#!/usr/bin/env python3
import json
import time
import subprocess

def run(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

print("=" * 70)
print("  CHECK 1: RDS DATABASE LIVE STATUS AND SECURITY GROUPS")
print("=" * 70)
db_info_raw = run("aws rds describe-db-instances --region eu-north-1 --db-instance-identifier sabay-bank-dev-postgres --query 'DBInstances[0]' --output json")
try:
    db_info = json.loads(db_info_raw)
    endpoint = db_info.get("Endpoint", {}).get("Address")
    status = db_info.get("DBInstanceStatus")
    vpc_sgs = [sg["VpcSecurityGroupId"] for sg in db_info.get("VpcSecurityGroups", [])]
    print(f"Endpoint:        {endpoint}")
    print(f"Status:          {status}")
    print(f"Security Groups: {vpc_sgs}")
except Exception as e:
    print("Could not inspect RDS:", e)

print("\n" + "=" * 70)
print("  CHECK 2: SECRETS MANAGER PARAMETERS")
print("=" * 70)
sec_raw = run("aws secretsmanager get-secret-value --secret-id sabay-bank-dev-db-credentials --region eu-north-1 --query SecretString --output text")
try:
    sec = json.loads(sec_raw)
    print(f"Host:     {sec.get('host')}")
    print(f"Database: {sec.get('database')}")
    print(f"Username: {sec.get('username')}")
    print(f"Password: (Length: {len(sec.get('password', ''))})")
except Exception as e:
    print("Could not inspect secret:", e)

print("\n" + "=" * 70)
print("  CHECK 3: EC2 TO RDS NETWORK REACHABILITY VIA SSM")
print("=" * 70)
inst_id = run("aws ssm describe-instance-information --region eu-north-1 --query 'InstanceInformationList[0].InstanceId' --output text")
print(f"Target EC2 Instance: {inst_id}")

test_script = f"""
echo "=== TCP Socket Probe (EC2 to {endpoint}:5432) ==="
python3 -c "import socket; s = socket.socket(); s.settimeout(3); res = s.connect_ex(('{endpoint}', 5432)); print('PORT 5432 STATUS (0 is OPEN):', res); s.close()"
echo "=== Last 15 Lines of Application Container Logs ==="
docker logs sabay_app --tail 15
"""

cmd_payload = json.dumps({"commands": [test_script]})
cmd_id = run(f"aws ssm send-command --region eu-north-1 --instance-ids '{inst_id}' --document-name 'AWS-RunShellScript' --parameters '{cmd_payload}' --query 'Command.CommandId' --output text")

time.sleep(5)
logs = run(f"aws ssm get-command-invocation --region eu-north-1 --command-id '{cmd_id}' --instance-id '{inst_id}' --query 'StandardOutputContent' --output text")
print(logs)
print("=" * 70)
