"""Event ingestion service.

This service owns the flow from raw event input to created incident output.
"""

from sqlalchemy.orm import Session

from app.models import Event, Incident
from app.schemas import EventIn
from app.services.rules_engine import score_event
from app.services.rag_service import LocalRAGService


class IngestionService:
    """Handles operational event processing."""

    def __init__(self) -> None:
        # Create one local RAG helper for the service.
        self.rag = LocalRAGService()

    def ingest_event(self, db: Session, event_in: EventIn) -> Event:
        """Persist an event, score it, and possibly create an incident."""
        score = score_event(event_in)

        # Save the raw event first.
        event = Event(
            site_id=event_in.site_id,
            site_name=event_in.site_name,
            asset_id=event_in.asset_id,
            asset_type=event_in.asset_type,
            event_type=event_in.event_type,
            severity=event_in.severity,
            topic=event_in.topic,
            message=event_in.message,
            value=event_in.value,
            score=score,
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # In this starter project, any event with score >= 70 becomes an active incident.
        if score >= 70:
            actions, supporting_docs = self.rag.build_action_list(
                site_id=event_in.site_id,
                asset_type=event_in.asset_type,
                event_type=event_in.event_type,
            )

            incident = Incident(
                site_id=event_in.site_id,
                site_name=event_in.site_name,
                asset_id=event_in.asset_id,
                asset_type=event_in.asset_type,
                event_type=event_in.event_type,
                severity=event_in.severity,
                priority_score=score,
                recommended_actions=actions,
                supporting_docs=supporting_docs,
                is_active=True,
            )
            db.add(incident)
            db.commit()

        return event
