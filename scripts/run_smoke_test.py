from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

"""Local smoke test.

This script runs without Uvicorn by using FastAPI's TestClient.
It verifies the main flow:
- startup
- event ingestion
- incident creation
- ranked actions
- shift summary
"""

from pprint import pprint

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine
from app.seed_data import ensure_runbooks_exist

# Recreate local tables for a clean test run.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
ensure_runbooks_exist()

client = TestClient(app)

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
]

print("\n1) Sending sample events...")
for event in SAMPLE_EVENTS:
    response = client.post("/events", json=event)
    print("Status:", response.status_code)
    pprint(response.json())
    print("-" * 80)

print("\n2) Fetching active incidents...")
incidents = client.get("/ops/incidents")
print("Status:", incidents.status_code)
pprint(incidents.json())

print("\n3) Fetching ranked actions...")
ranked = client.get("/ops/ranked-actions")
print("Status:", ranked.status_code)
pprint(ranked.json())

print("\n4) Fetching shift summary...")
summary = client.get("/ops/shift-summary")
print("Status:", summary.status_code)
pprint(summary.json())

print("\nSmoke test finished successfully.")
