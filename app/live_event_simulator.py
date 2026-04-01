import time
import random
import requests
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000/events"

EVENT_TEMPLATES = [
    {
        "site_id": "water_north",
        "site_name": "North Water Plant",
        "asset_id": "pump_07",
        "asset_type": "pump",
        "event_type": "pressure_alarm",
        "severity_choices": ["medium", "high", "critical"],
        "message_choices": [
            "Pump discharge pressure above threshold",
            "Pump pressure rising beyond operating range",
            "High discharge pressure detected on pump"
        ],
        "value_range": (120.0, 170.0)
    },
    {
        "site_id": "water_north",
        "site_name": "North Water Plant",
        "asset_id": "plc_04",
        "asset_type": "plc",
        "event_type": "device_disconnect",
        "severity_choices": ["medium", "high"],
        "message_choices": [
            "PLC communication lost from SCADA",
            "PLC not reachable from edge gateway",
            "Device disconnect detected on PLC"
        ],
        "value_range": None
    },
    {
        "site_id": "mine_west",
        "site_name": "West Mine Conveyor Hub",
        "asset_id": "conv_02",
        "asset_type": "conveyor",
        "event_type": "motor_fault",
        "severity_choices": ["high", "critical"],
        "message_choices": [
            "Motor fault detected on conveyor 02",
            "Conveyor motor tripped under load",
            "Conveyor motor overload condition detected"
        ],
        "value_range": (1.0, 5.0)
    },
    {
        "site_id": "utility_east",
        "site_name": "East Utility Substation",
        "asset_id": "tr_ctrl_01",
        "asset_type": "transformer_controller",
        "event_type": "login_failure_burst",
        "severity_choices": ["medium", "high", "critical"],
        "message_choices": [
            "Repeated failed login burst from remote engineering path",
            "Unexpected login failures detected on controller",
            "Multiple authentication failures on transformer controller"
        ],
        "value_range": (3.0, 15.0)
    },
    {
        "site_id": "water_north",
        "site_name": "North Water Plant",
        "asset_id": "pump_03",
        "asset_type": "pump",
        "event_type": "temperature_alarm",
        "severity_choices": ["medium", "high"],
        "message_choices": [
            "Pump temperature above threshold",
            "Motor casing temperature rising",
            "Pump thermal alarm detected"
        ],
        "value_range": (70.0, 105.0)
    }
]


def build_payload():
    template = random.choice(EVENT_TEMPLATES)

    severity = random.choice(template["severity_choices"])
    message = random.choice(template["message_choices"])

    payload = {
        "site_id": template["site_id"],
        "site_name": template["site_name"],
        "asset_id": template["asset_id"],
        "asset_type": template["asset_type"],
        "event_type": template["event_type"],
        "severity": severity,
        "message": message,
        "topic": f"sites/{template['site_id']}/{template['asset_id']}/{template['event_type']}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if template["value_range"] is not None:
        low, high = template["value_range"]
        payload["value"] = round(random.uniform(low, high), 2)

    return payload


def send_event():
    payload = build_payload()
    response = requests.post(BASE_URL, json=payload, timeout=10)
    response.raise_for_status()
    return payload, response.json()


def main():
    print("Live event simulator started.")
    print("Sending events to:", BASE_URL)
    print("Press Ctrl + C to stop.\n")

    while True:
        try:
            payload, result = send_event()
            print("=" * 80)
            print("Sent at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print("Event Type:", payload["event_type"])
            print("Site:", payload["site_name"])
            print("Asset:", payload["asset_id"])
            print("Severity:", payload["severity"])
            print("Value:", payload.get("value", "None"))
            print("Message:", payload["message"])
            print("Backend Response:", result)

            sleep_seconds = random.randint(3, 8)
            time.sleep(sleep_seconds)

        except KeyboardInterrupt:
            print("\nSimulator stopped by user.")
            break
        except Exception as e:
            print("Failed to send event:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()