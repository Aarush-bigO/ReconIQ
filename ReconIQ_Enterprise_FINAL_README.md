# ReconIQ Enterprise
## AI Finance Control Center for Payment, Settlement & Ledger Reconciliation

> **Razorpay Buildathon — Track 04: AI Finance Controller**
>
> **Tagline:** **Reconcile what you can prove. Explain what you can't.**
>
> **Core principle:** **Deterministic systems decide. AI explains.**

ReconIQ Enterprise is a finance-operations control center designed for merchants and finance teams that need to reconcile payment, settlement, accounting-ledger, and bank data across inconsistent sources.

The platform ingests financial records, normalizes source-specific identifiers, generates and scores candidate matches using probabilistic record linkage, applies deterministic reconciliation policies, measures performance against ground truth, routes uncertainty into an exception workbench, explains exceptions with bounded AI, and records every financial decision in a tamper-evident audit trail.

The product should look and behave like an **enterprise fintech operations console**, not like a student CSV dashboard or a generic AI chatbot.

---

# 1. PRODUCT VISION

ReconIQ Enterprise is the control layer between payment infrastructure and finance operations.

```text
                    PAYMENT ECOSYSTEM
                           │
             ┌─────────────┼─────────────┐
             │             │             │
          Payments     Settlements    Webhooks
             │             │             │
             └─────────────┼─────────────┘
                           │
                    Razorpay Adapter
                           │
                           ▼
                 ┌───────────────────┐
                 │  ReconIQ Core     │
                 │                   │
                 │ Normalize         │
                 │ Match             │
                 │ Reconcile         │
                 │ Measure           │
                 │ Explain           │
                 │ Audit             │
                 └─────────┬─────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Transactions   Exceptions    Settlements
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                  FINANCE CONTROL CENTER
```

The objective is not merely to find matching strings.

The objective is to create a measurable finance-control workflow:

```text
INGEST
  ↓
NORMALIZE
  ↓
MATCH
  ↓
RECONCILE
  ↓
MEASURE
  ↓
EXPLAIN
  ↓
REVIEW
  ↓
AUDIT
  ↓
REPORT
```

---

# 2. THE CORE PROBLEM

A merchant can have multiple records for the same economic event:

```text
Razorpay payment
Razorpay settlement
Merchant accounting ledger
Bank credit
```

Those records may differ because of:

- different identifiers
- UTR/reference prefixes
- spelling or formatting variations
- settlement delays
- duplicate records
- one-to-many settlements
- fees and tax
- partial settlements
- missing exports
- inconsistent date formats
- currency representations
- source-specific status values

A naive implementation:

```text
reference == reference
AND
amount == amount
```

will fail on real-world data.

ReconIQ therefore combines:

### 1. Canonical normalization

Preserve source data while creating controlled comparison fields.

### 2. Probabilistic record linkage

Use Splink to estimate the strength of evidence that records represent the same event.

### 3. Deterministic reconciliation policy

Convert evidence into:

```text
AUTO_MATCH
MANUAL_REVIEW
UNRESOLVED
```

### 4. Measured evaluation

Compare predicted relationships against hidden ground truth.

### 5. Exception management

Never force uncertain records into successful matches.

### 6. AI narration

Use an LLM only to explain structured evidence.

### 7. Auditability

Record decisions in a tamper-evident hash chain.

---

# 3. PRODUCT POSITIONING

## One sentence

**ReconIQ Enterprise automatically reconciles messy payment, settlement, merchant-ledger and bank records, measures what it can prove, surfaces uncertain transactions for human review, explains exceptions with bounded AI, and preserves a tamper-evident audit trail for every decision.**

## Pitch

> Finance teams should not have to choose between automation and trust. ReconIQ automates repetitive reconciliation while keeping financial decisions deterministic, publishing measurable performance, surfacing honest exceptions, and using AI only to explain evidence.

## Product promise

```text
FASTER RECONCILIATION
        +
MEASURABLE ACCURACY
        +
HONEST EXCEPTIONS
        +
AUDITABILITY
        +
AI EXPLANATION
```

## Closing line

> **The AI explains the books. It never invents them.**

---

# 4. RAZORPAY-FIRST ARCHITECTURE

ReconIQ must treat Razorpay as a genuine payment-data source.

Do not make a fake “Razorpay” tab containing static demo values.

Build a provider abstraction:

```text
PaymentProviderAdapter
        │
        ├── RazorpayAdapter
        │
        └── SyntheticAdapter
```

The reconciliation engine must be independent of the payment provider.

That means:

```text
Razorpay API
     ↓
Razorpay Adapter
     ↓
Canonical Model
     ↓
Reconciliation Core
```

and:

```text
Synthetic CSV
     ↓
Synthetic Adapter
     ↓
Canonical Model
     ↓
Reconciliation Core
```

Both paths must use exactly the same reconciliation engine.

---

# 5. OFFICIAL RAZORPAY SURFACES

Use official Razorpay documentation as the source of truth for integration semantics.

Relevant surfaces include:

- Payments
- Orders
- Settlements
- Settlement Recon
- Settlement Reports
- Webhooks

Official references:

```text
https://razorpay.com/

https://razorpay.com/docs/api/

https://razorpay.com/docs/payments/settlements/apis/

https://razorpay.com/docs/api/settlements/fetch-recon/

https://razorpay.com/docs/payments/settlements/dashboard/

https://razorpay.com/docs/webhooks/

https://github.com/razorpay

https://github.com/razorpay/razorpay-node
```

Use Razorpay test mode/sandbox data wherever supported and clearly label the environment.

Never imply production connectivity when the demo is using synthetic/test data.

---

# 6. RAZORPAY INGESTION

Create:

```text
ingestion/razorpay_adapter.py
```

Responsibilities:

```text
authenticate
fetch data
validate response
map source fields
preserve source IDs
normalize data
return canonical records
```

Suggested interface:

