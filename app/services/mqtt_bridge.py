"""Optional MQTT bridge skeleton.

This file shows where MQTT would fit in a more realistic deployment.
It is not required for the smoke test and is not started automatically.

Why keep it optional?
- Many student environments do not have a broker running.
- The REST path is easier to test locally.
- The architecture still stays realistic because MQTT can be plugged in later.

To use this in the future:
1. Install paho-mqtt.
2. Point it to a broker.
3. Forward received MQTT payloads into the same ingestion service.
"""

# NOTE:
# The import is intentionally commented out so the base project does not require paho-mqtt.
# import paho.mqtt.client as mqtt

from typing import Any


class MQTTBridge:
    """Placeholder MQTT bridge.

    A future version would subscribe to remote site topics such as:
    - water_north/+/+
    - mine_west/+/+
    - utility_east/+/+
    """

    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883) -> None:
        self.broker_host = broker_host
        self.broker_port = broker_port

    def start(self) -> None:
        """Start the MQTT subscriber loop.

        In a real version, this method would:
        - connect to the broker
        - subscribe to site topics
        - parse MQTT messages
        - transform them into EventIn payloads
        - forward them into the ingestion flow
        """
        print(
            "MQTTBridge is a starter placeholder. "
            "Use the REST API path now, or extend this file for a real broker."
        )

    def on_message(self, payload: dict[str, Any]) -> None:
        """Example handler signature for future incoming MQTT payloads."""
        print("Received MQTT payload:", payload)
