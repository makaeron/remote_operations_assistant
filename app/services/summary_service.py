"""Shift summary builder.

This gives remote operators a compact handoff view.
"""

from collections import Counter
from typing import List

from app.models import Incident
from app.schemas import ShiftSummaryOut


def build_shift_summary(incidents: List[Incident]) -> ShiftSummaryOut:
    """Summarize active incidents for the current shift."""
    if not incidents:
        return ShiftSummaryOut(
            total_active_incidents=0,
            top_site=None,
            top_issue=None,
            site_breakdown=[],
            summary_text="No active incidents. All monitored sites are currently stable.",
        )

    # Highest score incident becomes the top issue.
    top_incident = sorted(incidents, key=lambda item: item.priority_score, reverse=True)[0]

    site_counter = Counter(incident.site_name for incident in incidents)
    site_breakdown = [f"{site}: {count} active incident(s)" for site, count in site_counter.items()]

    summary_text = (
        f"There are {len(incidents)} active incidents. "
        f"The top site needing attention is {top_incident.site_name} due to "
        f"{top_incident.event_type} on asset {top_incident.asset_id}. "
        f"Remote operators should start with the highest ranked issue and then review repeated patterns across sites."
    )

    return ShiftSummaryOut(
        total_active_incidents=len(incidents),
        top_site=top_incident.site_name,
        top_issue=f"{top_incident.event_type} on {top_incident.asset_id}",
        site_breakdown=site_breakdown,
        summary_text=summary_text,
    )
