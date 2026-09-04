"""
ReconIQ Enterprise — Reference Normalization
============================================
Extracts reference_core from source-specific reference formats.

Design principle:
  NEVER overwrite source_reference.
  ALWAYS derive reference_core as a controlled comparison field.

Example:
  PAY-82917       → 82917
  UTR-82917       → 82917
  NEFT82917       → 82917
  payment_82917   → 82917
  TXN-82917       → 82917
  LED-1042        → 1042
"""
import re
from typing import Optional
from ingestion.schemas import NormalizationTrace

# ── Known prefix patterns (order matters — longest first) ────────────────────
KNOWN_PREFIXES: list[str] = [
    "PAY-", "PAY_",
    "UTR-", "UTR_", "UTR",
    "NEFT-", "NEFT_", "NEFT",
    "IMPS-", "IMPS_", "IMPS",
    "RTGS-", "RTGS_", "RTGS",
    "TXN-", "TXN_",
    "LED-", "LED_",
    "BANK-", "BANK_",
    "SETL_", "SETL-",
    "payment_", "payment-",
    "order_", "order-",
    "ORDER-", "ORDER_",
]

# Sort by length descending so longer prefixes are matched first
KNOWN_PREFIXES.sort(key=len, reverse=True)

# Trailing suffixes that don't change the core (e.g. UTR82917A → 82917)
SUFFIX_PATTERN = re.compile(r"[A-Za-z_-]$")


def strip_prefix(raw: str) -> tuple[str, list[str]]:
    """Strip known prefixes from a reference string. Returns (core, stripped_prefixes)."""
    value = raw.strip()
    stripped = []
    changed = True
    while changed:
        changed = False
        for prefix in KNOWN_PREFIXES:
            if value.upper().startswith(prefix.upper()):
                stripped.append(prefix)
                value = value[len(prefix):]
                changed = True
                break
    return value, stripped


def normalize_reference(raw: str) -> NormalizationTrace:
    """
    Normalize a raw reference to its canonical core.

    Returns a NormalizationTrace with:
      raw: original value
      normalizer: name of the normalizer applied
      normalized: the comparison key
      prefixes_stripped: which prefixes were removed
    """
    if not raw or not raw.strip():
        return NormalizationTrace(
            raw=raw,
            normalizer="empty",
            normalized="",
            prefixes_stripped=[],
        )

    core, prefixes = strip_prefix(raw.strip())

    # Strip trailing alpha suffixes like A/B in split settlements (UTR82917A)
    if core and core[-1].isalpha():
        core = core[:-1]

    normalizer = "strip_known_prefix" if prefixes else "passthrough"

    return NormalizationTrace(
        raw=raw,
        normalizer=normalizer,
        normalized=core.strip(),
        prefixes_stripped=prefixes,
    )


def normalize_amount(amount_str: str) -> int:
    """Parse amount string to integer minor units. Raises ValueError on invalid input."""
    if not amount_str or str(amount_str).strip() == "":
        return 0
    cleaned = str(amount_str).replace(",", "").replace("₹", "").strip()
    try:
        return int(float(cleaned))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid amount: {amount_str!r}") from e


def normalize_currency(currency_str: str) -> str:
    """Normalize currency string to ISO 4217 uppercase."""
    mapping = {
        "inr": "INR",
        "₹": "INR",
        "rs": "INR",
        "rupee": "INR",
        "rupees": "INR",
        "usd": "USD",
        "$": "USD",
    }
    s = str(currency_str).strip().lower()
    return mapping.get(s, str(currency_str).strip().upper())


def normalize_status(source: str, raw_status: str) -> str:
    """Map source-specific status values to canonical statuses."""
    status_map = {
        "razorpay": {
            "captured": "captured",
            "authorized": "authorized",
            "failed": "failed",
            "refunded": "refunded",
            "created": "created",
        },
        "ledger": {
            "posted": "posted",
            "pending": "pending",
            "reversed": "reversed",
            "draft": "draft",
        },
        "bank": {
            "credited": "credited",
            "debited": "debited",
            "returned": "returned",
            "pending": "pending",
        },
    }
    source_map = status_map.get(source.lower(), {})
    return source_map.get(raw_status.lower(), raw_status.lower())
