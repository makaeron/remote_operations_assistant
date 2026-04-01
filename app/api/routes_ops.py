"""Operator-facing operations routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident
from app.schemas import IncidentOut, RankedActionOut, ShiftSummaryOut
from app.services.metrics_service import metrics_store
from app.services.prioritization_service import build_ranked_actions
from app.services.summary_service import build_shift_summary

router = APIRouter(prefix="/ops", tags=["operations"])


@router.get("/incidents", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return (
        db.query(Incident)
        .filter(Incident.is_active.is_(True))
        .order_by(Incident.priority_score.desc())
        .all()
    )


@router.get("/ranked-actions", response_model=List[RankedActionOut])
def ranked_actions(db: Session = Depends(get_db)):
    incidents = (
        db.query(Incident)
        .filter(Incident.is_active.is_(True))
        .order_by(Incident.priority_score.desc())
        .all()
    )
    return build_ranked_actions(incidents)


@router.get("/shift-summary", response_model=ShiftSummaryOut)
def shift_summary(db: Session = Depends(get_db)):
    incidents = db.query(Incident).filter(Incident.is_active.is_(True)).all()
    return build_shift_summary(incidents)


@router.get("/metrics")
def get_metrics():
    return metrics_store.snapshot()