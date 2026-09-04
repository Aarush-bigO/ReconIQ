"""
ReconIQ Enterprise — Razorpay Adapter
======================================
Fetches payment and settlement data from the Razorpay API and maps to FinancialEvent.

Provider abstraction:
  PaymentProviderAdapter (base)
    ├── RazorpayAdapter      (real API, test mode)
    └── SyntheticAdapter     (CSV fallback for demo/offline)

The reconciliation engine is INDEPENDENT of the provider.
"""
import hashlib
import hmac
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional
import uuid

from ingestion.schemas import FinancialEvent
from ingestion.normalize import normalize_reference


class PaymentProviderAdapter(ABC):
    """Base adapter interface — provider-agnostic."""

    @abstractmethod
    def fetch_payments(self, start: datetime, end: datetime) -> list[FinancialEvent]:
        ...

    @abstractmethod
    def fetch_settlements(self, start: datetime, end: datetime) -> list[FinancialEvent]:
        ...

    @abstractmethod
    def fetch_settlement_recon(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        ...


class RazorpayAdapter(PaymentProviderAdapter):
    """
    Connects to the Razorpay API (test mode) and returns canonical records.
    
    References:
      https://razorpay.com/docs/api/payments/
      https://razorpay.com/docs/payments/settlements/apis/
      https://razorpay.com/docs/api/settlements/fetch-recon/
    """

    def __init__(self, key_id: str, key_secret: str):
        self.key_id = key_id
        self.key_secret = key_secret
        self._client = None
        self._connected = False
        self._init_client()

    def _init_client(self):
        try:
            import razorpay
            self._client = razorpay.Client(auth=(self.key_id, self.key_secret))
            # Verify connection with a lightweight call
            self._client.utility.verify_payment_signature  # Just access the attr
            self._connected = True
        except Exception as e:
            self._connected = False
            print(f"[RazorpayAdapter] Connection failed: {e}")

    def is_connected(self) -> bool:
        return self._connected

    def get_provider_name(self) -> str:
        return "Razorpay (Test Mode)"

    def _to_epoch(self, dt: datetime) -> int:
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    def fetch_payments(self, start: datetime, end: datetime) -> list[FinancialEvent]:
        """Fetch payments from Razorpay API and return canonical records."""
        if not self._connected:
            return []

        records = []
        try:
            # Razorpay API uses epoch timestamps
            response = self._client.payment.all({
                "from": self._to_epoch(start),
                "to": self._to_epoch(end),
                "count": 100,
            })
            items = response.get("items", [])

            for item in items:
                pay_id = item.get("id", "")
                amount = int(item.get("amount", 0))
                fee = int(item.get("fee", 0))
                tax = int(item.get("tax", 0))
                created_at = datetime.fromtimestamp(item.get("created_at", 0), tz=timezone.utc)
                reference = item.get("description") or item.get("order_id") or pay_id
                norm = normalize_reference(reference)

                record = FinancialEvent(
                    canonical_id=f"txn_{uuid.uuid4().hex[:12]}",
                    source="razorpay",
                    source_record_id=pay_id,
                    source_reference=reference,
                    reference_core=norm.normalized,
                    normalization_trace={
                        "raw": norm.raw,
                        "normalizer": norm.normalizer,
                        "normalized": norm.normalized,
                        "prefixes_stripped": norm.prefixes_stripped,
                    },
                    amount_minor=amount,
                    currency=item.get("currency", "INR"),
                    event_time=created_at,
                    event_type="PAYMENT",
                    direction="CREDIT",
                    status=item.get("status", ""),
                    payment_id=pay_id,
                    order_id=item.get("order_id", ""),
                    settlement_id=item.get("settlement_id") or "",
                    utr="",
                    fee_minor=fee,
                    tax_minor=tax,
                    adjustment_minor=0,
                    metadata={
                        "method": item.get("method", ""),
                        "bank": item.get("bank", ""),
                        "vpa": item.get("vpa", ""),
                        "email": item.get("email", ""),
                        "contact": item.get("contact", ""),
                        "notes": item.get("notes", {}),
                    },
                )
                records.append(record)
        except Exception as e:
            print(f"[RazorpayAdapter] fetch_payments error: {e}")

        return records

    def fetch_settlements(self, start: datetime, end: datetime) -> list[FinancialEvent]:
        """Fetch settlements from Razorpay API."""
        if not self._connected:
            return []

        records = []
        try:
            response = self._client.settlement.all({
                "from": self._to_epoch(start),
                "to": self._to_epoch(end),
                "count": 100,
            })
            items = response.get("items", [])

            for item in items:
                setl_id = item.get("id", "")
                amount = int(item.get("amount", 0))
                fees = int(item.get("fees", 0))
                tax = int(item.get("tax", 0))
                created_at = datetime.fromtimestamp(item.get("created_at", 0), tz=timezone.utc)
                utr = item.get("utr", "")
                norm = normalize_reference(utr or setl_id)

                record = FinancialEvent(
                    canonical_id=f"txn_{uuid.uuid4().hex[:12]}",
                    source="razorpay",
                    source_record_id=setl_id,
                    source_reference=utr or setl_id,
                    reference_core=norm.normalized,
                    normalization_trace={"raw": norm.raw, "normalizer": norm.normalizer, "normalized": norm.normalized},
                    amount_minor=amount,
                    currency="INR",
                    event_time=created_at,
                    event_type="SETTLEMENT",
                    direction="CREDIT",
                    status=item.get("status", ""),
                    payment_id="",
                    order_id="",
                    settlement_id=setl_id,
                    utr=utr,
                    fee_minor=fees,
                    tax_minor=tax,
                    adjustment_minor=0,
                    metadata={"settlement_raw": item},
                )
                records.append(record)
        except Exception as e:
            print(f"[RazorpayAdapter] fetch_settlements error: {e}")

        return records

    def fetch_settlement_recon(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """
        Fetch detailed settlement reconciliation report from Razorpay.
        Reference: https://razorpay.com/docs/api/settlements/fetch-recon/
        """
        if not self._connected:
            return []

        try:
            response = self._client.settlement.fetch_recon({
                "year": start.year,
                "month": start.month,
                "day": start.day,
                "count": 100,
            })
            return response.get("items", [])
        except Exception as e:
            print(f"[RazorpayAdapter] fetch_settlement_recon error: {e}")
            return []


class SyntheticAdapter(PaymentProviderAdapter):
    """
    Fallback adapter — loads from synthetic CSV files.
    Used when Razorpay credentials are not configured.
    Always clearly labeled as 'Demo Mode'.
    """

    def get_provider_name(self) -> str:
        return "Synthetic Data (Demo Mode)"

    def is_connected(self) -> bool:
        return True

    def fetch_payments(self, start: datetime, end: datetime) -> list[FinancialEvent]:
        from ingestion.loaders import load_csv, SYNTHETIC_DIR
        return load_csv(SYNTHETIC_DIR / "razorpay.csv", "razorpay")

    def fetch_settlements(self, start: datetime, end: datetime) -> list[FinancialEvent]:
        from ingestion.loaders import load_csv, SYNTHETIC_DIR
        return load_csv(SYNTHETIC_DIR / "bank.csv", "bank")

    def fetch_settlement_recon(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        return []


def get_adapter(key_id: str = "", key_secret: str = "") -> PaymentProviderAdapter:
    """Return the appropriate adapter based on credentials availability."""
    if key_id and key_secret and key_id != "rzp_test_your_key_id_here":
        adapter = RazorpayAdapter(key_id, key_secret)
        if adapter.is_connected():
            return adapter
    return SyntheticAdapter()


# ── Webhook Parser ────────────────────────────────────────────────────────────

class WebhookVerificationError(Exception):
    """Raised when webhook signature verification fails."""
    pass


def verify_razorpay_webhook(
    payload_bytes: bytes,
    signature: str,
    webhook_secret: str,
) -> bool:
    """
    Verify Razorpay webhook signature using HMAC-SHA256.
    Reference: https://razorpay.com/docs/webhooks/validate-test/
    """
    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_webhook_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Parse a Razorpay webhook payload into a normalized event.
    
    Stored fields: event_id, event_type, provider, received_at, payload_hash, processing_status
    """
    payload_str = json.dumps(payload, sort_keys=True)
    payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

    return {
        "event_id": payload.get("id", f"evt_{uuid.uuid4().hex[:12]}"),
        "event_type": payload.get("event", "unknown"),
        "provider": "razorpay",
        "received_at": datetime.utcnow().isoformat(),
        "payload_hash": payload_hash,
        "processing_status": "received",
        "raw_payload": payload,
    }