```python
class PaymentProviderAdapter:
    def fetch_payments(self, start, end):
        ...

    def fetch_settlements(self, start, end):
        ...

    def fetch_settlement_recon(self, start, end):
        ...
```

Implementation:

```python
class RazorpayAdapter(PaymentProviderAdapter):
    ...
```

Keep provider-specific code outside the matching engine.

---

# 7. WEBHOOK DESIGN

Where practical, support payment/settlement event ingestion through a webhook endpoint.

Conceptual flow:

```text
Razorpay
   │
   │ webhook
   ▼
POST /webhooks/razorpay
   │
   ▼
signature verification
   │
   ▼
event normalization
   │
   ▼
idempotency check
   │
   ▼
canonical transaction event
   │
   ▼
reconciliation queue
```

Never trust webhook payloads without signature verification.

Webhook events should be idempotent.

Store:

```text
event_id
event_type
provider
received_at
payload_hash
processing_status
```

---

# 8. CANONICAL DATA MODEL

Every source gets mapped into a canonical schema.

Recommended fields:

```text
canonical_id
source
source_record_id
source_reference
reference_core
amount_minor
currency
event_time
transaction_type
status
payment_id
order_id
settlement_id
utr
fee_minor
tax_minor
adjustment_minor
metadata
created_at
```

Example:

```json
{
  "canonical_id": "txn_0001042",
  "source": "razorpay",
  "source_record_id": "pay_xxxxx",
  "source_reference": "PAY-82917",
  "reference_core": "82917",
  "amount_minor": 425000,
  "currency": "INR",
  "event_time": "2026-08-18T10:32:00Z",
  "transaction_type": "payment",
  "status": "captured",
  "payment_id": "pay_xxxxx",
  "order_id": "order_xxxxx",
  "settlement_id": null,
  "utr": null,
  "fee_minor": 0,
  "tax_minor": 0,
  "adjustment_minor": 0,
  "metadata": {}
}
```

Use integer minor units such as paise for authoritative monetary computation.

Do not use floating point for financial arithmetic.

---

# 9. NORMALIZATION

Never overwrite the raw source value.

Keep:

```text
source_reference
```

and derive:

```text
reference_core
```

Example:

```text
Razorpay:
PAY-82917

Bank:
UTR-82917

Ledger:
payment_82917
```

becomes:

```text
source_reference      reference_core
-------------------------------------
PAY-82917             82917
UTR-82917             82917
payment_82917         82917
```

The normalization rules must be deterministic and tested.

Keep a normalization trace:

```json
{
  "raw": "UTR-82917",
  "normalizer": "strip_known_prefix",
  "normalized": "82917"
}
```

---

# 10. THE REAL BUILD CHALLENGE

During development, bank references used a UTR-style prefix while settlement/ledger records used a PAY-style identifier.

Exact string comparison therefore caused legitimate cross-source relationships to appear unmatched.

The fix:

```text
raw reference
      ↓
controlled normalization
      ↓
reference_core
      ↓
probabilistic matching
```

This is a genuine engineering challenge.

Application-safe wording:

> “We encountered a cross-source identifier normalization issue where equivalent transactions used different reference conventions. We preserved the raw identifiers and introduced a canonical comparison field rather than weakening the reconciliation rules or hard-coding source-specific matches.”

Do not call this a Razorpay defect.

---

# 11. RECONCILIATION ENGINE

Use a three-stage architecture.

## Stage 1 — Candidate generation

Reduce unnecessary comparisons.

Potential deterministic constraints:

```text
same currency
amount within configured tolerance
date within configured window
same reference_core where available
```

Candidate generation must never create the final financial decision.

---

## Stage 2 — Probabilistic linkage

Use:

### Splink

https://github.com/moj-analytical-services/splink

Splink is the primary technical reference for probabilistic record linkage.

Potential comparison features:

```text
amount agreement
date proximity
reference similarity
reference_core agreement
payment/order identifier
settlement identifier
currency
transaction type
```

Use Splink's actual pipeline.

Do not replace it with a mocked score.

---

## Stage 3 — Decision policy

The reconciliation policy converts linkage evidence into an operational decision.

Example:

```text
probability >= auto_match_threshold
and no hard contradiction
        ↓
AUTO_MATCH

review_threshold <= probability < auto_match_threshold
        ↓
MANUAL_REVIEW

probability < review_threshold
        ↓
UNRESOLVED
```

Recommended initial configuration:

```text
AUTO_MATCH_THRESHOLD = 0.95
REVIEW_THRESHOLD = 0.70
DATE_TOLERANCE_DAYS = 3
```

These defaults must be configurable and benchmarked.

---

# 12. NO BLACK-BOX FINANCIAL DECISIONS

For each match, expose evidence.

Example:

```text
MATCH
98.7% confidence

Amount                 1.00
Reference similarity   0.96
Date proximity         0.91
Currency               PASS
Window                 PASS

Ledger      LED-1042
Razorpay    pay_xxxxx
Bank        UTR-82917
```

The user must be able to click:

```text
[ Why did this match? ]
```

and see the underlying comparison evidence.

---

# 13. 360-DEGREE TRANSACTION VIEW

Every transaction gets a detailed view.

```text
Transaction PAY-82917

                   ₹4,250
                  RECONCILED

┌────────────────┬────────────────┬────────────────┐
│ RAZORPAY       │ LEDGER         │ BANK           │
├────────────────┼────────────────┼────────────────┤
│ pay_xxxxx      │ LED-1042       │ UTR-82917      │
│ ₹4,250         │ ₹4,250         │ ₹4,250         │
│ 18 Aug         │ 18 Aug         │ 20 Aug         │
│ Captured       │ Posted         │ Credited       │
└────────────────┴────────────────┴────────────────┘

MATCH EVIDENCE

Amount             ✓
Reference          96%
Date               91%
Currency           ✓
Settlement Window  ✓

Decision             MATCH
Confidence           98.7%

[ Why did this match? ]
[ View Audit Trail ]
[ Explain ]
[ Export Evidence ]
```

