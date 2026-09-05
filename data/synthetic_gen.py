"""
ReconIQ Enterprise — Synthetic Data Generator
=============================================
Generates realistic multi-source financial reconciliation test data.

Outputs:
  data/synthetic/razorpay.csv     — Payment records (Razorpay source)
  data/synthetic/ledger.csv       — Merchant accounting ledger records
  data/synthetic/bank.csv         — Bank credit records
  data/ground_truth/matches.json  — Hidden ground truth (never shown to matcher)

Seed: 42 (fully reproducible)

Distribution:
  300 normal clean matches
   50 reference format variants (UTR/PAY prefix differences)
   40 date drift (settlement delay 1-3 days)
   25 duplicates in source data
   25 fee/tax differences
   25 partial settlements (one-to-many)
   25 missing counterparts (no match exists)
   10 ambiguous (multiple candidates)
  ───
  500 scenarios
"""

import csv
import hashlib
import json
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SEED = 42
random.seed(SEED)

BASE_DIR = Path(__file__).parent.parent
SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth"
SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)
GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def _date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

def _rzp_id(prefix: str, n: int) -> str:
    return f"{prefix}_{n:08x}"

def _amount_inr(minor: int) -> str:
    """Return amount in paise (integer, no float)."""
    return str(minor)

BASE_DATE = datetime(2026, 8, 1, 0, 0, 0, tzinfo=timezone.utc)

def _rand_date(offset_days: int = 0) -> datetime:
    day = random.randint(1, 25)
    hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    return BASE_DATE + timedelta(days=day + offset_days, hours=hour, minutes=minute)

def _rand_amount() -> int:
    """Random amount in paise (₹100 – ₹50,000)."""
    return random.choice([
        random.randint(10000, 100000),    # ₹100–₹1,000
        random.randint(100000, 1000000),  # ₹1,000–₹10,000
        random.randint(1000000, 5000000), # ₹10,000–₹50,000
    ])

def _fee(amount: int) -> int:
    """Razorpay fee: 2% of amount, min ₹2."""
    return max(200, int(amount * 0.02))

def _tax(fee: int) -> int:
    """GST 18% on fee."""
    return int(fee * 0.18)

def _net(amount: int, fee: int, tax: int, adjustment: int = 0) -> int:
    return amount - fee - tax - adjustment


# ── Scenario builders ─────────────────────────────────────────────────────────

razorpay_rows = []
ledger_rows = []
bank_rows = []
ground_truth = []  # {"ledger_id": ..., "true_matches": [...]}

pay_counter = 1000
led_counter = 1000
setl_counter = 100
bank_counter = 1000


def _next_pay():
    global pay_counter
    pay_counter += 1
    return f"pay_{pay_counter:07d}"

def _next_led():
    global led_counter
    led_counter += 1
    return f"LED-{led_counter}"

def _next_setl():
    global setl_counter
    setl_counter += 1
    return f"SETL_{setl_counter}"

def _next_bank():
    global bank_counter
    bank_counter += 1
    return f"BANK-{bank_counter}"


def add_normal_match(i: int):
    """Clean match across all 3 sources. Same reference_core, same amount."""
    pay_id = _next_pay()
    led_id = _next_led()
    bank_id = _next_bank()
    core_ref = f"{82000 + i}"
    setl_id = _next_setl()

    amount = _rand_amount()
    fee = _fee(amount)
    tax = _tax(fee)
    net = _net(amount, fee, tax)
    dt = _rand_date()
    settle_dt = dt + timedelta(days=random.randint(1, 2))

    razorpay_rows.append({
        "source": "razorpay",
        "source_record_id": pay_id,
        "source_reference": f"PAY-{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "captured",
        "payment_id": pay_id,
        "order_id": f"order_{i:07d}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": fee,
        "tax_minor": tax,
        "adjustment_minor": 0,
    })

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"payment_{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": pay_id,
        "order_id": f"order_{i:07d}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    bank_rows.append({
        "source": "bank",
        "source_record_id": bank_id,
        "source_reference": f"UTR-{core_ref}",
        "amount_minor": net,
        "currency": "INR",
        "event_time": _ts(settle_dt),
        "transaction_type": "credit",
        "status": "credited",
        "payment_id": "",
        "order_id": "",
        "settlement_id": setl_id,
        "utr": f"UTR{core_ref}",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [pay_id, bank_id],
        "scenario": "NORMAL_MATCH",
        "core_ref": core_ref,
    })


