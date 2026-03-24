"""Simulation script.

This script sends sample industrial site events into the FastAPI API.
Run the API first, then run this file in another terminal.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import time

import httpx

BASE_URL = "http://127.0.0.1:8000"

SAMPLE_EVENTS = [
    {
        "site_id": "water_north",
        "site_name": "North Water Plant",
        "asset_id": "pump_07",
        "asset_type": "pump",
        "event_type": "pressure_alarm",
        "severity": "high",
        "topic": "water_north/pump_07/pressure_alarm",
        "message": "Pressure exceeded upper threshold for 2 minutes",
        "value": 142.8,
    },
    {
        "site_id": "mine_west",
        "site_name": "West Mine Conveyor Hub",
        "asset_id": "conv_02",
        "asset_type": "conveyor",
        "event_type": "motor_fault",
        "severity": "critical",
        "topic": "mine_west/conv_02/motor_fault",
        "message": "Motor trip repeated during loaded startup",
        "value": 1.0,
    },
    {
        "site_id": "utility_east",
        "site_name": "East Utility Substation",
        "asset_id": "tr_ctrl_01",
        "asset_type": "transformer_controller",
        "event_type": "login_failure_burst",
        "severity": "high",
        "topic": "utility_east/tr_ctrl_01/login_failure_burst",
        "message": "Repeated failed login burst from remote engineering path",
        "value": 9.0,
    },
    {
        "site_id": "water_north",
        "site_name": "North Water Plant",
        "asset_id": "plc_01",
        "asset_type": "plc",
        "event_type": "device_disconnect",
        "severity": "high",
        "topic": "water_north/plc_01/device_disconnect",
        "message": "PLC disconnect detected from SCADA and edge gateway",
        "value": None,
    },
]


def main() -> None:
    """Post sample events to the running API."""
    with httpx.Client(timeout=10.0) as client:
        for event in SAMPLE_EVENTS:
            response = client.post(f"{BASE_URL}/events", json=event)
            response.raise_for_status()
            print("Sent event:")
            print(json.dumps(response.json(), indent=2))
            print("-" * 80)
            time.sleep(0.4)

    print("Simulation complete. Now open /ops/ranked-actions in the browser.")


if __name__ == "__main__":
    main()
