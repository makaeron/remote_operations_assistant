"""Seed helper for local runbook documents.

The project uses local text files as a simple knowledge base.
"""

from pathlib import Path

from app.config import RUNBOOKS_DIR


RUNBOOK_CONTENT = {
    "water_north_pump_pressure_alarm.txt": """
Site: water_north
AssetType: pump
EventType: pressure_alarm

Title: Pump high pressure response

1. Confirm that the pressure reading is not stale by checking the last telemetry timestamp.
2. Compare the current pressure with the last 15-minute trend.
3. Verify whether the discharge valve position changed recently.
4. Check for downstream blockage or misconfigured control logic.
5. If pressure stays above threshold for more than 2 minutes, reduce pump load and notify maintenance.
6. Escalate immediately if pump temperature and vibration alarms are also present.
""",
    "water_north_plc_disconnect.txt": """
Site: water_north
AssetType: plc
EventType: device_disconnect

Title: PLC communication loss

1. Confirm whether the device is unreachable from SCADA and from the edge gateway.
2. Check switch port link status and recent network changes.
3. Verify if there was a maintenance window or power event.
4. Review whether neighboring assets on the same panel also lost communication.
5. Escalate to field technician if communication is not restored within 5 minutes.
""",
    "mine_west_conveyor_fault.txt": """
Site: mine_west
AssetType: conveyor
EventType: motor_fault

Title: Conveyor motor fault response

1. Confirm if the motor tripped under load or during startup.
2. Check overload relay state and upstream breaker status.
3. Review temperature, current draw, and bearing vibration from the last hour.
4. Inspect whether the conveyor is jammed or overloaded.
5. Coordinate with site operations before restart.
""",
    "utility_east_transformer_login_failures.txt": """
Site: utility_east
AssetType: transformer_controller
EventType: login_failure_burst

Title: Repeated controller login failures

1. Confirm whether the failures are from a known engineering workstation.
2. Compare source IP or host identity with the approved maintenance list.
3. Check if login failures happened during a planned remote session.
4. Lock remote access route if failures continue and no valid maintenance ticket exists.
5. Notify cyber operations and site supervisor for investigation.
""",
    "generic_shift_handoff.txt": """
Site: generic
AssetType: any
EventType: any

Title: Shift handoff guidance

1. Review all unresolved high-priority incidents.
2. Confirm which sites still require local technician dispatch.
3. Note repeated alarms that may indicate chronic equipment or network issues.
4. Highlight the site with the highest current workload.
5. Record what action was taken and what is still pending.
""",
}


def ensure_runbooks_exist() -> None:
    """Create seed runbook files if they are missing."""
    RUNBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in RUNBOOK_CONTENT.items():
        file_path = RUNBOOKS_DIR / filename
        if not file_path.exists():
            file_path.write_text(content.strip() + "\n", encoding="utf-8")
