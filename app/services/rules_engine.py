"""Rules engine for event scoring.

This starter engine uses a few explainable rules instead of a black-box model.
That makes it easier to demo, test, and explain.
"""

SEVERITY_BASE_SCORE = {
    "low": 20.0,
    "medium": 45.0,
    "high": 70.0,
    "critical": 90.0,
}

EVENT_BONUS = {
    "pressure_alarm": 12.0,
    "device_disconnect": 18.0,
    "motor_fault": 20.0,
    "login_failure_burst": 16.0,
    "config_change": 10.0,
}


def score_event(event_in) -> float:
    """Calculate an urgency score for the event.

    The score is deliberately simple:
    - severity contributes the largest part
    - event type adds domain-specific weight
    - message keywords can further increase urgency
    """
    base = SEVERITY_BASE_SCORE.get(event_in.severity.lower(), 10.0)
    bonus = EVENT_BONUS.get(event_in.event_type, 5.0)

    # Keyword-based urgency boost.
    message = event_in.message.lower()
    keyword_bonus = 0.0
    for word in ["repeated", "failed", "disconnect", "trip", "blocked", "critical", "burst"]:
        if word in message:
            keyword_bonus += 3.0

    # Numeric values can be used later for richer scoring.
    return round(base + bonus + keyword_bonus, 2)
