"""
ReconIQ Enterprise — Exception Manager
=========================================
Inspired by Financial Transaction Reconciliation's practical workflows.

Features:
  - Exception aging with SLA tracking
  - Priority scoring based on amount, age, and severity
  - Operator assignment and resolution tracking
  - Exception queue with filtering and sorting

Exception Lifecycle:
  OPEN → ASSIGNED → IN_REVIEW → RESOLVED | ESCALATED
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional


class ExceptionStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class ExceptionSeverity(str, Enum):
    CRITICAL = "CRITICAL"   # > ₹1,00,000 or system integrity issue
    HIGH = "HIGH"           # > ₹10,000 or pattern anomaly
    MEDIUM = "MEDIUM"       # Standard exceptions
    LOW = "LOW"             # Minor discrepancies


class ResolutionType(str, Enum):
    MANUAL_MATCH = "MANUAL_MATCH"        # Analyst confirmed the match
    FALSE_POSITIVE = "FALSE_POSITIVE"    # Exception was a false alarm
    DATA_FIX = "DATA_FIX"               # Source data was corrected
    WRITE_OFF = "WRITE_OFF"             # Amount written off (authorized)
    DUPLICATE_REMOVED = "DUPLICATE_REMOVED"  # Duplicate record removed
    ESCALATED_TO_GATEWAY = "ESCALATED_TO_GATEWAY"  # Sent to Razorpay support
    OTHER = "OTHER"


# SLA deadlines by severity (in hours)
SLA_HOURS = {
    ExceptionSeverity.CRITICAL: 4,
    ExceptionSeverity.HIGH: 24,
    ExceptionSeverity.MEDIUM: 72,
    ExceptionSeverity.LOW: 168,  # 7 days
}


@dataclass
class ExceptionRecord:
    """
    A single exception requiring investigation.
    Includes aging, assignment, and resolution tracking.
    """
    exception_id: str
    run_id: str
    record_id: str
    reason_code: str
    severity: ExceptionSeverity
    amount_minor: int
    currency: str = "INR"

    # Evidence
    evidence_json: dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    recommended_action: str = ""
    deduction_category: Optional[str] = None

    # Lifecycle
    status: ExceptionStatus = ExceptionStatus.OPEN
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Assignment
    assigned_to: str = ""
    assigned_at: str = ""

    # Resolution
    resolution_type: Optional[ResolutionType] = None
    resolution_notes: str = ""
    resolved_at: str = ""
    resolved_by: str = ""

    # Priority (computed)
    priority_score: float = 0.0

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def age_hours(self) -> float:
        """How old is this exception in hours."""
        created = datetime.fromisoformat(self.created_at)
        return (datetime.now(timezone.utc) - created).total_seconds() / 3600

    @property
    def age_days(self) -> float:
        """How old is this exception in days."""
        return self.age_hours / 24

    @property
    def sla_deadline(self) -> str:
        """ISO timestamp of the SLA deadline."""
        created = datetime.fromisoformat(self.created_at)
        hours = SLA_HOURS.get(self.severity, 72)
        deadline = created + timedelta(hours=hours)
        return deadline.isoformat()

    @property
    def sla_remaining_hours(self) -> float:
        """Hours remaining until SLA breach. Negative if breached."""
        deadline = datetime.fromisoformat(self.sla_deadline)
        remaining = (deadline - datetime.now(timezone.utc)).total_seconds() / 3600
        return round(remaining, 2)

    @property
    def is_sla_breached(self) -> bool:
        """Whether the SLA deadline has passed."""
        return self.sla_remaining_hours < 0

    def compute_priority(self) -> float:
        """
        Compute priority score (higher = more urgent).

        Factors:
          - Severity weight (CRITICAL=100, HIGH=75, MEDIUM=50, LOW=25)
          - Amount weight (scaled logarithmically)
          - Age weight (increases with time)
          - SLA breach penalty (+50 if breached)
        """
        severity_weights = {
            ExceptionSeverity.CRITICAL: 100,
            ExceptionSeverity.HIGH: 75,
            ExceptionSeverity.MEDIUM: 50,
            ExceptionSeverity.LOW: 25,
        }

        # Base severity score
        score = float(severity_weights.get(self.severity, 50))

        # Amount factor (logarithmic scale, ₹100 = +10, ₹10000 = +20, ₹100000 = +30)
        import math
        if self.amount_minor > 0:
            score += min(30, math.log10(self.amount_minor / 100 + 1) * 10)

        # Age factor (older = higher priority)
        score += min(20, self.age_hours / 4)

        # SLA breach penalty
        if self.is_sla_breached:
            score += 50

        self.priority_score = round(score, 2)
        return self.priority_score

    def assign(self, operator: str) -> None:
        """Assign this exception to an operator."""
        self.assigned_to = operator
        self.assigned_at = datetime.now(timezone.utc).isoformat()
        self.status = ExceptionStatus.ASSIGNED
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def start_review(self) -> None:
        """Mark exception as being actively reviewed."""
        self.status = ExceptionStatus.IN_REVIEW
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def resolve(
        self,
        resolution_type: ResolutionType,
        notes: str = "",
        resolved_by: str = "",
    ) -> None:
        """Resolve this exception."""
        self.status = ExceptionStatus.RESOLVED
        self.resolution_type = resolution_type
        self.resolution_notes = notes
        self.resolved_by = resolved_by
        self.resolved_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def escalate(self, notes: str = "") -> None:
        """Escalate this exception."""
        self.status = ExceptionStatus.ESCALATED
        self.resolution_notes = notes
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "exception_id": self.exception_id,
            "run_id": self.run_id,
            "record_id": self.record_id,
            "reason_code": self.reason_code,
            "severity": self.severity.value,
            "amount_minor": self.amount_minor,
            "amount": self.amount_minor / 100,
            "currency": self.currency,
            "status": self.status.value,
            "created_at": self.created_at,
            "age_hours": round(self.age_hours, 2),
            "age_days": round(self.age_days, 2),
            "sla_deadline": self.sla_deadline,
            "sla_remaining_hours": self.sla_remaining_hours,
            "is_sla_breached": self.is_sla_breached,
            "priority_score": self.priority_score,
            "assigned_to": self.assigned_to,
            "assigned_at": self.assigned_at,
            "resolution_type": self.resolution_type.value if self.resolution_type else None,
            "resolution_notes": self.resolution_notes,
            "resolved_at": self.resolved_at,
            "resolved_by": self.resolved_by,
            "explanation": self.explanation,
            "recommended_action": self.recommended_action,
            "deduction_category": self.deduction_category,
            "evidence_json": self.evidence_json,
        }


# ── Exception Queue ───────────────────────────────────────────────────────────

class ExceptionQueue:
    """
    Priority-sorted exception queue with filtering.
    Inspired by Financial Transaction Reconciliation's workflow management.
    """

    def __init__(self):
        self._exceptions: dict[str, ExceptionRecord] = {}

    def add(self, exception: ExceptionRecord) -> None:
        """Add an exception and compute its priority."""
        exception.compute_priority()
        self._exceptions[exception.exception_id] = exception

    def get(self, exception_id: str) -> Optional[ExceptionRecord]:
        """Get a specific exception by ID."""
        return self._exceptions.get(exception_id)

    def assign(self, exception_id: str, operator: str) -> bool:
        """Assign an exception to an operator."""
        exc = self._exceptions.get(exception_id)
        if exc:
            exc.assign(operator)
            return True
        return False

    def resolve(
        self,
        exception_id: str,
        resolution_type: ResolutionType,
        notes: str = "",
        resolved_by: str = "",
    ) -> bool:
        """Resolve an exception."""
        exc = self._exceptions.get(exception_id)
        if exc:
            exc.resolve(resolution_type, notes, resolved_by)
            return True
        return False

    def list_by_priority(
        self,
        status_filter: Optional[ExceptionStatus] = None,
        severity_filter: Optional[ExceptionSeverity] = None,
        assigned_to_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ExceptionRecord]:
        """
        List exceptions sorted by priority (highest first).
        Supports filtering by status, severity, and assignment.
        """
        # Recompute priorities (they change with time)
        for exc in self._exceptions.values():
            exc.compute_priority()

        exceptions = list(self._exceptions.values())

        # Apply filters
        if status_filter:
            exceptions = [e for e in exceptions if e.status == status_filter]
        if severity_filter:
            exceptions = [e for e in exceptions if e.severity == severity_filter]
        if assigned_to_filter:
            exceptions = [e for e in exceptions if e.assigned_to == assigned_to_filter]

        # Sort by priority (highest first)
        exceptions.sort(key=lambda e: e.priority_score, reverse=True)

        # Paginate
        return exceptions[offset:offset + limit]

    def sla_breached(self) -> list[ExceptionRecord]:
        """Get all exceptions that have breached their SLA."""
        return [
            exc for exc in self._exceptions.values()
            if exc.is_sla_breached and exc.status not in (
                ExceptionStatus.RESOLVED, ExceptionStatus.CLOSED
            )
        ]

    def summary(self) -> dict[str, Any]:
        """Get a summary of the exception queue."""
        all_exc = list(self._exceptions.values())
        open_exc = [e for e in all_exc if e.status in (
            ExceptionStatus.OPEN, ExceptionStatus.ASSIGNED, ExceptionStatus.IN_REVIEW
        )]
        breached = self.sla_breached()

        total_amount = sum(e.amount_minor for e in open_exc)

        status_dist = {}
        severity_dist = {}
        for e in all_exc:
            status_dist[e.status.value] = status_dist.get(e.status.value, 0) + 1
            severity_dist[e.severity.value] = severity_dist.get(e.severity.value, 0) + 1

        return {
            "total_exceptions": len(all_exc),
            "open_exceptions": len(open_exc),
            "sla_breached": len(breached),
            "total_amount_at_risk_minor": total_amount,
            "total_amount_at_risk": total_amount / 100,
            "status_distribution": status_dist,
            "severity_distribution": severity_dist,
        }

    @property
    def count(self) -> int:
        return len(self._exceptions)


# ── Global exception queue ────────────────────────────────────────────────────

_global_queue = ExceptionQueue()


def get_exception_queue() -> ExceptionQueue:
    return _global_queue


def reset_exception_queue() -> ExceptionQueue:
    global _global_queue
    _global_queue = ExceptionQueue()
    return _global_queue
