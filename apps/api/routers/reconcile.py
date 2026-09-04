"""
ReconIQ Enterprise — Reconciliation Router
=============================================
Orchestrates the full reconciliation pipeline incorporating all enterprise modules:
  - Splink Probabilistic Linkage
  - Data Quality Validation
  - Double-Entry Accounting Ledger
  - Settlement Reconciliation
  - Agent Architecture Pipeline
  - Exception Management
  - Tamper-Evident Audit Logging
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.api.config import get_settings
from ingestion.loaders import load_all_sources, records_to_dict_list
from matching.run_splink import run_multi_source_linkage
from matching.reconcile import reconcile, ReconciliationRunConfig
from matching.metrics import load_ground_truth, compute_metrics
from exceptions.classifier import classify_all_exceptions

# Enterprise Modules
from audit.audit_log import AuditChain, get_chain, reset_chain, AuditAction
from data_quality.validator import validate_all_sources
from accounting.ledger import LedgerState, journal_payment_capture
from settlements.engine import compute_settlement_breakdown
from settlements.reconciler import reconcile_all_settlements
from llm.agent_layer import run_agent_pipeline
from apps.api.routers.exceptions_router import set_exceptions
from apps.api.routers.settlements import (
    set_settlement_batches, 
    set_settlement_recon_results,
    set_settlements
)
from apps.api.routers.reports import set_latest_report
from database.session import SyncSessionLocal
from database.models import ReconciliationRun, Match, MatchCandidate, Transaction

router = APIRouter()
settings = get_settings()

# In-memory store fallback for demo purposes where necessary
_runs: dict[str, Any] = {}
_latest_ledger = LedgerState()


class ReconcileRequest(BaseModel):
    auto_match_threshold: float = 0.95
    review_threshold: float = 0.70
    date_tolerance_days: int = 3
    amount_tolerance_minor: int = 100
    use_razorpay_api: bool = False


@router.post("")
def run_reconciliation(req: ReconcileRequest):
    """Run the complete enterprise reconciliation pipeline."""
    run_id = f"recon_{uuid.uuid4().hex[:8]}"
    db = SyncSessionLocal()
    chain = AuditChain(db_session=db)

    # Record run start
    chain.record(run_id, run_id, AuditAction.RECONCILIATION_STARTED)

    try:
        # ── 1. Load Sources & Data Quality ────────────────────────────────────
        config = ReconciliationRunConfig(
            auto_match_threshold=req.auto_match_threshold,
            review_threshold=req.review_threshold,
            date_tolerance_days=req.date_tolerance_days,
            amount_tolerance_minor=req.amount_tolerance_minor,
        )

        sources_canonical = load_all_sources()
        sources_dict: dict[str, list[dict]] = {}
        for source_name, records in sources_canonical.items():
            dict_records = records_to_dict_list(records)
            sources_dict[source_name] = dict_records
            chain.record(run_id, source_name, AuditAction.INGESTED,
                         extra={"record_count": len(dict_records)})

        # Validate Data Quality
        dq_report = validate_all_sources(sources_dict)

        # ── 2. Splink Linkage & Match Policy ──────────────────────────────────
        predictions = run_multi_source_linkage(sources_dict)
        output = reconcile(sources_dict, predictions, config)

        for match in output.matches:
            chain.record(
                run_id, match.left_id, AuditAction.MATCH_CONFIRMED,
                decision=match.decision,
                confidence=match.probability,
                reason_code=match.reason_code,
            )

        # ── 3. Exception Classification & Queue ───────────────────────────────
        unresolved_records = [
            r for source_records in sources_dict.values()
            for r in source_records
            if r["canonical_id"] in output.unresolved_ids
        ]
        right_records = sources_dict.get("razorpay", []) + sources_dict.get("bank", [])
        exceptions = classify_all_exceptions(
            unresolved_records, right_records, predictions, config.dict()
        )
        
        # Populate FTR-inspired exception queue
        exc_dicts = [
            {
                "exception_id": f"exc_{uuid.uuid4().hex[:8]}",
                "run_id": run_id,
                "record_id": e.transaction_id,
                "reason_code": e.reason_code,
                "severity": e.severity,
                "amount_minor": e.amount_minor,
                "currency": "INR",
                "evidence_json": e.evidence_json,
                "candidate_count": e.candidate_count,
            }
            for e in exceptions
        ]
        set_exceptions(exc_dicts)

        for exc in exc_dicts:
            chain.record(run_id, exc["record_id"], AuditAction.EXCEPTION_CREATED,
                         reason_code=exc["reason_code"])

        # ── 4. Double-Entry Accounting ────────────────────────────────────────
        # Post journal entries for all EXACT matches (Sales Revenue)
        global _latest_ledger
        ledger = LedgerState(db_session=db)
        
        matched_payment_ids = set()
        for match in output.matches:
            amount = match.evidence.get("left_amount", 0)
            payment_id = match.evidence.get("left_payment_id", match.left_id)
            if amount > 0 and payment_id not in matched_payment_ids:
                try:
                    je = journal_payment_capture(payment_id, amount)
                    ledger.post(je)
                    matched_payment_ids.add(payment_id)
                    chain.record(run_id, payment_id, AuditAction.JOURNAL_ENTRY_POSTED,
                                 extra={"debit_minor": amount, "credit_minor": amount})
                except Exception as e:
                    print(f"Failed to post JE for {payment_id}: {e}")
                    
        _latest_ledger = ledger

        # ── 5. Settlement Reconciliation ──────────────────────────────────────
        # Group Razorpay payments by settlement ID
        rzp_records = sources_dict.get("razorpay", [])
        bank_credits = sources_dict.get("bank", [])
        
        settlements_map = {}
        for r in rzp_records:
            sid = r.get("settlement_id")
            if sid:
                if sid not in settlements_map:
                    settlements_map[sid] = []
                settlements_map[sid].append(r)
                
        recon_results = reconcile_all_settlements(
            payments_by_settlement=settlements_map,
            bank_credits=bank_credits
        )
        
        batches = [res.batch for res in recon_results]
        set_settlement_batches([b.to_breakdown() for b in batches])
        set_settlement_recon_results([res.to_dict() for res in recon_results])
        
        for res in recon_results:
            chain.record(
                run_id, res.batch.settlement_id, 
                AuditAction.SETTLEMENT_RECONCILED,
                decision=res.match_result.value,
                extra={"variance_minor": res.variance_minor}
            )

        # ── 6. Agent Architecture Pipeline ────────────────────────────────────
        # Prepare output dict for agent layer
        recon_output_dict = {
            "run_id": run_id,
            "matches": [m.__dict__ for m in output.matches],
            "manual_review": [m.__dict__ for m in output.manual_review],
            "unresolved_ids": output.unresolved_ids,
            "all_ids": output.all_ids,
            "processing_ms": output.processing_ms,
        }
        
        agent_results = run_agent_pipeline(
            recon_output_dict, 
            exceptions=exc_dicts,
            api_key=""
        )
        agent_summary = agent_results.get("report")
        if agent_summary and hasattr(agent_summary, "to_dict"):
            agent_summary = agent_summary.to_dict()
        elif agent_summary and hasattr(agent_summary, "data"):
            agent_summary = agent_summary.data
        else:
            agent_summary = {}

        # ── Metrics (if ground truth available) ──────────────────────────────
        try:
            gt = load_ground_truth()
            metrics = compute_metrics(output, gt, sources_dict)
        except Exception:
            metrics = {
                "match_rate": output.match_rate,
                "auto_matched": output.auto_matched,
                "manual_review": output.manual_review_count,
                "unresolved": output.unresolved_count,
            }

        # ── Build & Return Response ───────────────────────────────────────────
        reconciled_value = sum(
            sources_dict.get("ledger", [])[i].get("amount_minor", 0)
            for i in range(len(sources_dict.get("ledger", [])))
            if sources_dict.get("ledger", [])[i].get("canonical_id") in
               {m.left_id for m in output.matches}
        )

        from ingestion.loaders import get_payment_provider
        provider = get_payment_provider()

        is_valid, _ = chain.verify()

        result = {
            "run_id": run_id,
            "status": "COMPLETED",
            "started_at": output.started_at.isoformat(),
            "completed_at": output.completed_at.isoformat(),
            "processing_ms": output.processing_ms,
            "config": {
                "auto_match_threshold": req.auto_match_threshold,
                "review_threshold": req.review_threshold,
                "date_tolerance_days": req.date_tolerance_days,
            },
            "summary": {
                "records_processed": output.records_processed,
                "auto_matched": output.auto_matched,
                "manual_review": output.manual_review_count,
                "unresolved": output.unresolved_count,
                "exceptions": len(exceptions),
                "reconciled_value_minor": reconciled_value,
                "match_rate": output.match_rate,
            },
            "metrics": metrics,
            "data_quality_score": dq_report.overall_score,
            "agent_summary": agent_summary,
            "audit": {
                "event_count": chain.event_count(),
                "chain_verified": is_valid,
                "last_hash": chain.last_hash()[:16] + "..." if chain.last_hash() else "",
            },
            "data_source": provider.get_provider_name(),
        }

        chain.record(run_id, run_id, AuditAction.RECONCILIATION_COMPLETED,
                     extra={"match_rate": output.match_rate, "exceptions": len(exceptions)})

        db_run = ReconciliationRun(
            run_id=run_id,
            started_at=output.started_at,
            completed_at=output.completed_at,
            threshold=req.auto_match_threshold,
            records_processed=output.records_processed,
            auto_matched=output.auto_matched,
            manual_review=output.manual_review_count,
            unresolved=output.unresolved_count,
            match_rate=output.match_rate,
            reconciled_value_minor=reconciled_value,
            processing_ms=output.processing_ms,
            status="COMPLETED"
        )
        db.add(db_run)
        db.commit()  # Commit the run summary first!

        # Now try to insert the matches. If it fails due to FK/Unique, ignore.
        existing_matches = db.query(Match.left_transaction_id, Match.right_transaction_id).all()
        existing_set = set((m[0], m[1]) for m in existing_matches)

        for m in output.matches:
            if (m.left_id, m.right_id) in existing_set:
                continue
                
            db.add(
                Match(
                    run_id=run_id,
                    left_transaction_id=m.left_id,
                    right_transaction_id=m.right_id,
                    decision=m.decision,
                    probability=m.probability,
                    reason_code=m.reason_code,
                    evidence={"splink_score": m.probability}
                )
            )
            
        try:
            db.commit()
        except Exception as e:
            db.rollback()


        _runs[run_id] = result
        set_latest_report(result)
        db.close()
        return result

    except Exception as e:
        chain.record(run_id, run_id, "RECONCILIATION_FAILED", extra={"error": str(e)})
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.close()
        raise HTTPException(status_code=500, detail=f"Reconciliation failed: {str(e)}")


@router.get("/runs")
async def list_runs():
    db = SyncSessionLocal()
    runs = db.query(ReconciliationRun).order_by(ReconciliationRun.id.desc()).all()
    if not runs:
        db.close()
        return {"runs": list(_runs.values())}
    result = []
    for r in runs:
        result.append({
            "run_id": r.run_id,
            "status": r.status,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "match_rate": r.match_rate,
            "reconciled_value_minor": r.reconciled_value_minor
        })
    db.close()
    return {"runs": result}


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run