def add_reference_variant(i: int):
    """Same transaction, reference prefixes differ — the core normalization challenge."""
    pay_id = _next_pay()
    led_id = _next_led()
    bank_id = _next_bank()
    core_ref = f"{85000 + i}"
    setl_id = _next_setl()

    amount = _rand_amount()
    fee = _fee(amount)
    tax = _tax(fee)
    net = _net(amount, fee, tax)
    dt = _rand_date()
    settle_dt = dt + timedelta(days=1)

    # Razorpay: PAY- prefix
    # Ledger: TXN- prefix (different!)
    # Bank: UTR- prefix (different!)
    razorpay_rows.append({
        "source": "razorpay",
        "source_record_id": pay_id,
        "source_reference": f"PAY-{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "captured",
        "payment_id": pay_id,
        "order_id": f"order_ref_{i}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": fee,
        "tax_minor": tax,
        "adjustment_minor": 0,
    })

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"TXN-{core_ref}",  # Different prefix
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": pay_id,
        "order_id": f"order_ref_{i}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    bank_rows.append({
        "source": "bank",
        "source_record_id": bank_id,
        "source_reference": f"NEFT{core_ref}",   # Yet another format
        "amount_minor": net,
        "currency": "INR",
        "event_time": _ts(settle_dt),
        "transaction_type": "credit",
        "status": "credited",
        "payment_id": "",
        "order_id": "",
        "settlement_id": setl_id,
        "utr": f"NEFT{core_ref}",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [pay_id, bank_id],
        "scenario": "REFERENCE_VARIANT",
        "core_ref": core_ref,
    })


def add_date_drift(i: int):
    """Same transaction but bank credits 2–3 days after payment capture."""
    pay_id = _next_pay()
    led_id = _next_led()
    bank_id = _next_bank()
    core_ref = f"{88000 + i}"
    setl_id = _next_setl()

    amount = _rand_amount()
    fee = _fee(amount)
    tax = _tax(fee)
    net = _net(amount, fee, tax)
    dt = _rand_date()
    drift_days = random.randint(2, 3)
    settle_dt = dt + timedelta(days=drift_days)

    razorpay_rows.append({
        "source": "razorpay",
        "source_record_id": pay_id,
        "source_reference": f"PAY-{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "captured",
        "payment_id": pay_id,
        "order_id": f"order_drift_{i}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": fee,
        "tax_minor": tax,
        "adjustment_minor": 0,
    })

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"payment_{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": pay_id,
        "order_id": f"order_drift_{i}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    bank_rows.append({
        "source": "bank",
        "source_record_id": bank_id,
        "source_reference": f"UTR-{core_ref}",
        "amount_minor": net,
        "currency": "INR",
        "event_time": _ts(settle_dt),  # Date drifted
        "transaction_type": "credit",
        "status": "credited",
        "payment_id": "",
        "order_id": "",
        "settlement_id": setl_id,
        "utr": f"UTR{core_ref}",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [pay_id, bank_id],
        "scenario": "DATE_DRIFT",
        "core_ref": core_ref,
        "drift_days": drift_days,
    })


def add_duplicate(i: int):
    """Duplicate records in source — same reference appears twice."""
    pay_id = _next_pay()
    pay_id_dup = _next_pay()
    led_id = _next_led()
    bank_id = _next_bank()
    core_ref = f"{91000 + i}"
    setl_id = _next_setl()

    amount = _rand_amount()
    fee = _fee(amount)
    tax = _tax(fee)
    net = _net(amount, fee, tax)
    dt = _rand_date()
    # Duplicate a few minutes later
    dt_dup = dt + timedelta(minutes=random.randint(1, 10))

    for pid, event_dt in [(pay_id, dt), (pay_id_dup, dt_dup)]:
        razorpay_rows.append({
            "source": "razorpay",
            "source_record_id": pid,
            "source_reference": f"PAY-{core_ref}",  # Same reference!
            "amount_minor": amount,
            "currency": "INR",
            "event_time": _ts(event_dt),
            "transaction_type": "payment",
            "status": "captured",
            "payment_id": pid,
            "order_id": f"order_dup_{i}",
            "settlement_id": setl_id,
            "utr": "",
            "fee_minor": fee,
            "tax_minor": tax,
            "adjustment_minor": 0,
        })

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"payment_{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": pay_id,
        "order_id": f"order_dup_{i}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    bank_rows.append({
        "source": "bank",
        "source_record_id": bank_id,
        "source_reference": f"UTR-{core_ref}",
        "amount_minor": net,
        "currency": "INR",
        "event_time": _ts(dt + timedelta(days=1)),
        "transaction_type": "credit",
        "status": "credited",
        "payment_id": "",
        "order_id": "",
        "settlement_id": setl_id,
        "utr": f"UTR{core_ref}",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [pay_id, bank_id],
        "scenario": "DUPLICATE",
        "core_ref": core_ref,
        "duplicate_pay_id": pay_id_dup,
    })


