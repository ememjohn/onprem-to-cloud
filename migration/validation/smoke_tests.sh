#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <TARGET_BASE_URL>"
    echo "Example: $0 http://sabay-bank-dev-alb-123456.eu-north-1.elb.amazonaws.com"
    exit 1
fi

BASE_URL="${1%/}"
FAILURES=0

echo "======================================================================"
echo "  SABAY PREMIUM BANK: AUTOMATED ACCEPTANCE SMOKE TESTS"
echo "  Target Endpoint: ${BASE_URL}"
echo "======================================================================"

# Test 1: Healthcheck Probe
echo -n "[*] Test 1: Healthcheck probe (${BASE_URL}/healthz)... "
HEALTH_RESP=$(curl -s -w "\n%{http_code}\n%{time_total}" "${BASE_URL}/healthz")
HTTP_CODE=$(echo "${HEALTH_RESP}" | tail -n 2 | head -n 1)
LATENCY=$(echo "${HEALTH_RESP}" | tail -n 1)

if [ "${HTTP_CODE}" -eq 200 ]; then
    echo "PASSED (HTTP 200, Latency: ${LATENCY}s)"
else
    echo "FAILED (HTTP ${HTTP_CODE})"
    FAILURES=$((FAILURES + 1))
fi

# Test 2: Customer Account Listing
echo -n "[*] Test 2: Customer account retrieval (${BASE_URL}/api/v1/customers)... "
CUST_COUNT=$(curl -s "${BASE_URL}/api/v1/customers" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

if [ "${CUST_COUNT}" -ge 3 ]; then
    echo "PASSED (Retrieved ${CUST_COUNT} active corporate accounts)"
else
    echo "FAILED (Expected at least 3 accounts, received ${CUST_COUNT})"
    FAILURES=$((FAILURES + 1))
fi

# Test 3: Transaction Ledger Retrieval
echo -n "[*] Test 3: Transaction ledger history (${BASE_URL}/api/v1/orders)... "
TX_COUNT=$(curl -s "${BASE_URL}/api/v1/orders" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

if [ "${TX_COUNT}" -ge 5 ]; then
    echo "PASSED (Retrieved ${TX_COUNT} settled ledger transactions)"
else
    echo "FAILED (Expected at least 5 transactions, received ${TX_COUNT})"
    FAILURES=$((FAILURES + 1))
fi

# Test 4: Transaction Settlement Write
echo -n "[*] Test 4: Live transaction settlement write (POST /api/v1/orders)... "
POST_RESP=$(curl -s -X POST "${BASE_URL}/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "total_amount": 5000.00, "status": "SETTLED"}' 2>/dev/null || echo "{}")

NEW_ID=$(echo "${POST_RESP}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 0))" 2>/dev/null || echo 0)

if [ "${NEW_ID}" -gt 0 ]; then
    echo "PASSED (New transaction settled with ID: ${NEW_ID})"
else
    echo "FAILED (Write failed or sequence collision occurred)"
    FAILURES=$((FAILURES + 1))
fi

echo "======================================================================"
if [ "${FAILURES}" -eq 0 ]; then
    echo "[VERDICT] ALL ACCEPTANCE CRITERIA MET. TARGET STABLE."
    exit 0
else
    echo "[VERDICT] SMOKE TESTS FAILED (${FAILURES} failures detected). TRIGGER ROLLBACK RUNBOOK."
    exit 1
fi