---

# 14. EXCEPTION MODEL

Never force every record into a match.

Core reason codes:

```text
MISSING_COUNTERPART
AMBIGUOUS_MATCH
REFERENCE_MISMATCH
DATE_DRIFT
DUPLICATE
PARTIAL_SETTLEMENT
FEE_DIFFERENCE
CURRENCY_ISSUE
UNCLASSIFIED
```

Each exception must include deterministic evidence.

Example:

```json
{
  "exception_id": "exc_00014",
  "transaction_id": "LED-1042",
  "reason_code": "MISSING_COUNTERPART",
  "severity": "HIGH",
  "amount_minor": 1480000,
  "candidate_count": 0,
  "window_days": 3,
  "status": "OPEN"
}
```

---

# 15. EXCEPTION WORKBENCH

This should be one of the most polished screens.

```text
EXCEPTION WORKBENCH

14 Open Exceptions                         Filters ▼

HIGH
Missing counterpart                    ₹14,800
Ledger: LED-1042                      2h ago

──────────────────────────────────────────────

Exception #1042

₹14,800
MISSING COUNTERPART

SOURCE RECORD
Ledger: LED-1042
Reference: payment_8821
Date: Aug 25

COUNTERPART SEARCH
Razorpay candidates: 0
Bank candidates: 0

CONFIGURATION
Window: 3 days
Threshold: 0.95

AI EXPLANATION

“No corresponding settlement or bank
record was identified within the configured
reconciliation window.”

RECOMMENDED ACTION

Review delayed settlement exports or
verify whether the source transaction
was omitted.

[ Assign ]
[ Mark Reviewed ]
[ Escalate ]
[ View Audit ]
```

Any status-changing action must be audited.

---

# 16. PARTIAL SETTLEMENTS

Do not treat every amount difference as a missing transaction.

Example:

```text
Gross payment       ₹10,000
Fee                    ₹250
Tax                     ₹45
Adjustment              ₹5
--------------------------------
Expected settlement   ₹9,700
```

The system should reconcile based on the configured settlement model.

For one-to-many cases:

```text
payment ₹10,000
       │
       ├── settlement A ₹7,000
       └── settlement B ₹3,000
```

Either:

```text
support one-to-many reconciliation
```

or:

```text
PARTIAL_SETTLEMENT → MANUAL_REVIEW
```

Never manipulate the data simply to raise the match rate.

---

# 17. DUPLICATE DETECTION

Detect possible duplicates independently of ordinary linkage.

Signals:

```text
same source reference
same amount
same event date
same normalized reference
same payment/order ID
```

Display:

```text
DUPLICATE SUSPECTED

3 records appear to represent
the same source event.

[ Compare Records ]
```

Do not automatically delete anything.

---

# 18. SETTLEMENT OPERATIONS

Settlements are a first-class product domain.

Page:

```text
Settlements
```

Display:

```text
Expected
Received
Variance
Reconciled
Pending
```

Example:

```text
Expected             ₹12.84L
Bank received        ₹12.31L
Variance             ₹53,420
Reconciled           95.8%
```

Settlement table:

```text
Settlement ID
Settlement date
Gross
Fees
Tax
Adjustments
Net
Bank credit
UTR
Status
```

Clicking opens the settlement detail timeline.

---

# 19. SETTLEMENT DETAIL

```text
SETL_1042

RECONCILED

Timeline

Aug 24  Payment captured
Aug 24  Payment included
Aug 25  Settlement processed
Aug 25  Bank credit received
Aug 26  Reconciliation completed

FINANCIAL BREAKDOWN

Gross                 ₹125,000
Fees                    ₹2,250
Tax                       ₹405
Adjustments               ₹500
Net                    ₹121,845

Bank credit            ₹121,845

Variance                     ₹0
```

Use actual source fields when connected.

The numbers above are UI examples only.

---

# 20. OVERVIEW — FINANCE CONTROL CENTER

The Overview page should feel like the command center of a finance organization.

Header:

```text
ReconIQ Enterprise
Finance Control Center

Connected: Razorpay Test Mode ●
Last Sync: 2 minutes ago
```

Primary KPI cards:

```text
Records Processed
200

Auto-Matched
184

Match Rate
92%

Reconciled Value
₹8.69L

Open Exceptions
14

Audit
VERIFIED
```

Do not hard-code the reported development numbers.

The UI must call the API.

---

# 21. OVERVIEW INFORMATION HIERARCHY

Recommended sections:

```text
1. Financial Health
2. Reconciliation Health
3. Exception Risk
4. Settlement Timeline
5. Data Quality
6. AI Operations
7. Recent Runs
```

Example:

```text
┌──────────────────────────────────────────────────────────────┐
│ FINANCIAL HEALTH                                             │
│                                                              │
│ Processed      Reconciled      Variance       Exceptions     │
│ ₹12.84L        ₹12.31L         ₹53,420        14             │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────┬───────────────────────────────┐
│ RECONCILIATION HEALTH        │ EXCEPTION RISK                │
│                              │                               │
│ 92% matched                 │ ₹42,800 under review         │
│ ███████████████████░░       │ 6 high priority               │
└──────────────────────────────┴───────────────────────────────┘

┌──────────────────────────────┬───────────────────────────────┐
│ SETTLEMENT TIMELINE           │ AI CONTROL ROOM              │
│                              │                               │
│ Aug 24 ✓                     │ 14 exceptions analyzed       │
│ Aug 25 ✓                     │ 3 require attention          │
│ Aug 26 ⚠                     │ 0 auto-resolved              │
└──────────────────────────────┴───────────────────────────────┘
```

---

# 22. AI CONTROL ROOM

Razorpay increasingly presents AI as part of its broader product direction.

ReconIQ should therefore have meaningful AI functionality without turning the core financial decisions over to an LLM.

The AI Control Room should summarize deterministic findings.

Example:

```text
AI CONTROL ROOM

Today's financial anomalies

14 exceptions detected
3 high priority
8 routine
3 ambiguous

Suggested reviews

• Missing counterpart: ₹14,800
• Repeated reference mismatch
• Settlement variance: SETL_8293
• Duplicate payment cluster

[ Open Exception Queue ]
```

The AI never performs an unapproved financial action.

---

# 23. AI EXPLANATION CONTRACT

LLM input must be structured evidence only.

Example input:

```json
{
  "decision": "UNRESOLVED",
  "reason_code": "MISSING_COUNTERPART",
  "amount_minor": 1480000,
  "currency": "INR",
  "candidate_count": 0,
  "search_window_days": 3
}
```

Expected output:

```json
{
  "explanation": "No corresponding settlement or bank record was identified within the configured reconciliation window.",
  "recommended_action": "Review delayed settlements or verify that the source transaction was exported."
}
```

Validate the response with a schema.

---

# 24. AI SAFETY BOUNDARY

LLM cannot:

```text
change amount
change currency
change decision
change confidence
create a match
delete an exception
invent IDs
invent evidence
modify settlement state
write directly to ledger tables
```

The LLM output should be presentation-level only.

Architecture:

```text
Deterministic result
       ↓
Evidence builder
       ↓
JSON schema
       ↓
LLM
       ↓
JSON validation
       ↓
Display
```

If an API key is missing:

```text
rule-based explanation fallback
```

The core application remains functional.

---

# 25. DECISION TRACE

Add a dedicated feature:

## “How did ReconIQ decide?”

Show:

```text
INPUT
  ↓
NORMALIZATION
  ↓
CANDIDATE GENERATION
  ↓
SPLINK COMPARISONS
  ↓
PROBABILITY
  ↓
RECONCILIATION POLICY
  ↓
DECISION
  ↓
EXCEPTION / MATCH
  ↓
AI EXPLANATION
  ↓
AUDIT EVENT
```

This is a key trust feature.

---

# 26. DATA QUALITY CENTER

Create:

```text
Data Quality
```

Show each source's health.

Example:

```text
RAZORPAY

Schema                 ✓
Required fields        ✓
Currency consistency   ✓
Reference formats      ⚠ 7 variants

BANK

Schema                 ✓
Required fields        ✓
UTR formatting         ⚠ 12 variants

MERCHANT LEDGER

Schema                 ✓
Required fields        ✓
Duplicates              ⚠ 4
```

Each warning should link to the relevant records.

---

# 27. AUDIT TRAIL

Every important event should be recorded.

Recommended event:

```json
{
  "event_id": "evt_001042",
  "run_id": "recon_001",
  "record_id": "LED-1042",
  "action": "MATCH_DECISION",
  "decision": "MATCH",
  "confidence": 0.987,
  "reason_code": "AMOUNT_DATE_REFERENCE",
  "timestamp": "2026-08-27T18:21:00Z",
  "previous_hash": "abc123...",
  "current_hash": "def456..."
}
```

Hash:

```text
event 1
  │
 hash1
  │
event 2 + hash1
  │
 hash2
  │
event 3 + hash2
  │
 hash3
```

Verification:

```text
AUDIT CHAIN
✓ VERIFIED

Events: 200
Last verified: 18:21:03
```

Tamper test:

```text
Clean chain
    → PASS

Modify event #104
    → FAIL
```

Call it:

> **tamper-evident hash-chained audit logging**

Do not call it blockchain.

---

# 28. AUDIT EVENT TYPES

At minimum:

```text
INGESTED
NORMALIZED
MATCH_PROPOSED
MATCH_CONFIRMED
MANUAL_REVIEW_STARTED
EXCEPTION_CREATED
EXCEPTION_REVIEWED
EXPLANATION_GENERATED
REPORT_EXPORTED
CONFIG_CHANGED
```

Any state-changing action must create an event.

---

# 29. REPORTING

Reports should include:

```text
Reconciliation summary
Settlement summary
Exception summary
Threshold analysis
Audit verification
```

Export:

```text
CSV
JSON
PDF-ready report
```

The PDF/print representation should be professional and suitable for a finance review.

---

# 30. EVALUATION LAB

Create a dedicated:

```text
Evaluation Lab
```

This is important because the Track 04 value proposition depends on measured performance rather than a cherry-picked demo.

Run thresholds:

```text
0.80
0.85
0.90
0.95
0.97
0.99
```

Show:

```text
Threshold     Precision     Recall     Match Rate
--------------------------------------------------
0.80          X             X          X
0.85          X             X          X
0.90          X             X          X
0.95          X             X          X
0.97          X             X          X
0.99          X             X          X
```

All X values must come from actual benchmark runs.

Show the chosen operating point and why:

```text
Recommended threshold:
0.95

Reason:
High precision with manageable
manual-review volume.
```

---

# 31. GROUND TRUTH

Use a dedicated ground-truth data structure.

Example:

```json
{
  "ledger_id": "LED-1042",
  "true_matches": [
    "PAY-82917",
    "BANK-82917"
  ]
}
```

Do not expose it to the production matcher.

Architecture:

```text
RAW DATA
   │
   └──> MATCHER
          │
          └──> PREDICTIONS

GROUND TRUTH
   │
   └──> EVALUATOR

PREDICTIONS + GROUND TRUTH
             ↓
       PRECISION / RECALL
```

This prevents benchmark leakage.

---

# 32. SYNTHETIC DATA GENERATOR

Create:

```text
data/synthetic_gen.py
```

Use a fixed seed.

Target:

```text
200+ records
```

Include:

```text
normal matches
reference typos
UTR/PAY prefix differences
date drift
duplicate candidates
partial settlements
fee differences
missing counterparts
ambiguous cases
currency formatting issues
```

Each scenario must be intentional.

Example distribution:

```text
120 normal
20 reference variants
15 date drift
10 duplicates
10 fee differences
10 partial settlements
10 missing counterparts
5 ambiguous
```