def add_fee_difference(i: int):
    """Payment captured but ledger shows slightly different amount (fee variance)."""
    pay_id = _next_pay()
    led_id = _next_led()
    bank_id = _next_bank()
    core_ref = f"{93000 + i}"
    setl_id = _next_setl()

    amount = _rand_amount()
    fee = _fee(amount)
    tax = _tax(fee)
    # Ledger may record gross amount; bank gets net
    net = _net(amount, fee, tax)
    # Slight fee rounding difference
    adj = random.randint(-50, 50)
    dt = _rand_date()

    razorpay_rows.append({
        "source": "razorpay",
        "source_record_id": pay_id,
        "source_reference": f"PAY-{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "captured",
        "payment_id": pay_id,
        "order_id": f"order_fee_{i}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": fee,
        "tax_minor": tax,
        "adjustment_minor": adj,
    })

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"payment_{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": pay_id,
        "order_id": f"order_fee_{i}",
        "settlement_id": setl_id,
        "utr": "",
        "fee_minor": fee + 100,  # Fee variance
        "tax_minor": tax,
        "adjustment_minor": 0,
    })

    bank_rows.append({
        "source": "bank",
        "source_record_id": bank_id,
        "source_reference": f"UTR-{core_ref}",
        "amount_minor": net + adj,
        "currency": "INR",
        "event_time": _ts(dt + timedelta(days=1)),
        "transaction_type": "credit",
        "status": "credited",
        "payment_id": "",
        "order_id": "",
        "settlement_id": setl_id,
        "utr": f"UTR{core_ref}",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [pay_id, bank_id],
        "scenario": "FEE_DIFFERENCE",
        "core_ref": core_ref,
    })


def add_partial_settlement(i: int):
    """One payment, two settlement records (split across two batches)."""
    pay_id = _next_pay()
    led_id = _next_led()
    bank_id_a = _next_bank()
    bank_id_b = _next_bank()
    core_ref = f"{95000 + i}"
    setl_id_a = _next_setl()
    setl_id_b = _next_setl()

    amount = _rand_amount()
    fee = _fee(amount)
    tax = _tax(fee)
    net = _net(amount, fee, tax)
    split_a = int(net * 0.6)
    split_b = net - split_a
    dt = _rand_date()

    razorpay_rows.append({
        "source": "razorpay",
        "source_record_id": pay_id,
        "source_reference": f"PAY-{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "captured",
        "payment_id": pay_id,
        "order_id": f"order_partial_{i}",
        "settlement_id": f"{setl_id_a},{setl_id_b}",
        "utr": "",
        "fee_minor": fee,
        "tax_minor": tax,
        "adjustment_minor": 0,
    })

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"payment_{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": pay_id,
        "order_id": f"order_partial_{i}",
        "settlement_id": setl_id_a,
        "utr": "",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    bank_rows.append({
        "source": "bank",
        "source_record_id": bank_id_a,
        "source_reference": f"UTR-{core_ref}A",
        "amount_minor": split_a,
        "currency": "INR",
        "event_time": _ts(dt + timedelta(days=1)),
        "transaction_type": "credit",
        "status": "credited",
        "payment_id": "",
        "order_id": "",
        "settlement_id": setl_id_a,
        "utr": f"UTR{core_ref}A",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    bank_rows.append({
        "source": "bank",
        "source_record_id": bank_id_b,
        "source_reference": f"UTR-{core_ref}B",
        "amount_minor": split_b,
        "currency": "INR",
        "event_time": _ts(dt + timedelta(days=2)),
        "transaction_type": "credit",
        "status": "credited",
        "payment_id": "",
        "order_id": "",
        "settlement_id": setl_id_b,
        "utr": f"UTR{core_ref}B",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [pay_id, bank_id_a, bank_id_b],
        "scenario": "PARTIAL_SETTLEMENT",
        "core_ref": core_ref,
    })


def add_missing_counterpart(i: int):
    """Ledger record with no matching Razorpay or bank record."""
    led_id = _next_led()
    core_ref = f"{97000 + i}"
    amount = _rand_amount()
    dt = _rand_date()

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"payment_{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": "",
        "order_id": f"order_missing_{i}",
        "settlement_id": "",
        "utr": "",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [],
        "scenario": "MISSING_COUNTERPART",
        "core_ref": core_ref,
    })


