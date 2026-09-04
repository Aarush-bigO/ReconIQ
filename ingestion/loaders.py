"""
ReconIQ Enterprise — Data Loaders
===================================
Loads CSV files from all sources and converts them to FinancialEvent records.
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import Iterator
import uuid

from apps.api.config import get_settings
from ingestion.razorpay_adapter import get_adapter, PaymentProviderAdapter

from ingestion.schemas import FinancialEvent
from ingestion.normalize import (
    normalize_reference,
    normalize_amount,
    normalize_currency,
    normalize_status,
)

SYNTHETIC_DIR = Path(__file__).parent.parent / "data" / "synthetic"


def _parse_dt(value: str) -> datetime:
    """Parse ISO datetime strings with or without Z suffix."""
    if not value:
        return datetime.utcnow()
    value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        # Fallback: try common date formats
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return datetime.utcnow()


def _row_to_canonical(row: dict, source: str) -> FinancialEvent:
    """Convert a CSV row dict to a FinancialEvent."""
    raw_ref = row.get("source_reference", "")
    norm = normalize_reference(raw_ref)

    amount = normalize_amount(row.get("amount_minor", "0"))
    currency = normalize_currency(row.get("currency", "INR"))
    status = normalize_status(source, row.get("status", ""))

    import hashlib
    src_id = row.get("source_record_id", "")
    stable_hash = hashlib.md5(f"{source}_{src_id}".encode()).hexdigest()[:12]

    return FinancialEvent(
        canonical_id=f"txn_{stable_hash}",
        source=source,
        source_record_id=row.get("source_record_id", ""),
        source_reference=raw_ref,
        reference_core=norm.normalized,
        normalization_trace={
            "raw": norm.raw,
            "normalizer": norm.normalizer,
            "normalized": norm.normalized,
            "prefixes_stripped": norm.prefixes_stripped,
        },
        amount_minor=amount,
        currency=currency,
        event_time=_parse_dt(row.get("event_time", "")),
        event_type=row.get("event_type", "PAYMENT").upper(),
        direction=row.get("direction", "CREDIT").upper(),
        status=status,
        payment_id=row.get("payment_id", ""),
        order_id=row.get("order_id", ""),
        settlement_id=row.get("settlement_id", ""),
        utr=row.get("utr", ""),
        fee_minor=normalize_amount(row.get("fee_minor", "0")),
        tax_minor=normalize_amount(row.get("tax_minor", "0")),
        adjustment_minor=normalize_amount(row.get("adjustment_minor", "0")),
        metadata={"original_source": source},
    )


def load_csv(path: Path, source: str) -> list[FinancialEvent]:
    """Load a CSV file and return canonical transaction records."""
    records = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                record = _row_to_canonical(row, source)
                records.append(record)
            except Exception as e:
                # Log and continue — never silently fail on individual records
                print(f"[WARN] Failed to parse row {row}: {e}")
    return records


def get_payment_provider() -> PaymentProviderAdapter:
    """Factory method to get the correct payment provider adapter."""
    settings = get_settings()
    return get_adapter(settings.razorpay_key_id, settings.razorpay_key_secret)


def load_ledger_csv(path: Path | None = None) -> list[FinancialEvent]:
    p = path or (SYNTHETIC_DIR / "ledger.csv")
    return load_csv(p, "ledger")


def load_bank_csv(path: Path | None = None) -> list[FinancialEvent]:
    p = path or (SYNTHETIC_DIR / "bank.csv")
    return load_csv(p, "bank")


def load_all_sources(
    ledger_path: Path | None = None,
    bank_path: Path | None = None,
) -> dict[str, list[FinancialEvent]]:
    """Load all three sources and return a dict keyed by source name."""
    provider = get_payment_provider()
    return {
        "razorpay": provider.fetch_payments(start=datetime.now(), end=datetime.now()),
        "ledger": load_ledger_csv(ledger_path),
        "bank": load_bank_csv(bank_path),
    }


def records_to_dict_list(records: list[FinancialEvent]) -> list[dict]:
    """Convert canonical records to flat dicts for Splink/Polars consumption."""
    rows = []
    for r in records:
        rows.append({
            "canonical_id": r.canonical_id,
            "source": r.source,
            "source_record_id": r.source_record_id,
            "source_reference": r.source_reference,
            "reference_core": r.reference_core,
            "amount_minor": r.amount_minor,
            "currency": r.currency,
            "event_time": r.event_time.isoformat(),
            "event_date": r.event_time.date().isoformat(),
            "event_type": r.event_type,
            "direction": r.direction,
            "status": r.status,
            "payment_id": r.payment_id,
            "order_id": r.order_id,
            "settlement_id": r.settlement_id,
            "utr": r.utr,
            "fee_minor": r.fee_minor,
            "tax_minor": r.tax_minor,
            "adjustment_minor": r.adjustment_minor,
            "net_minor": r.net_minor,
        })
    return rows
