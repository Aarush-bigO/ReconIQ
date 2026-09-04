"""
Unit tests for normalization, audit chain, and exception classification.
"""
import pytest
from ingestion.normalize import normalize_reference, normalize_amount, normalize_currency
from audit.audit_log import AuditChain, AuditAction
from exceptions.reason_codes import ReasonCode, REASON_CODE_METADATA


# ── Normalization tests ───────────────────────────────────────────────────────

class TestNormalization:
    def test_pay_prefix_stripped(self):
        result = normalize_reference("PAY-82917")
        assert result.normalized == "82917"
        assert "PAY-" in result.prefixes_stripped

    def test_utr_prefix_stripped(self):
        result = normalize_reference("UTR-82917")
        assert result.normalized == "82917"

    def test_neft_prefix_stripped(self):
        result = normalize_reference("NEFT82917")
        assert result.normalized == "82917"

    def test_payment_underscore_stripped(self):
        result = normalize_reference("payment_82917")
        assert result.normalized == "82917"

    def test_txn_prefix_stripped(self):
        result = normalize_reference("TXN-82917")
        assert result.normalized == "82917"

    def test_cross_source_same_core(self):
        """The core normalization challenge — different formats, same core."""
        refs = ["PAY-82917", "UTR-82917", "payment_82917", "NEFT82917", "TXN-82917"]
        cores = [normalize_reference(r).normalized for r in refs]
        assert all(c == "82917" for c in cores), f"Expected all 82917, got: {cores}"

    def test_empty_reference(self):
        result = normalize_reference("")
        assert result.normalized == ""
        assert result.normalizer == "empty"

    def test_no_prefix(self):
        result = normalize_reference("82917")
        assert result.normalized == "82917"
        assert result.normalizer == "passthrough"

    def test_led_prefix_stripped(self):
        result = normalize_reference("LED-1042")
        assert result.normalized == "1042"


class TestAmountNormalization:
    def test_integer_string(self):
        assert normalize_amount("425000") == 425000

    def test_float_string(self):
        assert normalize_amount("4250.50") == 4250

    def test_zero(self):
        assert normalize_amount("0") == 0

    def test_empty_string(self):
        assert normalize_amount("") == 0

    def test_comma_separated(self):
        assert normalize_amount("1,00,000") == 100000

    def test_with_rupee_symbol(self):
        assert normalize_amount("₹4250") == 4250


class TestCurrencyNormalization:
    def test_inr(self):
        assert normalize_currency("INR") == "INR"

    def test_lowercase_inr(self):
        assert normalize_currency("inr") == "INR"

    def test_rupee_symbol(self):
        assert normalize_currency("₹") == "INR"


# ── Audit chain tests ─────────────────────────────────────────────────────────

class TestAuditChain:
    def test_clean_chain_verifies(self):
        chain = AuditChain()
        chain.record("run_1", "txn_001", AuditAction.INGESTED)
        chain.record("run_1", "txn_001", AuditAction.MATCH_CONFIRMED, decision="AUTO_MATCH", confidence=0.98)
        is_valid, broken = chain.verify()
        assert is_valid is True
        assert broken is None

    def test_tampered_event_fails(self):
        chain = AuditChain()
        chain.record("run_1", "txn_001", AuditAction.INGESTED)
        chain.record("run_1", "txn_001", AuditAction.MATCH_CONFIRMED, decision="AUTO_MATCH", confidence=0.98)

        # Tamper with first event
        chain._events[0]["decision"] = "MATCH"

        is_valid, broken = chain.verify()
        assert is_valid is False
        assert broken == 0

    def test_removed_event_fails(self):
        chain = AuditChain()
        chain.record("run_1", "txn_001", AuditAction.INGESTED)
        chain.record("run_1", "txn_001", AuditAction.NORMALIZED)
        chain.record("run_1", "txn_001", AuditAction.MATCH_CONFIRMED)

        # Remove event 1 (middle)
        chain._events.pop(1)

        is_valid, broken = chain.verify()
        assert is_valid is False

    def test_empty_chain_verifies(self):
        chain = AuditChain()
        is_valid, broken = chain.verify()
        assert is_valid is True
        assert broken is None

    def test_event_count(self):
        chain = AuditChain()
        for i in range(5):
            chain.record("run_1", f"txn_{i:03d}", AuditAction.INGESTED)
        assert chain.event_count() == 5

    def test_hash_changes_with_each_event(self):
        chain = AuditChain()
        chain.record("run_1", "txn_001", AuditAction.INGESTED)
        hash1 = chain.last_hash()
        chain.record("run_1", "txn_002", AuditAction.INGESTED)
        hash2 = chain.last_hash()
        assert hash1 != hash2


# ── Reason codes tests ────────────────────────────────────────────────────────

class TestReasonCodes:
    def test_all_codes_have_metadata(self):
        for code in ReasonCode:
            assert code in REASON_CODE_METADATA, f"{code} missing from REASON_CODE_METADATA"

    def test_missing_counterpart_is_high_severity(self):
        from exceptions.reason_codes import Severity
        meta = REASON_CODE_METADATA[ReasonCode.MISSING_COUNTERPART]
        assert meta["severity"] == Severity.HIGH

    def test_currency_issue_is_high_severity(self):
        from exceptions.reason_codes import Severity
        meta = REASON_CODE_METADATA[ReasonCode.CURRENCY_ISSUE]
        assert meta["severity"] == Severity.HIGH

    def test_fee_difference_is_low_severity(self):
        from exceptions.reason_codes import Severity
        meta = REASON_CODE_METADATA[ReasonCode.FEE_DIFFERENCE]
        assert meta["severity"] == Severity.LOW