def add_ambiguous(i: int):
    """Same amount, close date — could match multiple candidates."""
    pay_id_a = _next_pay()
    pay_id_b = _next_pay()
    led_id = _next_led()
    core_ref = f"{99000 + i}"

    amount = 50000  # Fixed amount to create ambiguity
    fee = _fee(amount)
    tax = _tax(fee)
    dt = _rand_date()

    for pid, ref_suffix in [(pay_id_a, ""), (pay_id_b, "_2")]:
        razorpay_rows.append({
            "source": "razorpay",
            "source_record_id": pid,
            "source_reference": f"PAY-{core_ref}{ref_suffix}",
            "amount_minor": amount,
            "currency": "INR",
            "event_time": _ts(dt + timedelta(hours=random.randint(0, 4))),
            "transaction_type": "payment",
            "status": "captured",
            "payment_id": pid,
            "order_id": f"order_ambig_{i}",
            "settlement_id": _next_setl(),
            "utr": "",
            "fee_minor": fee,
            "tax_minor": tax,
            "adjustment_minor": 0,
        })

    ledger_rows.append({
        "source": "ledger",
        "source_record_id": led_id,
        "source_reference": f"payment_{core_ref}",
        "amount_minor": amount,
        "currency": "INR",
        "event_time": _ts(dt),
        "transaction_type": "payment",
        "status": "posted",
        "payment_id": "",  # No payment_id in ledger for this case
        "order_id": f"order_ambig_{i}",
        "settlement_id": "",
        "utr": "",
        "fee_minor": 0,
        "tax_minor": 0,
        "adjustment_minor": 0,
    })

    ground_truth.append({
        "ledger_id": led_id,
        "true_matches": [pay_id_a],  # Only first one is true
        "scenario": "AMBIGUOUS",
        "core_ref": core_ref,
        "decoy_id": pay_id_b,
    })


# ── Generate all scenarios ────────────────────────────────────────────────────

print("Generating synthetic reconciliation data (seed=42)...")

for i in range(300):
    add_normal_match(i)

for i in range(50):
    add_reference_variant(i)

for i in range(40):
    add_date_drift(i)

for i in range(25):
    add_duplicate(i)

for i in range(25):
    add_fee_difference(i)

for i in range(25):
    add_partial_settlement(i)

for i in range(25):
    add_missing_counterpart(i)

for i in range(10):
    add_ambiguous(i)

# Shuffle rows (don't let the order hint at matches)
random.shuffle(razorpay_rows)
random.shuffle(ledger_rows)
random.shuffle(bank_rows)

# ── Write CSVs ───────────────────────────────────────────────────────────────

COLS = [
    "source", "source_record_id", "source_reference",
    "amount_minor", "currency", "event_time", "transaction_type", "status",
    "payment_id", "order_id", "settlement_id", "utr",
    "fee_minor", "tax_minor", "adjustment_minor",
]


def write_csv(rows: list[dict], path: Path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows):4d} rows → {path.name}")


write_csv(razorpay_rows, SYNTHETIC_DIR / "razorpay.csv")
write_csv(ledger_rows, SYNTHETIC_DIR / "ledger.csv")
write_csv(bank_rows, SYNTHETIC_DIR / "bank.csv")

# ── Write ground truth (hidden) ──────────────────────────────────────────────

gt_path = GROUND_TRUTH_DIR / "matches.json"
with open(gt_path, "w") as f:
    json.dump({"seed": SEED, "generated_at": datetime.utcnow().isoformat(), "matches": ground_truth}, f, indent=2)

print(f"  Wrote {len(ground_truth):4d} ground-truth entries → {gt_path.name}")

# ── Summary ──────────────────────────────────────────────────────────────────

scenarios = {}
for gt in ground_truth:
    s = gt["scenario"]
    scenarios[s] = scenarios.get(s, 0) + 1

print("\nScenario distribution:")
for scenario, count in sorted(scenarios.items()):
    print(f"  {scenario:<30} {count:>4d}")

total_records = len(razorpay_rows) + len(ledger_rows) + len(bank_rows)
print(f"\nTotal records across all sources: {total_records}")
print(f"  Razorpay: {len(razorpay_rows)}")
print(f"  Ledger:   {len(ledger_rows)}")
print(f"  Bank:     {len(bank_rows)}")
print(f"\nGround truth: {len(ground_truth)} entries")
print("\n✓ Synthetic data generation complete (seed=42, fully reproducible)")
