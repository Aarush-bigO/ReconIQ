"""
ReconIQ Enterprise — Exception Reason Codes & Classification
=============================================================
Every unresolved transaction gets a deterministic classification.
No record is left without a structured reason.
"""
from enum import Enum


class ReasonCode(str, Enum):
    MISSING_COUNTERPART = "MISSING_COUNTERPART"
    AMBIGUOUS_MATCH = "AMBIGUOUS_MATCH"
    REFERENCE_MISMATCH = "REFERENCE_MISMATCH"
    DATE_DRIFT = "DATE_DRIFT"
    DUPLICATE = "DUPLICATE"
    PARTIAL_SETTLEMENT = "PARTIAL_SETTLEMENT"
    FEE_DIFFERENCE = "FEE_DIFFERENCE"
    CURRENCY_ISSUE = "CURRENCY_ISSUE"
    UNCLASSIFIED = "UNCLASSIFIED"


class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


REASON_CODE_METADATA = {
    ReasonCode.MISSING_COUNTERPART: {
        "description": "No matching record found in any counterpart source within the reconciliation window.",
        "severity": Severity.HIGH,
        "recommended_action": "Review delayed settlement exports or verify whether the source transaction was omitted.",
    },
    ReasonCode.AMBIGUOUS_MATCH: {
        "description": "Multiple candidate records found with similar attributes. System cannot determine the definitive match.",
        "severity": Severity.HIGH,
        "recommended_action": "Manual review required. Compare candidate records and confirm the correct match.",
    },
    ReasonCode.REFERENCE_MISMATCH: {
        "description": "Reference identifiers do not agree after normalization.",
        "severity": Severity.MEDIUM,
        "recommended_action": "Verify the source system reference formats and check if a manual correction is needed.",
    },
    ReasonCode.DATE_DRIFT: {
        "description": "Transaction dates differ by more than the configured tolerance window.",
        "severity": Severity.MEDIUM,
        "recommended_action": "Check settlement timing policies. May be a valid delayed credit.",
    },
    ReasonCode.DUPLICATE: {
        "description": "Multiple records in the same source appear to represent the same event.",
        "severity": Severity.HIGH,
        "recommended_action": "Investigate source system for duplicate transaction creation. Do not automatically remove any record.",
    },
    ReasonCode.PARTIAL_SETTLEMENT: {
        "description": "Payment amount does not match bank credit. May indicate a split settlement (one-to-many).",
        "severity": Severity.MEDIUM,
        "recommended_action": "Check if this payment was included in multiple settlement batches.",
    },
    ReasonCode.FEE_DIFFERENCE: {
        "description": "Amount difference matches expected fee or tax structure.",
        "severity": Severity.LOW,
        "recommended_action": "Verify fee schedule. May reconcile once fee deduction is accounted for.",
    },
    ReasonCode.CURRENCY_ISSUE: {
        "description": "Currency fields do not agree between records.",
        "severity": Severity.HIGH,
        "recommended_action": "Verify currency configuration in source systems. Do not auto-reconcile cross-currency records.",
    },
    ReasonCode.UNCLASSIFIED: {
        "description": "Exception does not match any known reason pattern.",
        "severity": Severity.MEDIUM,
        "recommended_action": "Manual investigation required.",
    },
}
