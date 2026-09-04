"""
ReconIQ Enterprise — Agent Architecture Layer
================================================
Inspired by FinRobot's multi-agent financial analysis framework.

Key principle from FinRobot: "Deterministic systems decide. AI explains."

Architecture:
  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
  │ PerceptionAgent  │────▶│  AnalysisAgent   │────▶│DecisionReporter  │
  │                  │     │                  │     │                  │
  │ Gathers evidence │     │ Formats for LLM  │     │ Creates reports  │
  │ from deterministic│     │ with strict I/O  │     │ from results     │
  │ outputs          │     │ contracts        │     │                  │
  └──────────────────┘     └──────────────────┘     └──────────────────┘

ALL agents are READ-ONLY. They never modify financial state.
They observe, format, analyze, and report — nothing more.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from llm.explain import (
    LLMExplanationOutput,
    build_evidence_payload,
    explain_exception,
    get_fallback_explanation,
)


# ── Agent Base ────────────────────────────────────────────────────────────────

@dataclass
class AgentOutput:
    """Standard output envelope for all agents."""
    agent_name: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "success"
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent_name,
            "timestamp": self.timestamp,
            "status": self.status,
            "data": self.data,
            "errors": self.errors,
        }


# ── Perception Agent ──────────────────────────────────────────────────────────
# Gathers and structures evidence from deterministic reconciliation outputs.
# Never computes financial values — only observes and organizes.

class PerceptionAgent:
    """
    Gathers structured evidence from reconciliation results.

    Inspired by FinRobot's data layer agents that collect market data
    before passing to analysis agents. Here, we collect reconciliation
    evidence before passing to the analysis and reporting agents.
    """

    AGENT_NAME = "PerceptionAgent"

    @staticmethod
    def gather_reconciliation_evidence(
        recon_output: dict[str, Any],
    ) -> AgentOutput:
        """
        Extract key metrics and patterns from a reconciliation run output.
        """
        try:
            matches = recon_output.get("matches", [])
            manual_reviews = recon_output.get("manual_review", [])
            unresolved = recon_output.get("unresolved_ids", [])
            all_ids = recon_output.get("all_ids", [])

            total = len(all_ids) if all_ids else 1
            match_count = len(matches) if isinstance(matches, list) else 0
            review_count = len(manual_reviews) if isinstance(manual_reviews, list) else 0
            unresolved_count = len(unresolved) if isinstance(unresolved, list) else 0

            # Compute probability distribution
            probabilities = []
            for m in matches:
                if isinstance(m, dict):
                    probabilities.append(m.get("probability", 0.0))

            for m in manual_reviews:
                if isinstance(m, dict):
                    probabilities.append(m.get("probability", 0.0))

            avg_prob = sum(probabilities) / len(probabilities) if probabilities else 0.0
            min_prob = min(probabilities) if probabilities else 0.0
            max_prob = max(probabilities) if probabilities else 0.0

            # Reason code distribution
            reason_codes: dict[str, int] = {}
            for m in manual_reviews:
                if isinstance(m, dict):
                    rc = m.get("reason_code", "UNKNOWN")
                    reason_codes[rc] = reason_codes.get(rc, 0) + 1

            evidence = {
                "total_records": total,
                "auto_matched": match_count,
                "manual_review": review_count,
                "unresolved": unresolved_count,
                "match_rate": round(match_count / total, 4) if total > 0 else 0.0,
                "review_rate": round(review_count / total, 4) if total > 0 else 0.0,
                "unresolved_rate": round(unresolved_count / total, 4) if total > 0 else 0.0,
                "probability_stats": {
                    "avg": round(avg_prob, 4),
                    "min": round(min_prob, 4),
                    "max": round(max_prob, 4),
                    "count": len(probabilities),
                },
                "reason_code_distribution": reason_codes,
                "run_id": recon_output.get("run_id", ""),
                "processing_ms": recon_output.get("processing_ms", 0),
            }

            return AgentOutput(
                agent_name=PerceptionAgent.AGENT_NAME,
                data=evidence,
            )

        except Exception as e:
            return AgentOutput(
                agent_name=PerceptionAgent.AGENT_NAME,
                status="error",
                errors=[str(e)],
            )

    @staticmethod
    def gather_exception_evidence(
        exceptions: list[dict[str, Any]],
    ) -> AgentOutput:
        """
        Gather evidence from exception records for analysis.
        """
        try:
            severity_dist: dict[str, int] = {}
            reason_dist: dict[str, int] = {}
            total_amount = 0

            for exc in exceptions:
                sev = exc.get("severity", "MEDIUM")
                severity_dist[sev] = severity_dist.get(sev, 0) + 1

                rc = exc.get("reason_code", "UNCLASSIFIED")
                reason_dist[rc] = reason_dist.get(rc, 0) + 1

                total_amount += int(exc.get("amount_minor", 0))

            return AgentOutput(
                agent_name=PerceptionAgent.AGENT_NAME,
                data={
                    "exception_count": len(exceptions),
                    "total_amount_at_risk_minor": total_amount,
                    "total_amount_at_risk": total_amount / 100,
                    "severity_distribution": severity_dist,
                    "reason_distribution": reason_dist,
                },
            )

        except Exception as e:
            return AgentOutput(
                agent_name=PerceptionAgent.AGENT_NAME,
                status="error",
                errors=[str(e)],
            )


# ── Analysis Agent ────────────────────────────────────────────────────────────
# Takes structured evidence and generates AI explanations.
# Strictly bounded input/output — LLM only sees sanitized evidence.

class AnalysisAgent:
    """
    Formats evidence for LLM analysis and processes responses.

    Inspired by FinRobot's analysis layer that separates
    deterministic computation from LLM narration.

    The AnalysisAgent NEVER modifies financial data.
    It only reads evidence and produces explanations.
    """

    AGENT_NAME = "AnalysisAgent"

    @staticmethod
    def analyze_exceptions(
        exceptions: list[dict[str, Any]],
        api_key: str = "",
    ) -> AgentOutput:
        """
        Generate AI explanations for a batch of exceptions.
        Falls back to deterministic explanations if no API key.
        """
        results = []

        for exc in exceptions:
            explanation, source = explain_exception(exc, api_key=api_key)
            results.append({
                "exception_id": exc.get("exception_id", ""),
                "reason_code": exc.get("reason_code", "UNCLASSIFIED"),
                "explanation": explanation.explanation,
                "recommended_action": explanation.recommended_action,
                "source": source,
            })

        return AgentOutput(
            agent_name=AnalysisAgent.AGENT_NAME,
            data={
                "explanations": results,
                "total_analyzed": len(results),
                "llm_count": sum(1 for r in results if r["source"] == "llm"),
                "fallback_count": sum(1 for r in results if r["source"] == "fallback"),
            },
        )

    @staticmethod
    def analyze_reconciliation_quality(
        perception_output: AgentOutput,
    ) -> AgentOutput:
        """
        Analyze the quality of a reconciliation run based on perception evidence.
        Pure deterministic analysis — no LLM involved.
        """
        data = perception_output.data
        match_rate = data.get("match_rate", 0.0)
        unresolved_rate = data.get("unresolved_rate", 0.0)

        # Quality scoring (deterministic rules)
        quality_score = 100.0
        findings = []

        if match_rate < 0.8:
            quality_score -= 30
            findings.append(
                f"Match rate ({match_rate:.1%}) is below the 80% target. "
                f"Review blocking rules and comparison settings."
            )

        if unresolved_rate > 0.15:
            quality_score -= 20
            findings.append(
                f"Unresolved rate ({unresolved_rate:.1%}) exceeds 15% threshold. "
                f"Check for missing source data or reference normalization issues."
            )

        prob_stats = data.get("probability_stats", {})
        avg_prob = prob_stats.get("avg", 0.0)
        if avg_prob < 0.7:
            quality_score -= 15
            findings.append(
                f"Average match probability ({avg_prob:.3f}) is low. "
                f"Consider re-training the Splink model or adjusting priors."
            )

        reason_dist = data.get("reason_code_distribution", {})
        if reason_dist.get("MISSING_COUNTERPART", 0) > 5:
            quality_score -= 10
            findings.append(
                f"High count of MISSING_COUNTERPART exceptions. "
                f"Verify data completeness across all sources."
            )

        quality_score = max(0.0, quality_score)

        return AgentOutput(
            agent_name=AnalysisAgent.AGENT_NAME,
            data={
                "quality_score": round(quality_score, 1),
                "quality_grade": (
                    "A" if quality_score >= 90 else
                    "B" if quality_score >= 75 else
                    "C" if quality_score >= 60 else
                    "D" if quality_score >= 40 else "F"
                ),
                "findings": findings,
                "finding_count": len(findings),
            },
        )


# ── Decision Report Agent ────────────────────────────────────────────────────
# Generates human-readable reports from deterministic results.

class DecisionReportAgent:
    """
    Generates structured reports from reconciliation results.

    Inspired by FinRobot's report generation layer.
    Creates executive summaries, detail reports, and action items.
    """

    AGENT_NAME = "DecisionReportAgent"

    @staticmethod
    def generate_executive_summary(
        perception_output: AgentOutput,
        analysis_output: AgentOutput,
    ) -> AgentOutput:
        """
        Generate an executive summary combining perception and analysis.
        """
        perc = perception_output.data
        analysis = analysis_output.data

        total = perc.get("total_records", 0)
        matched = perc.get("auto_matched", 0)
        review = perc.get("manual_review", 0)
        unresolved = perc.get("unresolved", 0)
        quality = analysis.get("quality_score", 0.0)
        grade = analysis.get("quality_grade", "N/A")

        summary_lines = [
            f"Reconciliation Run Summary",
            f"═" * 40,
            f"Records Processed:  {total:,}",
            f"Auto-Matched:       {matched:,} ({perc.get('match_rate', 0):.1%})",
            f"Manual Review:      {review:,} ({perc.get('review_rate', 0):.1%})",
            f"Unresolved:         {unresolved:,} ({perc.get('unresolved_rate', 0):.1%})",
            f"",
            f"Quality Score:      {quality:.1f}/100 (Grade: {grade})",
            f"Processing Time:    {perc.get('processing_ms', 0):,}ms",
        ]

        findings = analysis.get("findings", [])
        if findings:
            summary_lines.append("")
            summary_lines.append("Findings:")
            for i, finding in enumerate(findings, 1):
                summary_lines.append(f"  {i}. {finding}")

        action_items = []
        if unresolved > 0:
            action_items.append(
                f"Review {unresolved} unresolved records and assign to finance team"
            )
        if review > 0:
            action_items.append(
                f"Process {review} manual review items by SLA deadline"
            )
        if quality < 75:
            action_items.append(
                "Investigate data quality issues before next reconciliation run"
            )

        return AgentOutput(
            agent_name=DecisionReportAgent.AGENT_NAME,
            data={
                "summary_text": "\n".join(summary_lines),
                "action_items": action_items,
                "kpis": {
                    "total_records": total,
                    "auto_matched": matched,
                    "manual_review": review,
                    "unresolved": unresolved,
                    "match_rate": perc.get("match_rate", 0),
                    "quality_score": quality,
                    "quality_grade": grade,
                },
            },
        )


# ── Agent Pipeline Orchestrator ───────────────────────────────────────────────

def run_agent_pipeline(
    recon_output: dict[str, Any],
    exceptions: list[dict[str, Any]] | None = None,
    api_key: str = "",
) -> dict[str, AgentOutput]:
    """
    Run the full agent pipeline:
      1. PerceptionAgent gathers evidence
      2. AnalysisAgent analyzes quality
      3. DecisionReportAgent generates summary

    All agents are read-only. No financial state is modified.

    Returns a dict of agent name → AgentOutput.
    """
    # Stage 1: Perception
    perception = PerceptionAgent.gather_reconciliation_evidence(recon_output)

    # Stage 2: Analysis
    quality_analysis = AnalysisAgent.analyze_reconciliation_quality(perception)

    exception_analysis = None
    if exceptions:
        exception_perception = PerceptionAgent.gather_exception_evidence(exceptions)
        exception_analysis = AnalysisAgent.analyze_exceptions(
            exceptions, api_key=api_key
        )

    # Stage 3: Report
    report = DecisionReportAgent.generate_executive_summary(
        perception, quality_analysis
    )

    results = {
        "perception": perception,
        "quality_analysis": quality_analysis,
        "report": report,
    }

    if exception_analysis:
        results["exception_analysis"] = exception_analysis

    return results
