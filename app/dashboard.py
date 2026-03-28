import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh


BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Remote Operations Assistant", layout="wide")
st.title("Remote Operations Assistant Dashboard")
st.markdown("This dashboard reads data from the FastAPI backend.")
st.caption(f"Last refreshed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

refresh_seconds = st.sidebar.slider("Auto-refresh (seconds)", 0, 30, 5)
if refresh_seconds > 0:
    st_autorefresh(interval=refresh_seconds * 1000, key="dashboard_autorefresh")


def get_json(endpoint: str):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch {endpoint}: {e}")
        return None

st.sidebar.header("Controls")
if st.sidebar.button("Refresh Data"):
    st.rerun()

st.subheader("Backend Status")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    response.raise_for_status()
    health = response.json()
    st.success(f"Backend is running: {health}")
except Exception as e:
    st.error(f"Backend not reachable: {e}")
    st.stop()

st.subheader("Incidents")
incidents = get_json("/ops/incidents")
if incidents:
    if isinstance(incidents, list) and len(incidents) > 0:
        df_incidents = pd.DataFrame(incidents)
        st.dataframe(df_incidents, width="stretch")
    else:
        st.info("No incidents found.")
else:
    st.info("No incident data returned.")

st.subheader("Ranked Actions")
ranked_actions = get_json("/ops/ranked-actions")
if ranked_actions:
    if isinstance(ranked_actions, list) and len(ranked_actions) > 0:
        df_actions = pd.DataFrame(ranked_actions)
        st.dataframe(df_actions, width="stretch")
    else:
        st.info("No ranked actions found.")
else:
    st.info("No ranked action data returned.")

st.subheader("Shift Summary")
shift_summary = get_json("/ops/shift-summary")
if shift_summary:
    st.json(shift_summary)
else:
    st.info("No shift summary returned.")

st.subheader("Send Test Event")

with st.form("event_form"):
    site_id = st.text_input("Site ID", value="water_north")
    asset_id = st.text_input("Asset ID", value="pump_07")
    event_type = st.text_input("Event Type", value="pressure_alarm")
    severity = st.selectbox("Severity", ["low", "medium", "high", "critical"], index=2)
    message = st.text_input("Message", value="Pump discharge pressure above threshold")
    submitted = st.form_submit_button("Submit Event")

    if submitted:
        payload = {
            "site_id": site_id,
            "site_name": "North Water Plant",
            "asset_id": asset_id,
            "asset_type": "pump",
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "topic": f"sites/{site_id}/{asset_id}/{event_type}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            response = requests.post(f"{BASE_URL}/events", json=payload, timeout=10)
            response.raise_for_status()
            st.success("Event submitted successfully.")
            st.json(response.json())
        except requests.HTTPError as e:
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            st.error(f"Failed to submit event: {error_detail}")
        except Exception as e:
            st.error(f"Failed to submit event: {e}")