"""Pydantic request and response schemas.

These schemas validate API inputs and shape API outputs.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    """Incoming event payload used by clients and simulators."""
    timestamp: Optional[datetime] = Field(default=None, examples=["2026-03-31T12:00:00Z"])
    site_id: str = Field(..., examples=["water_north"])
    site_name: str = Field(..., examples=["North Water Plant"])
    asset_id: str = Field(..., examples=["pump_07"])
    asset_type: str = Field(..., examples=["pump"])
    event_type: str = Field(..., examples=["pressure_alarm"])
    severity: str = Field(..., examples=["high"])
    topic: str = Field(..., examples=["water_north/pump_07/pressure_alarm"])
    message: str = Field(..., examples=["Pressure exceeded upper threshold"])
    value: Optional[float] = Field(default=None, examples=[142.8])


class EventOut(EventIn):
    """Event payload returned from the API after persistence."""

    id: int
    score: float
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentOut(BaseModel):
    """Incident payload shown to remote operators."""

    id: int
    site_id: str
    site_name: str
    asset_id: str
    asset_type: str
    event_type: str
    severity: str
    priority_score: float
    recommended_actions: str
    supporting_docs: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RankedActionOut(BaseModel):
    """Simplified ranked action row for dashboard-like display."""

    incident_id: int
    site_id: str
    site_name: str
    asset_id: str
    event_type: str
    priority_score: float
    headline: str
    recommended_actions: str


class ShiftSummaryOut(BaseModel):
    """Summary payload representing a remote operator shift handoff."""

    total_active_incidents: int
    top_site: Optional[str]
    top_issue: Optional[str]
    site_breakdown: List[str]
    summary_text: str