These are recommended test categories, not required exact proportions.

---

# 33. WHY 200+ RECORDS

The system needs a batch large enough to demonstrate that it does not succeed merely because of a few hand-picked records.

Recommended demo:

```text
200 records
```

Then show benchmark scalability:

```text
50 records
100 records
200 records
```

Measure processing time.

Do not fabricate throughput.

---

# 34. BENCHMARK ARTIFACT

Create:

```text
benchmarks/run_benchmark.py
benchmarks/results/
```

Every benchmark result should record:

```text
dataset size
seed
threshold
Splink version
Python version
git commit SHA
timestamp
precision
recall
match rate
processing duration
reconciled value
exception count
```

Example result:

```json
{
  "dataset_size": 200,
  "seed": 42,
  "threshold": 0.95,
  "precision": 0.0,
  "recall": 0.0,
  "match_rate": 0.0,
  "processing_seconds": 0.0
}
```

Those values are placeholders for code schema only.

---

# 35. CURRENT DEVELOPMENT RESULTS

Previously reported development run:

```text
Match rate:        92%
Reconciled value:  ₹869,816.61
Exceptions:        14

At threshold 0.95:
Precision:         1.000
Recall:            0.841
```

These are development-run results.

Before the final public release:

```text
regenerate benchmark
save results
verify ground truth
verify metrics
record commit SHA
```

Only then publish the values in the README.

Never call:

```text
92% match rate
```

“92% accuracy.”

---

# 36. DATABASE MODEL

Use PostgreSQL.

Recommended tables:

```text
reconciliation_runs
transactions
settlements
match_candidates
matches
exceptions
audit_events
webhook_events
explanation_requests
benchmark_runs
source_configs
```

### transactions

```text
id
canonical_id
source
source_record_id
source_reference
reference_core
amount_minor
currency
event_time
transaction_type
status
payment_id
order_id
settlement_id
utr
fee_minor
tax_minor
adjustment_minor
metadata
created_at
```

### reconciliation_runs

```text
id
run_id
started_at
completed_at
threshold
records_processed
auto_matched
manual_review
unresolved
match_rate
reconciled_value_minor
processing_ms
status
```

### matches

```text
id
run_id
left_transaction_id
right_transaction_id
probability
decision
reason_code
created_at
```

### exceptions

```text
id
run_id
transaction_id
reason_code
severity
status
evidence_json
ai_explanation
created_at
reviewed_at
```

### audit_events

```text
id
event_id
run_id
record_id
action
decision
confidence
reason_code
payload_hash
previous_hash
current_hash
created_at
```

---

# 37. API DESIGN

FastAPI endpoints:

```text
GET  /health

POST /reconcile
POST /reconcile/upload

GET  /reports/latest
GET  /reports/{run_id}

GET  /transactions
GET  /transactions/{id}

GET  /exceptions
GET  /exceptions/{id}
POST /exceptions/{id}/review

GET  /settlements
GET  /settlements/{id}

GET  /audit
GET  /audit/verify

POST /exceptions/{id}/explain

POST /webhooks/razorpay
```

Use Pydantic models for all externally visible payloads.

---

# 38. FRONTEND INFORMATION ARCHITECTURE

Primary navigation:

```text
Overview
Reconciliation
Transactions
Settlements
Exceptions
Data Quality
AI Control Room
Audit Trail
Reports
Evaluation Lab
Settings
```

Global search:

```text
Search payments, settlements,
UTRs, transaction IDs...
```

Search should support:

```text
PAY-82917
UTR-82917
SETL_8291
LED-1042
```

---

# 39. TRANSACTION LIST

Columns:

```text
Status
Transaction ID
Reference
Amount
Source
Date
Settlement
Confidence
```

Filters:

```text
All
Matched
Review
Unresolved
Duplicate
Partial
Date Drift
```

Support:

```text
pagination
sorting
filter persistence
column visibility
CSV export
```

---

# 40. SETTLEMENT LIST

Columns:

```text
Settlement
Date
Gross
Fee
Tax
Adjustment
Net
Bank Credit
Variance
Status
UTR
```

Statuses:

```text
RECONCILED
PARTIAL
PENDING
VARIANCE
EXCEPTION
```

---

# 41. REPORTS

Provide:

### Reconciliation report

```text
run ID
period
sources
records
matches
review
exceptions
metrics
```

### Settlement report

```text
gross
fees
tax
adjustments
net
bank credit
variance
```

### Exception report

```text
reason
amount
source
priority
status
```

### Audit report

```text
chain status
events
verification timestamp
```

---

# 42. ROLE-READY DESIGN

Architecture should be role-ready even if authentication is lightweight for the hackathon.

Roles:

```text
Finance Analyst
Finance Admin
Auditor
```

### Finance Analyst

```text
run reconciliation
review exceptions
export reports
```

### Finance Admin

```text
all analyst actions
configure thresholds
manage integrations
change policies
```

### Auditor

```text
view transactions
view evidence
verify audit chain
export audit reports
```

Every permission-sensitive action should eventually map to an authorization layer.

---

# 43. SETTINGS

Settings page:

```text
Providers
Reconciliation Policy
Thresholds
Settlement Rules
Notifications
AI Settings
Audit
```

Example:

```text
Auto-match threshold       0.95
Review threshold            0.70
Date tolerance              3 days
Amount tolerance            ₹1.00
Currency                    INR
```

Changing configuration must create:

```text
CONFIG_CHANGED
```

audit event.

---

# 44. DESIGN SYSTEM

The interface should look like a serious enterprise fintech product.

### Visual principles

```text
data-first
clean
dense
professional
high-signal
minimal decoration
clear hierarchy
```

Use:

```text
neutral background
white cards
dark typography
subtle borders
restrained shadows
Razorpay-inspired red accent
semantic green/amber/red statuses
```

Do not create a pixel-for-pixel Razorpay clone.

Do not overuse:

```text
glassmorphism
large gradients
neon colors
floating blobs
gaming-style UI
AI sci-fi effects
```

Enterprise fintech should feel precise, not flashy.

---

# 45. COMPONENT LIBRARY

Build reusable components:

```text
KPI Card
Status Badge
Data Table
Filter Bar
Date Range Picker
Evidence Drawer
Transaction Timeline
Exception Drawer
Metric Card
Confidence Meter
Audit Chain Viewer
AI Explanation Card
Settlement Breakdown
Benchmark Chart
Search Command Menu
```

Use consistent spacing, typography and interaction behavior.

---

# 46. ACCESSIBILITY

Minimum:

```text
keyboard navigation
semantic buttons
visible focus states
accessible labels
sufficient contrast
table headers
error messages
```

Do not make core information dependent only on color.

---

# 47. OBSERVABILITY

Show system health:

```text
API             HEALTHY
DATABASE        HEALTHY
RAZORPAY        CONNECTED / NOT CONFIGURED
LLM             AVAILABLE / FALLBACK
AUDIT           VERIFIED
```

Store reconciliation operational metrics:

```text
run ID
duration
records
candidate count
matches
exceptions
threshold
```

---

# 48. ERROR HANDLING

Never silently fail.

Examples:

### Razorpay unavailable

```text
Razorpay integration unavailable.

Use Demo Data
```

### LLM unavailable

```text
AI explanation unavailable.
Showing deterministic fallback.
```

### Audit verification fails

```text
CRITICAL

Audit chain verification failed.

Do not treat the affected
record set as trusted until reviewed.
```

This should be visually prominent.

---

# 49. SECURITY

Never commit:

```text
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
OPENAI_API_KEY
DATABASE_PASSWORD
WEBHOOK_SECRET
```

Use:

```text
.env
.env.example
```

Security requirements:

```text
server-side API credentials
input validation
payload limits
webhook signature verification
idempotency
rate limiting where appropriate
structured logging
secret scanning
synthetic data in public repository
```

Do not place secrets in frontend code.

---

# 50. LLM SECURITY

Treat LLM output as untrusted.

Do not allow LLM-generated text to become executable instructions.

Never let the model:

```text
call arbitrary shell commands
execute SQL
write ledger records
approve transactions
change accounting state
```

Use allow-listed structured operations.

Prefer:

```text
read evidence
write explanation
```

only.

---

# 51. OPEN-SOURCE ARCHITECTURE REFERENCES

These repositories are research references.

They are not a license to copy their implementation.

## Splink

https://github.com/moj-analytical-services/splink

Use for:

```text
probabilistic record linkage
blocking
comparisons
model training
evaluation
```

## FinRobot

https://github.com/AI4Finance-Foundation/FinRobot

Use for:

```text
finance-agent architecture
deterministic computation
LLM narration separation
```

## Blnk

https://github.com/blnkfinance/blnk

Use for:

```text
financial transaction modeling
ledger concepts
reconciliation concepts
```

## Django Ledger

https://github.com/arrobalytics/django-ledger

Use for:

```text
double-entry accounting concepts
domain modeling
ledger architecture
```

## OpenFang

https://github.com/RightNow-AI/openfang

Use for:

```text
cryptographic audit concepts
tamper-evident event chains
```

## Financial Transaction Reconciliation

https://github.com/nabigwaku/Financial-Transaction-Reconciliation

Use for:

```text
practical reconciliation workflows
```

Before copying or redistributing third-party code, verify its current license and comply with its terms.

---

# 52. RAZORPAY OFFICIAL OPEN-SOURCE REFERENCES

Use official Razorpay SDKs/repositories where they fit.

Official organization:

https://github.com/razorpay

Node SDK:

https://github.com/razorpay/razorpay-node

Other official SDKs can be evaluated through the organization.

Prefer official documentation and SDKs over unofficial wrappers.

---

# 53. TEST STRATEGY

Minimum test groups:

```text
unit
integration
evaluation
security
LLM guardrails
API
frontend
```

### Unit

```text
normalization
currency conversion
date parsing
duplicate detection
exception classification
metric calculations
hash verification
```

### Integration

```text
CSV
 ↓
normalization
 ↓
Splink
 ↓
reconciliation
 ↓
metrics
 ↓
audit
```

### API

```text
/health
/reconcile
/reports/latest
/audit/verify
```

### Security

```text
invalid webhook signature
oversized payload
missing required field
malformed LLM response
secret exposure
```

---

# 54. REQUIRED EDGE-CASE TESTS

Test:

```text
exact match
fuzzy reference match
UTR/PAY prefix difference
date drift
duplicate reference
duplicate transaction
missing counterpart
ambiguous candidates
partial settlement
fee difference
currency mismatch
null values
malformed dates
zero amount
negative adjustment
one-to-many settlement
```

Do not allow a higher match rate to override correctness.

---

# 55. LLM TESTS

Test that the LLM cannot:

```text
change amount
change decision
change confidence
invent transaction IDs
invent evidence
```

Example malicious/invalid response:

```json
{
  "decision": "MATCH",
  "amount": "999999"
}
```

must be rejected because the LLM does not have authority over those fields.

Only accepted fields:

```text
explanation
recommended_action
```

---

# 56. AUDIT TESTS

Test:

```text
clean audit log       -> PASS
change old decision   -> FAIL
change confidence     -> FAIL
remove event          -> FAIL
reorder events        -> FAIL
```

The exact implementation can use a SHA-256 chain.

---

# 57. BENCHMARK TEST

Minimum final benchmark:

```text
50+ records
```

Recommended:

```text
200+ records
```

Benchmark:

```text
0.80
0.85
0.90
0.95
0.97
0.99
```

Report:

```text
precision
recall
match rate
manual review rate
exception count
processing time
reconciled value
```

The selected threshold should be justified by the trade-off.

---

# 58. REPOSITORY STRUCTURE

