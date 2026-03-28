import time
import requests
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000/events"

events = [
    {
        "site_id": "water_north",
        "site_name": "North Water Plant",
        "asset_id": "pump_07",
        "asset_type": "pump",
        "event_type": "pressure_alarm",
        "severity": "high",
        "message": "Pump discharge pressure above threshold",
    },
    {
        "site_id": "mine_west",
        "site_name": "West Mine Conveyor Hub",
        "asset_id": "conv_03",
        "asset_type": "conveyor",
        "event_type": "motor_fault",
        "severity": "critical",
        "message": "Conveyor motor overload detected",
    },
    {
        "site_id": "utility_east",
        "site_name": "East Utility Substation",
        "asset_id": "tr_ctrl_02",
        "asset_type": "transformer_controller",
        "event_type": "disconnect_alarm",
        "severity": "medium",
        "message": "Controller communication lost",
    },
]

i = 0
while True:
    event = events[i % len(events)].copy()
    event["topic"] = f"sites/{event['site_id']}/{event['asset_id']}/{event['event_type']}"
    event["timestamp"] = datetime.now(timezone.utc).isoformat()

    r = requests.post(BASE_URL, json=event, timeout=10)
    print(r.status_code, r.text)

    i += 1
    time.sleep(8)