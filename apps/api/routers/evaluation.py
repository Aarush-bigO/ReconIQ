"""Evaluation Lab router — threshold sweep with real precision/recall."""
import time
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
_benchmark_results: list[dict] = []


@router.get("/results")
async def get_benchmark_results():
    return {"results": _benchmark_results}


@router.post("/run")
def run_evaluation():
    """Run threshold sweep benchmark and return real metrics."""
    from ingestion.loaders import load_all_sources, records_to_dict_list
    from matching.run_splink import run_multi_source_linkage
    from matching.reconcile import reconcile, ReconciliationRunConfig
    from matching.metrics import load_ground_truth, compute_metrics
    import sys, splink

    thresholds = [0.80, 0.85, 0.90, 0.95, 0.97, 0.99]
    results = []

    sources_canonical = load_all_sources()
    sources_dict = {k: records_to_dict_list(v) for k, v in sources_canonical.items()}
    gt = load_ground_truth()
    predictions = run_multi_source_linkage(sources_dict)

    for threshold in thresholds:
        start = time.time()
        config = ReconciliationRunConfig(auto_match_threshold=threshold, review_threshold=0.70)
        output = reconcile(sources_dict, predictions, config)
        metrics = compute_metrics(output, gt, sources_dict)
        elapsed = time.time() - start

        results.append({
            "threshold": threshold,
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "match_rate": metrics["match_rate"],
            "manual_review_rate": metrics["manual_review_rate"],
            "auto_matched": output.auto_matched,
            "manual_review": output.manual_review_count,
            "unresolved": output.unresolved_count,
            "processing_seconds": round(elapsed, 3),
            "dataset_size": output.records_processed,
            "splink_version": splink.__version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        })

    global _benchmark_results
    _benchmark_results = results
    return {"results": results, "recommended_threshold": 0.95,
            "recommendation_reason": "High precision with manageable manual-review volume."}