```text
reconiq/
│
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
│
├── apps/
│   ├── api/
│   └── web/
│
├── data/
│   ├── raw/
│   ├── normalized/
│   ├── synthetic/
│   └── ground_truth/
│
├── ingestion/
│   ├── loaders.py
│   ├── normalize.py
│   ├── schemas.py
│   ├── razorpay_adapter.py
│   └── webhook_parser.py
│
├── matching/
│   ├── candidate_generation.py
│   ├── comparisons.py
│   ├── run_splink.py
│   ├── reconcile.py
│   └── metrics.py
│
├── exceptions/
│   ├── classifier.py
│   ├── reason_codes.py
│   └── policies.py
│
├── settlements/
│   ├── service.py
│   └── policies.py
│
├── audit/
│   ├── audit_log.py
│   └── verify.py
│
├── llm/
│   ├── explain.py
│   ├── prompts.py
│   └── schemas.py
│
├── database/
│   ├── models.py
│   ├── migrations/
│   └── session.py
│
├── benchmarks/
│   ├── run_benchmark.py
│   └── results/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   ├── security/
│   └── llm/
│
├── docs/
│   ├── architecture.md
│   ├── evaluation.md
│   ├── threat-model.md
│   ├── demo-script.md
│   └── decisions.md
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

# 59. TECHNOLOGY STACK

Recommended stack:

## Frontend

```text
Next.js
React
TypeScript
Tailwind CSS
Recharts
```

## Backend

```text
Python
FastAPI
Pydantic
```

## Data

```text
PostgreSQL
Polars/Pandas
DuckDB where useful
```

## Matching

```text
Splink 4.x
```

## AI

```text
OpenAI API
structured outputs / JSON schema
```

## Audit

```text
SHA-256 hash chain
```

## Deployment

```text
Vercel
+
Railway / Render
+
PostgreSQL
```

Docker must remain the local reproducibility path regardless of hosting provider.

---

# 60. BUILD PHASES

## Phase 1 — Foundation

Implement:

```text
Next.js
FastAPI
PostgreSQL
Docker
CI
```

Success:

```text
frontend loads
API health passes
database connection passes
```

---

## Phase 2 — Synthetic data

Implement:

```text
synthetic_gen.py
```

Success:

```text
200+ records
ground truth
controlled edge cases
fixed seed
```

---

## Phase 3 — Canonical ingestion

Implement:

```text
schemas.py
normalize.py
loaders.py
```

Success:

```text
all sources become canonical records
```

---

## Phase 4 — Splink

Implement:

```text
candidate_generation.py
comparisons.py
run_splink.py
```

Success:

```text
actual linkage probabilities
actual predictions
reproducible run
```

---

## Phase 5 — Reconciliation

Implement:

```text
reconcile.py
policies.py
metrics.py
```

Success:

```text
AUTO_MATCH
MANUAL_REVIEW
UNRESOLVED
```

---

## Phase 6 — Exceptions

Implement:

```text
classifier.py
reason_codes.py
```

Success:

Every unresolved transaction gets a deterministic explanation or `UNCLASSIFIED`.

---

## Phase 7 — Audit

Implement:

```text
audit_log.py
verify.py
```

Success:

```text
clean -> PASS
tampered -> FAIL
```

---

## Phase 8 — LLM

Implement:

```text
explain.py
schemas.py
prompts.py
```

Success:

```text
evidence in
explanation out
no financial-state mutation
```

---

## Phase 9 — Razorpay

Implement:

```text
razorpay_adapter.py
webhook_parser.py
```

Success:

```text
Razorpay data
 -> canonical model
 -> existing reconciliation engine
```

---

## Phase 10 — Dashboard

Implement:

```text
Overview
Reconciliation
Transactions
Settlements
Exceptions
Data Quality
AI Control Room
Audit
Reports
Evaluation
Settings
```

Success:

A judge can understand the complete product without looking at the source code.

---

## Phase 11 — QA

Run:

```bash
pytest
docker compose build
docker compose up
python -m benchmarks.run_benchmark
```

Run everything again from a fresh clone.

---

# 61. 5-MINUTE PITCH

## 0:00–0:20 — Problem

Show:

```text
Razorpay
Merchant Ledger
Bank
```

Say:

> “The same financial event can appear differently across payment, settlement and banking systems. ReconIQ turns that mess into a measurable finance-control workflow.”

---

## 0:20–0:50 — Data

Load:

```text
200 records
3 sources
```

Show data-quality warnings.

---

## 0:50–1:25 — Reconciliation

Press:

```text
Run Reconciliation
```

Show:

```text
records processed
match rate
reconciled value
exceptions
```

---

## 1:25–2:05 — Difficult match

Open:

```text
PAY-82917
UTR-82917
payment_82917
```

Show:

```text
reference_core
evidence
confidence
decision trace
```

---

## 2:05–2:50 — Exception

Open:

```text
₹14,800
MISSING_COUNTERPART
```

Show the evidence.

Click:

```text
Explain with AI
```

---

## 2:50–3:25 — Partial settlement

Show:

```text
Gross
Fee
Tax
Net
Bank credit
```

Demonstrate that amount differences do not automatically become false missing transactions.

---

## 3:25–3:55 — Audit

Open:

```text
Audit Trail
✓ VERIFIED
```

Optionally demonstrate tamper detection.

---

## 3:55–4:30 — Evaluation

Open:

```text
Evaluation Lab
```

Show:

```text
Precision
Recall
Match Rate
Threshold Tradeoff
Processing Time
```

---

## 4:30–5:00 — Close

Say:

> “ReconIQ doesn't optimize for a perfect-looking demo. It reconciles what it can prove, explains what it can't, and leaves an auditable trail for every decision.”

---

# 62. APPLICATION-SAFE CLAIMS

Do not claim:

```text
100% accurate
fraud-proof
production-ready
fully autonomous
replaces accountants
blockchain-secured
Razorpay-approved
official Razorpay product
```

Preferred language:

```text
AI-assisted
deterministic financial computation
probabilistic record linkage
tamper-evident audit trail
synthetic benchmark
test-mode integration
human-review workflow
```

---

# 63. BUILD-CHALLENGE STORY

Use the following structure in the submission:

### Challenge

Cross-source references were inconsistent.

### Symptom

Exact matching generated false unmatched records.

### Investigation

The same underlying transaction appeared with different source-specific prefixes.

### Solution

Added canonical `reference_core` normalization while preserving original source references.

### Result

The normalized representation became an additional controlled matching signal.

### Lesson

> Financial integrations should preserve source truth while creating explicit canonical comparison semantics.

This is a stronger engineering story than pretending the system was perfect from the beginning.

---

# 64. PROFESSIONAL PRODUCT REQUIREMENTS

ReconIQ must not look like:

```text
localhost dashboard
CSV uploaded
AI answer
```

It should look like:

```text
enterprise finance control center
```

The product must contain:

```text
persistent navigation
global search
dashboard KPIs
data tables
filtering
transaction drill-down
settlement views
exception workflow
AI control room
audit verification
evaluation lab
reports
settings
system health
```

A user should be able to operate the system without knowing how Splink works.

---

# 65. UI MICROCOPY

Use professional terminology.

Prefer:

```text
Run Reconciliation
Review Exception
View Evidence
Decision Trace
Audit Verified
Manual Review Required
Settlement Variance
Data Quality Warning
AI Explanation
Recommended Action
```

Avoid:

```text
Magic AI
Fix Everything
Auto Solve
Super AI
100% Correct
```

---

# 66. EMPTY / LOADING / ERROR STATES

Implement:

### Loading

```text
Reconciling 200 records...

