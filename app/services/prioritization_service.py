"""Prioritization logic for ranking incidents across sites."""

from typing import List

from app.models import Incident
from app.schemas import RankedActionOut


def build_ranked_actions(incidents: List[Incident]) -> List[RankedActionOut]:
    """Convert incidents into a sorted ranked action list."""
    ranked = sorted(incidents, key=lambda item: item.priority_score, reverse=True)

    output = []
    for incident in ranked:
        headline = (
            f"{incident.site_name} | {incident.asset_type} {incident.asset_id} | "
            f"{incident.event_type} | {incident.severity.upper()}"
        )
        output.append(
            RankedActionOut(
                incident_id=incident.id,
                site_id=incident.site_id,
                site_name=incident.site_name,
                asset_id=incident.asset_id,
                event_type=incident.event_type,
                priority_score=incident.priority_score,
                headline=headline,
                recommended_actions=incident.recommended_actions,
            )
        )
    return output
