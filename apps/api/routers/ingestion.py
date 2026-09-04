from fastapi import APIRouter
from ingestion.loaders import load_all_sources
from database.session import SyncSessionLocal
from database.models import WebhookEvent

router = APIRouter()

@router.post("/sync")
def trigger_data_sync():
    """Manually trigger the data ingestion pipeline across all configured sources."""
    sources = load_all_sources()
    counts = {k: len(v) for k, v in sources.items()}
    return {"status": "success", "records_ingested": counts}

@router.get("/webhooks")
def list_webhooks():
    """List recent webhook events."""
    db = SyncSessionLocal()
    events = db.query(WebhookEvent).order_by(WebhookEvent.id.desc()).limit(20).all()
    res = [{"event_id": e.event_id, "type": e.event_type, "status": e.processing_status} for e in events]
    db.close()
    return {"events": res}
