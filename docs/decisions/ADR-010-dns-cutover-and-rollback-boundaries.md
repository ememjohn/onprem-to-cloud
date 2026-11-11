# Architecture Decision Record 010

## Title
DNS Cutover Mechanism, TTL Strategy, and Post Write Rollback Boundaries

## Status
Accepted

## Context
Sabay Premium Bank required a deterministic traffic switching mechanism to shift public client and interbank traffic from the on premises server to the AWS Application Load Balancer. The banking ledger cannot tolerate split brain writes where both environments accept transactions simultaneously. I had to establish the technical criteria governing DNS time to live settings and rollback execution thresholds.

## Decision Drivers
1. Minimize Client Downtime: Ensure client resolvers pick up the new AWS endpoint within minutes.
2. Prevent Split Brain Data Divergence: Guarantee that on premises write operations cease before cloud write operations begin.
3. Establish an Audited Point of No Return: Define the exact operational threshold where rollback shifts from a simple DNS switch to an active data reconciliation event.
4. Financial Ledger Auditability: Ensure zero dropped transactions if an emergency abort occurs post cutover.

## Evaluated Alternatives

### 1. Immediate DNS Cutover with Default TTL
I rejected immediate cutover with default TTL values. Standard DNS records use a TTL of eighty six thousand four hundred seconds (twenty four hours). Client ISP caches ignore immediate IP changes, causing client traffic to route to the obsolete server for hours.

### 2. Pre Cutover TTL Reduction with Health Checking
I selected pre cutover TTL reduction. Seventy two hours prior to the maintenance window, DNS record TTL is reduced to sixty seconds. Route 53 or Cloudflare evaluates Application Load Balancer target health before routing traffic.

### 3. Naive DNS Reversal Rollback
I rejected naive DNS reversal. Flipping DNS back to on premises after the cloud target database has accepted live transactions causes silent data loss.

## The Point of No Return Rule
1. Before Target Writes: If preflight validation fails before the cloud database accepts live writes, rollback is a simple DNS reversal.
2. After Target Writes: The moment the cloud database accepts its first live transaction, rollback via simple DNS reversal is strictly prohibited. Any abort requires executing the Data Reconciliation Runbook, exporting new cloud transactions, and ingesting them into the on premises database before shifting traffic.

## My Decision
I chose pre cutover TTL reduction to sixty seconds combined with the Point of No Return rule. I authored migration/cutover/preflight.sh and migration/cutover/rollback-runbook.md to automate pre cutover checks and govern post write reverse data reconciliation.

## Consequences

### Positive
1. Sixty second TTL ensures rapid client cache eviction during maintenance windows.
2. Zero dropped transactions or ledger discrepancies during an emergency abort.
3. Clean, unambiguous operational boundaries for site reliability engineers.

### Negative
1. Low TTL settings temporarily increase DNS query resolution volume during the migration week.
2. Reverse data reconciliation requires executing custom SQL backport scripts before reversing traffic.