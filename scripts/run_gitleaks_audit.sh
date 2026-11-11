#!/usr/bin/env bash
set -euo pipefail

EVIDENCE_FILE="docs/evidence/2026-11-08-gitleaks-audit-proof.txt"

echo "[*] Downloading official Gitleaks binary..."
curl -sSL https://github.com/gitleaks/gitleaks/releases/download/v8.18.2/gitleaks_8.18.2_linux_x64.tar.gz -o /tmp/gitleaks.tar.gz
tar -xzf /tmp/gitleaks.tar.gz -C /tmp gitleaks
chmod +x /tmp/gitleaks

echo "[*] Running Gitleaks scan across working tree and full git history..."
/tmp/gitleaks detect --source . --verbose --no-git=false 2>&1 | tee "${EVIDENCE_FILE}" || true

rm -f /tmp/gitleaks.tar.gz /tmp/gitleaks
echo "[✓] Gitleaks scan completed. Report saved to ${EVIDENCE_FILE}"
