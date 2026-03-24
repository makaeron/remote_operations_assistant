"""SQLAlchemy ORM models.

These tables store operational events and generated incidents.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean

from app.database import Base


class Event(Base):
    """Raw incoming operational event from a site."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String, index=True, nullable=False)
    site_name = Column(String, nullable=False)
    asset_id = Column(String, index=True, nullable=False)
    asset_type = Column(String, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    severity = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    value = Column(Float, nullable=True)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Incident(Base):
    """A derived operator-facing incident created from one or more events."""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String, index=True, nullable=False)
    site_name = Column(String, nullable=False)
    asset_id = Column(String, index=True, nullable=False)
    asset_type = Column(String, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    severity = Column(String, nullable=False)
    priority_score = Column(Float, default=0.0)
    recommended_actions = Column(Text, nullable=False)
    supporting_docs = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
