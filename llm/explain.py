"""
ReconIQ Enterprise — LLM Explanation Engine
============================================
Uses bounded structured evidence to generate human-readable exception explanations.

AI Safety Contract:
  INPUT:  Structured deterministic evidence (JSON schema)
  OUTPUT: explanation + recommended_action ONLY
  
  LLM CANNOT:
    - change amount
    - change currency  
    - change decision
    - change confidence
    - create a match
    - delete an exception
    - invent transaction IDs
    - invent evidence
    - write to financial state

  Only accepted output fields: explanation, recommended_action

If OPENAI_API_KEY is missing → deterministic rule-based fallback.
Core application remains fully functional.
"""
import json
import os
from typing import Any, Optional
from pydantic import BaseModel, ValidationError


# ── Output schema (strict — LLM output must conform) ─────────────────────────

class LLMExplanationOutput(BaseModel):
    """The ONLY fields the LLM is permitted to populate."""
    explanation: str
    recommended_action: str


# ── Evidence builder ──────────────────────────────────────────────────────────

def build_evidence_payload(exception: dict[str, Any]) -> dict[str, Any]:
    """
    Build a bounded evidence JSON for LLM input.
    Never passes raw financial records — only structured metrics.
    """
    return {
        "decision": "UNRESOLVED",
        "reason_code": exception.get("reason_code", "UNCLASSIFIED"),
        "amount_minor": exception.get("amount_minor", 0),
        "currency": exception.get("evidence_json", {}).get("currency", "INR"),
        "candidate_count": exception.get("candidate_count", 0),
        "search_window_days": exception.get("window_days", 3),
        "severity": exception.get("severity", "MEDIUM"),
        "evidence_summary": {
            k: v
            for k, v in (exception.get("evidence_json") or {}).items()
            if k in [
                "amount_delta", "transaction_ref_core", "candidate_ref_core",
                "transaction_currency", "candidate_currency",
                "top_candidates",
            ]
        },
    }


# ── Deterministic fallback ────────────────────────────────────────────────────

FALLBACK_EXPLANATIONS = {
    "MISSING_COUNTERPART": (
        "No corresponding payment or bank credit record was identified "
        "within the configured reconciliation window.",
        "Review delayed settlement exports or verify whether the source "
        "transaction was included in the data extract.",
    ),
    "AMBIGUOUS_MATCH": (
        "Multiple candidate records were identified with similar attributes. "
        "The reconciliation engine cannot determine the definitive match without human review.",
        "Compare the candidate records side-by-side and confirm the correct match. "
        "Check payment IDs and order references for disambiguation.",
    ),
    "REFERENCE_MISMATCH": (
        "The reference identifiers across sources do not agree after normalization. "
        "The transactions may represent the same event under different reference conventions.",
        "Verify the reference format used by each source system and check "
        "whether a manual reference mapping is required.",
    ),
    "DATE_DRIFT": (
        "The transaction dates differ by more than the configured tolerance window. "
        "This may reflect a valid settlement delay.",
        "Review the settlement timing policy and verify whether the bank credit "
        "was delayed due to a weekend or banking holiday.",
    ),
    "DUPLICATE": (
        "Multiple records in the same source appear to represent the same economic event. "
        "This may indicate a duplicate submission or a processing error.",
        "Investigate the source system for duplicate transaction creation. "
        "Do not automatically delete any record — confirm the canonical record first.",
    ),
    "PARTIAL_SETTLEMENT": (
        "The payment amount does not match the bank credit amount. "
        "This may indicate a split settlement across multiple batches.",
        "Check whether this payment was included in multiple settlement cycles. "
        "Sum the related bank credits to verify the total matches the gross payment.",
    ),
    "FEE_DIFFERENCE": (
        "A small amount difference was detected that is consistent with a fee or tax deduction. "
        "The net settlement may reconcile once the fee structure is applied.",
        "Verify the applicable fee schedule for this payment method. "
        "Apply the fee and tax deduction model and re-evaluate the net settlement amount.",
    ),
    "CURRENCY_ISSUE": (
        "The currency fields do not agree between source records. "
        "Cross-currency records cannot be automatically reconciled.",
        "Verify the currency configuration in each source system. "
        "Do not reconcile records with differing currencies without explicit confirmation.",
    ),
    "UNCLASSIFIED": (
        "This exception does not match any known pattern. "
        "Manual investigation is required.",
        "Review the full transaction record and compare against available counterpart data.",
    ),
}


def get_fallback_explanation(reason_code: str) -> LLMExplanationOutput:
    """Return deterministic rule-based explanation when LLM is unavailable."""
    explanation, action = FALLBACK_EXPLANATIONS.get(
        reason_code,
        FALLBACK_EXPLANATIONS["UNCLASSIFIED"],
    )
    return LLMExplanationOutput(
        explanation=explanation,
        recommended_action=action,
    )


# ── OpenAI explanation ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a financial reconciliation assistant for ReconIQ Enterprise.

Your ONLY task is to explain why a transaction was flagged as an exception 
and recommend a next action for a finance analyst.

Rules you MUST follow:
1. Output ONLY valid JSON with exactly these two fields: "explanation" and "recommended_action"
2. Do NOT invent transaction IDs, amounts, dates, or any financial data
3. Do NOT change the decision, confidence, or any structured fields
4. Do NOT suggest automatic resolution — only human review actions
5. Keep explanations factual, professional, and concise (2-3 sentences max)
6. Never use: "I", "we", "AI", "machine learning", "algorithm"
7. Use present tense and professional finance terminology

Example output:
{
  "explanation": "No matching bank credit was found within the 3-day reconciliation window for this ₹14,800 payment.",
  "recommended_action": "Verify that the settlement batch for this date was exported and check for delayed bank processing."
}"""


def explain_exception(
    exception: dict[str, Any],
    api_key: str = "",
    model: str = "gemini-3.6-flash",
) -> tuple[LLMExplanationOutput, str]:
    """
    Generate an AI explanation for an exception.

    Returns: (LLMExplanationOutput, source) where source is "llm" or "fallback"
    """
    reason_code = exception.get("reason_code", "UNCLASSIFIED")
    evidence = build_evidence_payload(exception)

    # Use fallback if no API key
    if not api_key or api_key.startswith("sk-your"):
        return get_fallback_explanation(reason_code), "fallback"

    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model,
            contents=f"Exception evidence:\n{json.dumps(evidence, indent=2)}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=LLMExplanationOutput,
                temperature=0.1,
            )
        )

        raw_output = response.text or "{}"
        parsed = json.loads(raw_output)

        # ── Strict schema validation ──────────────────────────────────────
        # ONLY accepted fields: explanation, recommended_action
        allowed_fields = {"explanation", "recommended_action"}
        if not all(k in allowed_fields for k in parsed.keys()):
            raise ValueError(f"LLM returned disallowed fields: {set(parsed.keys()) - allowed_fields}")

        output = LLMExplanationOutput(**parsed)
        return output, "llm"

    except (ValidationError, ValueError, json.JSONDecodeError, KeyError) as e:
        # Schema validation failure — use fallback
        print(f"[LLM] Schema validation failed: {e}. Using fallback.")
        return get_fallback_explanation(reason_code), "fallback"

    except Exception as e:
        # API failure — use fallback
        print(f"[LLM] API call failed: {e}. Using fallback.")
        return get_fallback_explanation(reason_code), "fallback"
