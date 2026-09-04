"""
ReconIQ Enterprise — Tamper-Evident Audit Log
==============================================
SHA-256 hash-chained + HMAC-signed event log.

Inspired by OpenFang's cryptographic audit concepts.

Every financial event is recorded with:
  1. A SHA-256 hash linking to the previous event (chain integrity)
  2. An HMAC signature using a server secret (authenticity verification)
  3. A unique nonce (replay attack prevention)
  4. An envelope schema with version tracking

Any modification to any event breaks the chain, which is detected by verify().

This is tamper-EVIDENT audit logging — not blockchain.
Do not call it blockchain.

Chain structure:
  event_1.hash = sha256(event_1.payload)
  event_2.hash = sha256(event_2.payload + event_1.hash)
  event_3.hash = sha256(event_3.payload + event_2.hash)
  ...

HMAC structure:
  event.hmac = hmac_sha256(secret, event.current_hash + event.nonce)
"""
import hashlib
import hmac
import json
import os
import secrets
import uuid
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import Session
from database.models import AuditEvent


# Schema version for the audit event envelope
ENVELOPE_VERSION = "1.0"
SCHEMA_VERSION = "reconiq.audit.v1"


class AuditChain:
    """
    In-memory audit chain with HMAC signing.
    Persisted to DB via the API layer.

    Hardened with OpenFang-inspired cryptographic integrity features:
      - SHA-256 hash chain (tamper evidence)
      - HMAC-SHA256 signing (authenticity)
      - Unique nonces (replay prevention)
      - Event envelope schema (versioning)
    """

    def __init__(self, hmac_secret: str | None = None, db_session: Optional[Session] = None):
        self._events: list[dict[str, Any]] = []
        self._last_hash: str = "GENESIS"
        self._hmac_secret: str = hmac_secret or os.environ.get(
            "AUDIT_HMAC_SECRET", "reconiq-dev-secret-change-in-production"
        )
        self._created_at: str = datetime.utcnow().isoformat()
        self._db_session = db_session
        
        # Load events from DB if available
        if self._db_session:
            db_events = self._db_session.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
            for e in db_events:
                event_dict = {
                    "event_id": e.event_id,
                    "run_id": e.run_id,
                    "record_id": e.record_id,
                    "action": e.action,
                    "decision": e.decision,
                    "confidence": e.confidence,
                    "reason_code": e.reason_code,
                    **e.payload,
                    "previous_hash": e.previous_hash,
                    "current_hash": e.current_hash,
                    "hmac_signature": e.hmac_signature,
                    "nonce": e.nonce,
                    "sequence": e.sequence,
                }
                self._events.append(event_dict)
            if db_events:
                self._last_hash = db_events[-1].current_hash

    def _compute_hash(self, payload: dict, previous_hash: str) -> str:
        """Compute deterministic SHA-256 hash of (payload + previous_hash)."""
        content = json.dumps(payload, sort_keys=True, default=str) + previous_hash
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _compute_hmac(self, current_hash: str, nonce: str) -> str:
        """
        Compute HMAC-SHA256 of (current_hash + nonce) using the server secret.
        This proves the event was created by an authorized server instance.
        """
        message = f"{current_hash}:{nonce}".encode("utf-8")
        return hmac.new(
            self._hmac_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()

    def record(
        self,
        run_id: str,
        record_id: str,
        action: str,
        decision: str = "",
        confidence: float = 0.0,
        reason_code: str = "",
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Record a new audit event and append it to the chain.
        Returns the full event dict with hashes, HMAC, and envelope metadata.
        """
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat()
        nonce = secrets.token_hex(16)  # 32-char random nonce

        payload = {
            "event_id": event_id,
            "run_id": run_id,
            "record_id": record_id,
            "action": action,
            "decision": decision,
            "confidence": confidence,
            "reason_code": reason_code,
            "timestamp": timestamp,
            **(extra or {}),
        }

        current_hash = self._compute_hash(payload, self._last_hash)
        hmac_signature = self._compute_hmac(current_hash, nonce)

        event = {
            # Envelope metadata (OpenFang-inspired)
            "envelope_version": ENVELOPE_VERSION,
            "schema_version": SCHEMA_VERSION,
            "nonce": nonce,
            "sequence": len(self._events),
            # Payload
            **payload,
            # Integrity
            "previous_hash": self._last_hash,
            "current_hash": current_hash,
            "hmac_signature": hmac_signature,
        }

        self._events.append(event)
        self._last_hash = current_hash
        
        if self._db_session:
            db_event = AuditEvent(
                event_id=event_id,
                run_id=run_id,
                record_id=record_id,
                action=action,
                decision=decision,
                confidence=confidence,
                reason_code=reason_code,
                payload=payload,
                previous_hash=event["previous_hash"],
                current_hash=current_hash,
                hmac_signature=hmac_signature,
                nonce=nonce,
                sequence=event["sequence"],
                created_at=datetime.fromisoformat(timestamp)
            )
            self._db_session.add(db_event)
            self._db_session.commit()
            
        return event

    def verify(self) -> tuple[bool, Optional[int]]:
        """
        Verify the entire chain (hash chain + HMAC signatures).

        Returns:
          (True, None) — chain is intact and all signatures valid
          (False, broken_index) — chain is broken at event index
        """
        if not self._events:
            return True, None

        prev_hash = "GENESIS"
        for i, event in enumerate(self._events):
            # Extract payload (exclude integrity and envelope fields)
            excluded_keys = {
                "previous_hash", "current_hash", "hmac_signature",
                "envelope_version", "schema_version", "nonce", "sequence",
            }
            payload = {k: v for k, v in event.items() if k not in excluded_keys}

            # Verify hash chain
            expected_hash = self._compute_hash(payload, prev_hash)
            if event.get("current_hash") != expected_hash:
                return False, i

            if event.get("previous_hash") != prev_hash:
                return False, i

            # Verify HMAC signature
            nonce = event.get("nonce", "")
            expected_hmac = self._compute_hmac(event["current_hash"], nonce)
            if event.get("hmac_signature") != expected_hmac:
                return False, i

            # Verify sequence
            if event.get("sequence") != i:
                return False, i

            prev_hash = event["current_hash"]

        return True, None

    def get_events(self) -> list[dict[str, Any]]:
        return list(self._events)

    def event_count(self) -> int:
        return len(self._events)

    def last_hash(self) -> str:
        return self._last_hash

    def export_chain(self) -> dict[str, Any]:
        """
        Export the entire chain as a JSON-LD compatible document.
        Suitable for external verification or archival.
        """
        is_valid, broken_at = self.verify()

        return {
            "@context": "https://reconiq.dev/audit/v1",
            "@type": "AuditChain",
            "chain_id": f"chain_{uuid.uuid4().hex[:8]}",
            "created_at": self._created_at,
            "exported_at": datetime.utcnow().isoformat(),
            "envelope_version": ENVELOPE_VERSION,
            "schema_version": SCHEMA_VERSION,
            "event_count": len(self._events),
            "genesis_hash": "GENESIS",
            "head_hash": self._last_hash,
            "chain_valid": is_valid,
            "broken_at_index": broken_at,
            "events": self._events,
        }

    @classmethod
    def import_and_verify(
        cls,
        chain_data: dict[str, Any],
        hmac_secret: str | None = None,
    ) -> tuple[bool, Optional[int], "AuditChain"]:
        """
        Import a chain from exported data and verify its integrity.

        Returns:
          (is_valid, broken_at_index, chain_instance)
        """
        chain = cls(hmac_secret=hmac_secret)
        chain._events = chain_data.get("events", [])
        chain._created_at = chain_data.get("created_at", "")

        if chain._events:
            chain._last_hash = chain._events[-1].get("current_hash", "GENESIS")

        is_valid, broken_at = chain.verify()
        return is_valid, broken_at, chain

    def statistics(self) -> dict[str, Any]:
        """Get chain statistics for monitoring."""
        action_dist: dict[str, int] = {}
        for event in self._events:
            action = event.get("action", "UNKNOWN")
            action_dist[action] = action_dist.get(action, 0) + 1

        is_valid, broken_at = self.verify()

        return {
            "event_count": len(self._events),
            "head_hash": self._last_hash,
            "chain_valid": is_valid,
            "broken_at": broken_at,
            "action_distribution": action_dist,
            "created_at": self._created_at,
            "envelope_version": ENVELOPE_VERSION,
            "schema_version": SCHEMA_VERSION,
        }


# ── Event type constants ──────────────────────────────────────────────────────

class AuditAction:
    INGESTED = "INGESTED"
    NORMALIZED = "NORMALIZED"
    MATCH_PROPOSED = "MATCH_PROPOSED"
    MATCH_CONFIRMED = "MATCH_CONFIRMED"
    MANUAL_REVIEW_STARTED = "MANUAL_REVIEW_STARTED"
    EXCEPTION_CREATED = "EXCEPTION_CREATED"
    EXCEPTION_REVIEWED = "EXCEPTION_REVIEWED"
    EXCEPTION_RESOLVED = "EXCEPTION_RESOLVED"
    EXCEPTION_ESCALATED = "EXCEPTION_ESCALATED"
    EXPLANATION_GENERATED = "EXPLANATION_GENERATED"
    REPORT_EXPORTED = "REPORT_EXPORTED"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    TAMPER_DETECTED = "TAMPER_DETECTED"
    RECONCILIATION_STARTED = "RECONCILIATION_STARTED"
    RECONCILIATION_COMPLETED = "RECONCILIATION_COMPLETED"
    SETTLEMENT_COMPUTED = "SETTLEMENT_COMPUTED"
    SETTLEMENT_RECONCILED = "SETTLEMENT_RECONCILED"
    JOURNAL_ENTRY_POSTED = "JOURNAL_ENTRY_POSTED"
    CHAIN_EXPORTED = "CHAIN_EXPORTED"
    CHAIN_VERIFIED = "CHAIN_VERIFIED"


# ── Global chain (stateless per run — persisted to DB in production) ──────────

_global_chain = AuditChain()


def get_chain() -> AuditChain:
    return _global_chain


def reset_chain() -> AuditChain:
    """Reset for a new reconciliation run."""
    global _global_chain
    _global_chain = AuditChain()
    return _global_chain
