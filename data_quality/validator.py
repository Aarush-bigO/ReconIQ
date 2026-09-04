"""
ReconIQ Enterprise — Data Quality Validator
=============================================
Validates data quality across all ingestion sources.

Combines concepts from multiple reference repositories:
  - Schema completeness scoring per source
  - Field-level null rate tracking
  - Cross-source consistency checks
  - Anomaly detection (duplicate references, impossible amounts)

Data quality is critical for reconciliation accuracy.
Poor input data → false matches → financial loss.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class FieldQuality:
    """Quality metrics for a single field across all records."""
    field_name: str
    total_records: int = 0
    non_null_count: int = 0
    null_count: int = 0
    empty_string_count: int = 0
    distinct_values: int = 0
    null_rate: float = 0.0
    completeness: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "total_records": self.total_records,
            "non_null_count": self.non_null_count,
            "null_count": self.null_count,
            "empty_string_count": self.empty_string_count,
            "distinct_values": self.distinct_values,
            "null_rate": round(self.null_rate, 4),
            "completeness": round(self.completeness, 4),
        }


@dataclass
class SourceQuality:
    """Quality metrics for a single data source."""
    source_name: str
    record_count: int = 0
    field_quality: list[FieldQuality] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    overall_score: float = 100.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "record_count": self.record_count,
            "overall_score": round(self.overall_score, 1),
            "field_quality": [f.to_dict() for f in self.field_quality],
            "issues": self.issues,
            "issue_count": len(self.issues),
            "warnings": self.warnings,
            "warning_count": len(self.warnings),
        }


@dataclass
class DataQualityReport:
    """Complete data quality report across all sources."""
    report_id: str = ""
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    sources: list[SourceQuality] = field(default_factory=list)
    cross_source_issues: list[str] = field(default_factory=list)
    overall_score: float = 100.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "overall_score": round(self.overall_score, 1),
            "source_count": len(self.sources),
            "sources": [s.to_dict() for s in self.sources],
            "cross_source_issues": self.cross_source_issues,
            "cross_source_issue_count": len(self.cross_source_issues),
        }


# ── Required fields per source ────────────────────────────────────────────────

REQUIRED_FIELDS = {
    "razorpay": [
        "canonical_id", "payment_id", "amount_minor", "currency",
        "event_time", "reference_core", "source",
    ],
    "ledger": [
        "canonical_id", "amount_minor", "currency",
        "event_time", "reference_core", "source",
    ],
    "bank": [
        "canonical_id", "amount_minor", "currency",
        "event_time", "reference_core", "source", "utr",
    ],
}

# Fields to check for quality
ALL_FIELDS = [
    "canonical_id", "payment_id", "order_id", "settlement_id",
    "utr", "amount_minor", "fee_minor", "tax_minor",
    "currency", "event_time", "reference_core", "source",
    "source_reference",
]


def validate_source(
    source_name: str,
    records: list[dict[str, Any]],
) -> SourceQuality:
    """
    Validate data quality for a single source.
    """
    quality = SourceQuality(
        source_name=source_name,
        record_count=len(records),
    )

    if not records:
        quality.issues.append("No records found for this source")
        quality.overall_score = 0.0
        return quality

    # ── Field-level quality ───────────────────────────────────────────────
    for field_name in ALL_FIELDS:
        fq = FieldQuality(
            field_name=field_name,
            total_records=len(records),
        )

        values = []
        for record in records:
            val = record.get(field_name)
            if val is None:
                fq.null_count += 1
            elif isinstance(val, str) and val.strip() == "":
                fq.empty_string_count += 1
                fq.null_count += 1  # Treat empty strings as null for quality
            else:
                fq.non_null_count += 1
                values.append(val)

        fq.distinct_values = len(set(str(v) for v in values)) if values else 0
        fq.null_rate = fq.null_count / fq.total_records if fq.total_records > 0 else 0.0
        fq.completeness = fq.non_null_count / fq.total_records if fq.total_records > 0 else 0.0

        quality.field_quality.append(fq)

    # ── Required field checks ─────────────────────────────────────────────
    required = REQUIRED_FIELDS.get(source_name, REQUIRED_FIELDS.get("ledger", []))
    score_deductions = 0.0

    for req_field in required:
        fq_match = next(
            (f for f in quality.field_quality if f.field_name == req_field),
            None,
        )
        if fq_match:
            if fq_match.null_rate > 0.1:
                quality.issues.append(
                    f"Required field '{req_field}' has {fq_match.null_rate:.1%} null rate"
                )
                score_deductions += 10
            elif fq_match.null_rate > 0:
                quality.warnings.append(
                    f"Required field '{req_field}' has {fq_match.null_count} null values"
                )
                score_deductions += 3

    # ── Amount validation ─────────────────────────────────────────────────
    zero_amounts = sum(1 for r in records if int(r.get("amount_minor", 0)) == 0)
    negative_amounts = sum(1 for r in records if int(r.get("amount_minor", 0)) < 0)

    if zero_amounts > 0:
        quality.warnings.append(f"{zero_amounts} records have zero amount")
        score_deductions += 5

    if negative_amounts > 0:
        quality.issues.append(f"{negative_amounts} records have NEGATIVE amount (invalid)")
        score_deductions += 15

    # ── Duplicate detection ───────────────────────────────────────────────
    canonical_ids = [r.get("canonical_id", "") for r in records if r.get("canonical_id")]
    unique_ids = set(canonical_ids)
    if len(canonical_ids) != len(unique_ids):
        dup_count = len(canonical_ids) - len(unique_ids)
        quality.issues.append(f"{dup_count} duplicate canonical_id values detected")
        score_deductions += 20

    # ── Reference core quality ────────────────────────────────────────────
    ref_cores = [r.get("reference_core", "") for r in records if r.get("reference_core")]
    if ref_cores:
        unique_refs = set(ref_cores)
        dup_refs = len(ref_cores) - len(unique_refs)
        if dup_refs > len(records) * 0.1:
            quality.warnings.append(
                f"High duplicate rate in reference_core: {dup_refs} duplicates "
                f"({dup_refs / len(records):.1%})"
            )
            score_deductions += 5

    # ── Currency consistency ──────────────────────────────────────────────
    currencies = set(r.get("currency", "INR") for r in records)
    if len(currencies) > 1:
        quality.warnings.append(
            f"Multiple currencies found: {', '.join(sorted(currencies))}. "
            f"Cross-currency reconciliation may produce false mismatches."
        )
        score_deductions += 5

    quality.overall_score = max(0.0, 100.0 - score_deductions)
    return quality


def validate_all_sources(
    sources: dict[str, list[dict[str, Any]]],
) -> DataQualityReport:
    """
    Validate data quality across all sources and check cross-source consistency.
    """
    import uuid

    report = DataQualityReport(
        report_id=f"dqr_{uuid.uuid4().hex[:8]}",
    )

    # Validate each source independently
    for source_name, records in sources.items():
        source_quality = validate_source(source_name, records)
        report.sources.append(source_quality)

    # ── Cross-source consistency checks ───────────────────────────────────

    # Check record count ratios
    counts = {s.source_name: s.record_count for s in report.sources}
    if counts:
        max_count = max(counts.values())
        for name, count in counts.items():
            if max_count > 0 and count < max_count * 0.5:
                report.cross_source_issues.append(
                    f"Source '{name}' has significantly fewer records ({count}) "
                    f"than the largest source ({max_count}). Data may be incomplete."
                )

    # Check currency consistency across sources
    all_currencies: dict[str, set[str]] = {}
    for source_name, records in sources.items():
        currencies = set(r.get("currency", "INR") for r in records)
        all_currencies[source_name] = currencies

    all_unique = set()
    for c in all_currencies.values():
        all_unique.update(c)

    if len(all_unique) > 1:
        report.cross_source_issues.append(
            f"Currency mismatch across sources: "
            f"{', '.join(f'{k}: {v}' for k, v in all_currencies.items())}"
        )

    # Check date range overlap
    date_ranges: dict[str, tuple[str, str]] = {}
    for source_name, records in sources.items():
        dates = [r.get("event_time", "") for r in records if r.get("event_time")]
        if dates:
            date_ranges[source_name] = (min(dates), max(dates))

    if len(date_ranges) > 1:
        ranges = list(date_ranges.values())
        # Check if date ranges overlap
        all_mins = [r[0] for r in ranges]
        all_maxs = [r[1] for r in ranges]
        if max(all_mins) > min(all_maxs):
            report.cross_source_issues.append(
                "Date ranges across sources do not overlap. "
                "This will result in high unresolved rates."
            )

    # ── Overall score ─────────────────────────────────────────────────────
    if report.sources:
        avg_score = sum(s.overall_score for s in report.sources) / len(report.sources)
        cross_penalty = len(report.cross_source_issues) * 5
        report.overall_score = max(0.0, avg_score - cross_penalty)
    else:
        report.overall_score = 0.0

    return report
