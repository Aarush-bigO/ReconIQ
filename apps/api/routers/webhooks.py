"""Webhooks router — Razorpay webhook ingestion with signature verification."""
import hashlib
import hmac
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from apps.api.config import get_settings
from ingestion.razorpay_adapter import verify_razorpay_webhook, parse_webhook_event

from database.session import SyncSessionLocal
from database.models import WebhookEvent
from apps.api.services.ledger import process_financial_event_sync

router = APIRouter()
settings = get_settings()

@router.post("/razorpay")
async def receive_razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
):
    payload_bytes = await request.body()

    # Signature verification
    if settings.razorpay_webhook_secret and x_razorpay_signature:
        is_valid = verify_razorpay_webhook(
            payload_bytes, x_razorpay_signature, settings.razorpay_webhook_secret
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Webhook signature verification failed.")
    elif settings.razorpay_webhook_secret and not x_razorpay_signature:
        raise HTTPException(status_code=401, detail="Missing X-Razorpay-Signature header.")

    try:
        import json
        payload = json.loads(payload_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    event_data = parse_webhook_event(payload)

    db = SyncSessionLocal()
    # Idempotency check
    event_id = event_data["event_id"]
    existing = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
    if existing:
        db.close()
        return {"status": "already_processed", "event_id": event_id}

    db_event = WebhookEvent(
        event_id=event_id,
        event_type=event_data["event_type"],
        provider=event_data["provider"],
        processing_status=event_data["processing_status"],
        payload=event_data["raw_payload"]
    )
    db.add(db_event)
    
    # Process financial event (for demo, parsing from payload if valid financial event)
    # E.g. order.paid, payment.captured, settlement.processed
    if "payment" in event_data["event_type"].lower():
        process_financial_event_sync(
            db=db,
            event_type="PAYMENT",
            direction="CREDIT",
            amount_minor=payload.get("payload", {}).get("payment", {}).get("entity", {}).get("amount", 0),
            reference=event_id,
            description=f"Webhook Event {event_id}"
        )
    elif "settlement" in event_data["event_type"].lower():
        process_financial_event_sync(
            db=db,
            event_type="SETTLEMENT",
            direction="CREDIT",
            amount_minor=payload.get("payload", {}).get("settlement", {}).get("entity", {}).get("amount", 0),
            reference=event_id,
            description=f"Webhook Event {event_id}"
        )
    
    db.commit()
    db.close()

    return {"status": "received", "event_id": event_id, "event_type": event_data["event_type"]}


@router.get("/razorpay/events")
async def list_webhook_events():
    db = SyncSessionLocal()
    events = db.query(WebhookEvent).order_by(WebhookEvent.id.desc()).limit(50).all()
    res = []
    for e in events:
        res.append({
            "event_id": e.event_id,
            "event_type": e.event_type,
            "provider": e.provider,
            "received_at": e.received_at.isoformat() if e.received_at else None,
            "processing_status": e.processing_status,
            "payload": e.payload
        })
    db.close()
    return {"total": len(res), "events": res}
