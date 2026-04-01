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

st.sidebar.header("Controls")
refresh_seconds = st.sidebar.slider("Auto-refresh (seconds)", 0, 30, 5)
if refresh_seconds > 0:
    st_autorefresh(interval=refresh_seconds * 1000, key="dashboard_autorefresh")

if st.sidebar.button("Refresh Data"):
    st.rerun()


def get_json(endpoint: str, timeout: int = 10):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch {endpoint}: {e}")
        return None


def post_json(endpoint: str, payload: dict, timeout: int = 10):
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.HTTPError as e:
        try:
            return None, e.response.json()
        except Exception:
            return None, e.response.text
    except Exception as e:
        return None, str(e)


st.subheader("Backend Status")
health = get_json("/")
if not health:
    st.error("Backend not reachable. Start FastAPI first with: uvicorn app.main:app --reload")
    st.stop()

st.success("Backend is running.")


st.subheader("Pipeline Metrics")
metrics = get_json("/ops/metrics")
if not metrics:
    metrics = {
        "total_events": 0,
        "accepted_events": 0,
        "ingestion_success_rate": 0,
        "duplicate_rate": 0,
        "validation_rejection_rate": 0,
        "avg_freshness_delay_ms": 0,
    }

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Total Events", metrics.get("total_events", 0))
m2.metric("Accepted Events", metrics.get("accepted_events", 0))
m3.metric("Ingestion Success Rate", f"{metrics.get('ingestion_success_rate', 0) * 100:.2f}%")
m4.metric("Duplicate Rate", f"{metrics.get('duplicate_rate', 0) * 100:.2f}%")
m5.metric("Validation Rejection Rate", f"{metrics.get('validation_rejection_rate', 0) * 100:.2f}%")
m6.metric("Avg Freshness Delay", f"{metrics.get('avg_freshness_delay_ms', 0):.2f} ms")


st.subheader("Incidents")
incidents = get_json("/ops/incidents")

if incidents and isinstance(incidents, list) and len(incidents) > 0:
    df_incidents = pd.DataFrame(incidents)

    defaults = {
        "severity": "unknown",
        "site_name": "Unknown Site",
        "event_type": "unknown_event",
        "asset_id": "unknown_asset",
        "message": "",
        "priority_score": 0,
    }
    for column, default_value in defaults.items():
        if column not in df_incidents.columns:
            df_incidents[column] = default_value

    severity_series = df_incidents["severity"].astype(str).str.lower()

    total_incidents = len(df_incidents)
    critical_count = int((severity_series == "critical").sum())
    high_count = int((severity_series == "high").sum())
    medium_count = int((severity_series == "medium").sum())
    low_count = int((severity_series == "low").sum())

    st.subheader("Incident Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Incidents", total_incidents)
    c2.metric("Critical", critical_count)
    c3.metric("High", high_count)
    c4.metric("Medium", medium_count)
    c5.metric("Low", low_count)

    st.subheader("Critical Incident Section")
    df_critical = df_incidents[severity_series == "critical"].copy()

    if not df_critical.empty:
        st.warning(f"There are {len(df_critical)} critical incident(s) requiring immediate attention.")
        critical_display_cols = [
            col for col in [
                "id",
                "site_name",
                "asset_id",
                "event_type",
                "severity",
                "message",
                "priority_score",
                "created_at",
            ] if col in df_critical.columns
        ]
        st.dataframe(df_critical[critical_display_cols].reset_index(drop=True), width="stretch")
    else:
        st.success("No critical incidents at the moment.")

    st.subheader("Incident Trend Charts")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Incidents by Severity**")
        severity_counts = severity_series.value_counts().reindex(
            ["critical", "high", "medium", "low"], fill_value=0
        )
        st.bar_chart(severity_counts)

    with chart_col2:
        st.markdown("**Incidents by Site**")
        site_counts = df_incidents["site_name"].astype(str).value_counts()
        st.bar_chart(site_counts)

    st.markdown("**Incidents by Event Type**")
    event_type_counts = df_incidents["event_type"].astype(str).value_counts()
    st.bar_chart(event_type_counts)

    st.subheader("All Active Incidents")
    st.dataframe(df_incidents, width="stretch")
else:
    st.info("No incident data returned.")


st.subheader("Ranked Actions")
ranked_actions = get_json("/ops/ranked-actions")
if ranked_actions and isinstance(ranked_actions, list) and len(ranked_actions) > 0:
    df_actions = pd.DataFrame(ranked_actions)
    st.dataframe(df_actions, width="stretch")
else:
    st.info("No ranked actions found.")


st.subheader("Shift Summary")
shift_summary = get_json("/ops/shift-summary")
if shift_summary:
    st.json(shift_summary)
else:
    st.info("No shift summary returned.")


st.subheader("Send Test Event")

with st.form("event_form"):
    site_id = st.text_input("Site ID", value="water_north")
    site_name = st.text_input("Site Name", value="North Water Plant")
    asset_id = st.text_input("Asset ID", value="pump_07")
    asset_type = st.text_input("Asset Type", value="pump")
    event_type = st.text_input("Event Type", value="pressure_alarm")
    severity = st.selectbox("Severity", ["low", "medium", "high", "critical"], index=2)
    message = st.text_input("Message", value="Pump discharge pressure above threshold")
    include_value = st.checkbox("Include numeric value", value=True)

    value = None
    if include_value:
        value = st.number_input(
            "Value",
            min_value=0.0,
            value=142.8,
            step=0.1,
            format="%.2f",
        )

    submitted = st.form_submit_button("Submit Event")

    if submitted:
        payload = {
            "site_id": site_id,
            "site_name": site_name,
            "asset_id": asset_id,
            "asset_type": asset_type,
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "topic": f"sites/{site_id}/{asset_id}/{event_type}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if include_value:
            payload["value"] = value

        result, error = post_json("/events", payload)
        if error:
            st.error(f"Failed to submit event: {error}")
        else:
            st.success("Event submitted successfully.")
            st.json(result)
