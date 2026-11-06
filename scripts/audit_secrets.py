import re
import subprocess
from pathlib import Path

root = Path.cwd()
violations = []

# 1. Regex patterns for sensitive data
patterns = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Private Key Header": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Hardcoded AWS Secret": re.compile(r"aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+=]{40}['\"]"),
}

print("=" * 70)
print("  STAGE 1: SCANNING WORKING TREE FILES FOR SENSITIVE TOKENS")
print("=" * 70)

ignored_dirs = {".git", ".venv", "venv", "node_modules"}

for p in root.rglob("*"):
    if p.is_file() and not any(part in ignored_dirs for part in p.parts):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            for name, reg in patterns.items():
                if reg.search(text):
                    violations.append(f"[!] {name} detected in file: {p.relative_to(root)}")
        except Exception:
            pass

if not violations:
    print("[✓] Zero live access keys, secret keys, or private key headers found on disk.")
else:
    for v in violations:
        print(v)

print("\n" + "=" * 70)
print("  STAGE 2: AUDITING GIT COMMIT HISTORY FOR COMMITTED SECRETS")
print("=" * 70)

# Check if terraform.tfstate was ever tracked in git
res = subprocess.run("git log --all --full-history -- '**.tfstate*'", shell=True, capture_output=True, text=True)
if res.stdout.strip():
    print("[!] WARNING: terraform.tfstate detected in historic git commits!")
else:
    print("[✓] terraform.tfstate was NEVER committed to git history.")

# Check for AWS Access Key signatures in commit history
log_scan = subprocess.run("git log -p -S 'AKIA' --all", shell=True, capture_output=True, text=True)
if "AKIA" in log_scan.stdout:
    print("[!] WARNING: String 'AKIA' detected in historical git commit diffs!")
else:
    print("[✓] Zero AWS Access Key signatures detected in git commit history.")

print("=" * 70)