Generating candidate matches
██████████████████░░
```

### Empty exceptions

```text
No open exceptions

All records in this run passed
the configured reconciliation policy.
```

### Error

```text
Reconciliation failed

Run ID: recon_001

No financial state was modified.
View error details
```

### Audit failure

```text
Audit verification failed

One or more events may have been
modified or removed.
```

---

# 67. FINAL QUALITY BAR

Before submission, ALL must pass:

```text
[ ] 200+ synthetic records
[ ] hidden ground truth
[ ] three source ingestion
[ ] canonical normalization
[ ] UTR/PAY handling
[ ] real Splink 4.x linkage
[ ] configurable threshold
[ ] measured precision
[ ] measured recall
[ ] measured match rate
[ ] threshold sweep
[ ] exception taxonomy
[ ] partial settlement handling
[ ] duplicate handling
[ ] transaction evidence
[ ] decision trace
[ ] AI explanation
[ ] AI guardrails
[ ] fallback explanation
[ ] SHA-256 audit chain
[ ] tamper test
[ ] Razorpay adapter
[ ] test-mode/demo path
[ ] webhook verification path
[ ] PostgreSQL
[ ] FastAPI
[ ] Next.js
[ ] role-ready architecture
[ ] data quality center
[ ] settlement operations page
[ ] evaluation lab
[ ] reports
[ ] global search
[ ] Docker
[ ] CI
[ ] unit tests
[ ] integration tests
[ ] security tests
[ ] no committed secrets
[ ] reproducible benchmark
[ ] polished screenshots
[ ] 5-minute pitch
```

---

# 68. FINAL PRODUCT DEFINITION

## ReconIQ Enterprise

**AI Finance Control Center**

ReconIQ is a governed finance-operations platform that reconciles payment, settlement, ledger and bank records using probabilistic record linkage and deterministic financial policies.

It measures performance against ground truth, exposes uncertainty through a structured exception workflow, uses AI only to explain deterministic evidence, and preserves a tamper-evident audit trail for every decision.

### Core principle

> **Deterministic systems decide. AI explains.**

### Product promise

> **Reconcile what you can prove. Explain what you can't.**

---

# 69. IMPLEMENTATION RULE FOR ANTIGRAVITY

Treat this README as the source-of-truth engineering specification.

Do not:

```text
fake metrics
hard-code KPI values
mock Splink
allow LLMs to decide matches
hide exceptions
copy Razorpay UI pixel-for-pixel
copy third-party repositories wholesale
commit credentials
leak ground truth
```

Do:

```text
build the backend first
build the evaluation harness early
make every dashboard number API-driven
make benchmark results reproducible
build evidence before AI narration
build audit before final demo
test from a fresh clone
```

When a requirement is ambiguous, choose the implementation that maximizes:

```text
correctness
auditability
reproducibility
operator usefulness
security
demonstrable business impact
```

---

# 70. FINAL README CHECK

The final README published to GitHub should include:

```text
Product screenshots
Architecture diagram
Quick start
Docker setup
Environment variables
Razorpay integration setup
Demo dataset
Benchmark results
Evaluation methodology
Security model
Open-source references
Limitations
5-minute demo instructions
```

The benchmark section must be generated from the actual repository state immediately before submission.

---

# OFFICIAL REFERENCES

Razorpay:
https://razorpay.com/

Razorpay API:
https://razorpay.com/docs/api/

Razorpay settlement APIs:
https://razorpay.com/docs/payments/settlements/apis/

Razorpay settlement reconciliation:
https://razorpay.com/docs/api/settlements/fetch-recon/

Razorpay settlement dashboard:
https://razorpay.com/docs/payments/settlements/dashboard/

Razorpay webhooks:
https://razorpay.com/docs/webhooks/

Razorpay GitHub:
https://github.com/razorpay

Razorpay Node SDK:
https://github.com/razorpay/razorpay-node

Splink:
https://github.com/moj-analytical-services/splink

FinRobot:
https://github.com/AI4Finance-Foundation/FinRobot

Blnk:
https://github.com/blnkfinance/blnk

Django Ledger:
https://github.com/arrobalytics/django-ledger

OpenFang:
https://github.com/RightNow-AI/openfang

Financial Transaction Reconciliation:
https://github.com/nabigwaku/Financial-Transaction-Reconciliation
