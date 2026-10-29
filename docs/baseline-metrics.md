# Baseline Verification and Performance Metrics Report

## Test Execution Matrix
| Test Identifier | Verified Flow | Input Payload / Condition | Observed Response | Execution Verdict |
| :--- | :--- | :--- | :--- | :--- |
| TC-HEALTH-01 | GET /healthz | Valid database socket available | HTTP 200 (database: connected) | PASSED |
| TC-CUST-02 | GET /api/v1/customers | Standard query | HTTP 200, Array count: 3 | PASSED |
| TC-ORD-03 | GET /api/v1/orders | Standard query | HTTP 200, Array count: 5 | PASSED |
| TC-ORD-04 | POST /api/v1/orders | customer_id: 1, total_amount: 99.99 | HTTP 201, Generated Order ID | PASSED |
| TC-PERSIST-05 | Container Recreate | docker compose down && up | Zero data loss, all 5 orders intact | PASSED |

## Seed Data Inventory
| Entity ID | Entity Classification | Core Attributes | Migration Verification Checksum |
| :--- | :--- | :--- | :--- |
| Customer 1 | Corporate Client | Acme Industrial Supplies (procurement@acme-industrial.example) | Deterministic Seed Baseline |
| Customer 2 | Corporate Client | Globex Logistics Corp (ops@globex-logistics.example) | Deterministic Seed Baseline |
| Customer 3 | Corporate Client | Soylent Foods Ltd (supplychain@soylent-foods.example) | Deterministic Seed Baseline |
| Order 1 | Settled Transaction | Customer 1, Amount: 1450.50 USD, Status: COMPLETED | Deterministic Seed Baseline |
| Order 2 | In Flight Transaction | Customer 1, Amount: 320.00 USD, Status: SHIPPED | Deterministic Seed Baseline |
| Order 3 | In Flight Transaction | Customer 2, Amount: 8920.00 USD, Status: PROCESSING | Deterministic Seed Baseline |
| Order 4 | New Transaction | Customer 3, Amount: 450.75 USD, Status: PENDING | Deterministic Seed Baseline |
| Order 5 | Runtime Test Transaction | Customer 2, Amount: 750.00 USD, Status: PENDING | Persistence Drill Verified Record |
