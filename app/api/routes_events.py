"""Event-related API routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import EventIn, EventOut
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/events", tags=["events"])

# Create one service instance that can be reused by the routes.
ingestion_service = IngestionService()


@router.post("", response_model=EventOut)
def create_event(event_in: EventIn, db: Session = Depends(get_db)):
    """Accept an operational event and process it."""
    return ingestion_service.ingest_event(db, event_in)


@router.get("", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db)):
    """Return all stored events ordered by newest first."""
    return db.query(Event).order_by(Event.created_at.desc()).all()
