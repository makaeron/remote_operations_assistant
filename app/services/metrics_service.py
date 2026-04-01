from datetime import datetime, timezone


class MetricsStore:
    def __init__(self):
        self.total_events = 0
        self.accepted_events = 0
        self.validation_rejected_events = 0
        self.duplicate_events = 0
        self.service_rejected_events = 0
        self.total_freshness_delay_ms = 0.0
        self.freshness_samples = 0

    def record_total(self):
        self.total_events += 1

    def record_accepted(self):
        self.accepted_events += 1

    def record_validation_rejected(self):
        self.validation_rejected_events += 1

    def record_duplicate(self):
        self.duplicate_events += 1

    def record_service_rejected(self):
        self.service_rejected_events += 1

    def record_freshness(self, event_timestamp):
        now = datetime.now(timezone.utc)
        delay_ms = (now - event_timestamp).total_seconds() * 1000
        if delay_ms >= 0:
            self.total_freshness_delay_ms += delay_ms
            self.freshness_samples += 1

    def snapshot(self):
        ingestion_success_rate = (
            self.accepted_events / self.total_events if self.total_events else 0
        )
        duplicate_rate = (
            self.duplicate_events / self.total_events if self.total_events else 0
        )
        validation_rejection_rate = (
            self.validation_rejected_events / self.total_events if self.total_events else 0
        )
        avg_freshness_delay_ms = (
            self.total_freshness_delay_ms / self.freshness_samples
            if self.freshness_samples else 0
        )

        return {
            "total_events": self.total_events,
            "accepted_events": self.accepted_events,
            "validation_rejected_events": self.validation_rejected_events,
            "duplicate_events": self.duplicate_events,
            "service_rejected_events": self.service_rejected_events,
            "ingestion_success_rate": round(ingestion_success_rate, 4),
            "duplicate_rate": round(duplicate_rate, 4),
            "validation_rejection_rate": round(validation_rejection_rate, 4),
            "avg_freshness_delay_ms": round(avg_freshness_delay_ms, 2),
        }


metrics_store = MetricsStore()