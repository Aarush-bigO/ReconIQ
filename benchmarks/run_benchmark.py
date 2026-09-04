"""
ReconIQ Enterprise — Benchmark Runner
======================================
Runs the full reconciliation pipeline across multiple thresholds
and records reproducible results.

Usage:
  python -m benchmarks.run_benchmark

Every benchmark result records:
  dataset_size, seed, threshold, splink_version, python_version,
  git_commit_sha, timestamp, precision, recall, match_rate,
  processing_seconds, reconciled_value_minor, exception_count
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import splink

# ── Setup path ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from ingestion.loaders import load_all_sources, records_to_dict_list
from matching.run_splink import run_multi_source_linkage
from matching.reconcile import reconcile, ReconciliationRunConfig
from matching.metrics import load_ground_truth, compute_metrics

RESULTS_DIR = ROOT / "benchmarks" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLDS = [0.80, 0.85, 0.90, 0.95, 0.97, 0.99]
SEED = 42


def get_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=ROOT
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def run_benchmark():
    print("=" * 60)
    print("ReconIQ Enterprise — Benchmark Run")
    print(f"Splink version: {splink.__version__}")
    print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Git SHA: {get_git_sha()}")
    print("=" * 60)

    # ── Load data ─────────────────────────────────────────────────────────
    print("\nLoading synthetic data (seed=42)...")
    sources_canonical = load_all_sources()
    sources_dict = {k: records_to_dict_list(v) for k, v in sources_canonical.items()}

    total_records = sum(len(v) for v in sources_dict.values())
    ledger_records = len(sources_dict.get("ledger", []))
    print(f"  Total records: {total_records}")
    print(f"  Sources: {list(sources_dict.keys())}")

    # ── Load ground truth ─────────────────────────────────────────────────
    print("\nLoading ground truth...")
    gt = load_ground_truth()
    print(f"  Ground truth entries: {len(gt)}")

    # ── Run Splink linkage ONCE (shared across thresholds) ─────────────────
    print("\nRunning Splink probabilistic linkage...")
    link_start = time.time()
    predictions = run_multi_source_linkage(sources_dict)
    link_elapsed = time.time() - link_start
    print(f"  Linkage complete in {link_elapsed:.2f}s")
    print(f"  Candidate pairs: {len(predictions)}")

    # ── Sweep thresholds ──────────────────────────────────────────────────
    print("\nThreshold sweep:")
    print(f"{'Threshold':>10} {'Precision':>10} {'Recall':>10} {'Match Rate':>12} {'F1':>8} {'Time(s)':>8}")
    print("-" * 62)

    results = []
    for threshold in THRESHOLDS:
        t_start = time.time()
        config = ReconciliationRunConfig(
            auto_match_threshold=threshold,
            review_threshold=0.70,
        )
        output = reconcile(sources_dict, predictions, config)
        metrics = compute_metrics(output, gt, sources_dict)
        elapsed = time.time() - t_start

        # Compute reconciled value
        ledger_recs = sources_dict.get("ledger", [])
        ledger_map = {r["canonical_id"]: r for r in ledger_recs}
        matched_ids = {m.left_id for m in output.matches}
        reconciled_value = sum(
            ledger_map[cid]["amount_minor"]
            for cid in matched_ids
            if cid in ledger_map
        )

        result = {
            "dataset_size": ledger_records,
            "total_records": total_records,
            "seed": SEED,
            "threshold": threshold,
            "splink_version": splink.__version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "git_commit_sha": get_git_sha(),
            "timestamp": datetime.utcnow().isoformat(),
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "match_rate": metrics["match_rate"],
            "manual_review_rate": metrics["manual_review_rate"],
            "auto_matched": output.auto_matched,
            "manual_review": output.manual_review_count,
            "unresolved": output.unresolved_count,
            "true_positives": metrics["true_positives"],
            "false_positives": metrics["false_positives"],
            "false_negatives": metrics["false_negatives"],
            "exception_count": output.unresolved_count,
            "reconciled_value_minor": reconciled_value,
            "processing_seconds": round(elapsed, 3),
        }
        results.append(result)

        print(
            f"{threshold:>10.2f} "
            f"{metrics['precision']:>10.4f} "
            f"{metrics['recall']:>10.4f} "
            f"{metrics['match_rate']:>12.4f} "
            f"{metrics['f1']:>8.4f} "
            f"{elapsed:>8.3f}"
        )

    # ── Save results ──────────────────────────────────────────────────────
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"benchmark_{timestamp}.json"
    with open(result_file, "w") as f:
        json.dump({
            "run_metadata": {
                "timestamp": timestamp,
                "git_sha": get_git_sha(),
                "splink_version": splink.__version__,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "total_records": total_records,
                "seed": SEED,
            },
            "results": results,
            "recommended_threshold": {
                "value": 0.95,
                "reason": "High precision with manageable manual-review volume.",
            },
        }, f, indent=2)
    print(f"\n✓ Results saved to: {result_file}")

    # ── Summary ───────────────────────────────────────────────────────────
    rec_95 = next((r for r in results if r["threshold"] == 0.95), None)
    if rec_95:
        print(f"\nOperating point (threshold=0.95):")
        print(f"  Precision:    {rec_95['precision']:.4f}")
        print(f"  Recall:       {rec_95['recall']:.4f}")
        print(f"  Match rate:   {rec_95['match_rate']:.4f}")
        print(f"  F1:           {rec_95['f1']:.4f}")

    print("\n✓ Benchmark complete.")
    return results


if __name__ == "__main__":
    run_benchmark()
