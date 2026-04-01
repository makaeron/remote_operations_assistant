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

if incidents and isinstance(incidents, list) and len(incidents) > 0:
    df_incidents = pd.DataFrame(incidents)

    # Make sure columns exist before using them
    if "severity" not in df_incidents.columns:
        df_incidents["severity"] = "unknown"

    if "site_name" not in df_incidents.columns:
        df_incidents["site_name"] = "Unknown Site"

    if "event_type" not in df_incidents.columns:
        df_incidents["event_type"] = "unknown_event"

    if "asset_id" not in df_incidents.columns:
        df_incidents["asset_id"] = "unknown_asset"

    # -----------------------------
    # Summary metrics
    # -----------------------------
    total_incidents = len(df_incidents)
    critical_count = len(df_incidents[df_incidents["severity"].str.lower() == "critical"])
    high_count = len(df_incidents[df_incidents["severity"].str.lower() == "high"])
    medium_count = len(df_incidents[df_incidents["severity"].str.lower() == "medium"])
    low_count = len(df_incidents[df_incidents["severity"].str.lower() == "low"])

    st.subheader("Incident Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Incidents", total_incidents)
    col2.metric("Critical", critical_count)
    col3.metric("High", high_count)
    col4.metric("Medium", medium_count)
    col5.metric("Low", low_count)

    # -----------------------------
    # Critical Incident section
    # -----------------------------
    st.subheader("Critical Incident Section")

    df_critical = df_incidents[df_incidents["severity"].str.lower() == "critical"].copy()

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
                "created_at"
            ] if col in df_critical.columns
        ]

        st.dataframe(
            df_critical[critical_display_cols].reset_index(drop=True),
            width="stretch"
        )
    else:
        st.success("No critical incidents at the moment.")

    # -----------------------------
    # Trend charts
    # -----------------------------
    st.subheader("Incident Trend Charts")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Incidents by Severity**")
        severity_counts = (
            df_incidents["severity"]
            .str.lower()
            .value_counts()
            .reindex(["critical", "high", "medium", "low"], fill_value=0)
        )
        st.bar_chart(severity_counts)

    with chart_col2:
        st.markdown("**Incidents by Site**")
        site_counts = df_incidents["site_name"].value_counts()
        st.bar_chart(site_counts)

    # -----------------------------
    # Optional event type chart
    # -----------------------------
    st.markdown("**Incidents by Event Type**")
    event_type_counts = df_incidents["event_type"].value_counts()
    st.bar_chart(event_type_counts)

    # -----------------------------
    # Full incident table
    # -----------------------------
    st.subheader("All Active Incidents")
    st.dataframe(df_incidents, width="stretch")

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
    site_name = st.text_input("Site Name", value="North Water Plant")
    asset_id = st.text_input("Asset ID", value="pump_07")
    asset_type = st.text_input("Asset Type", value="pump")
    event_type = st.text_input("Event Type", value="pressure_alarm")
    severity = st.selectbox("Severity", ["low", "medium", "high", "critical"], index=2)
    message = st.text_input("Message", value="Pump discharge pressure above threshold")
    value = st.number_input(
        "Value",
        min_value=0.0,
        value=142.8,
        step=0.1,
        format="%.2f"
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
            "value": value
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


st.title("Remote Operations Assistant Dashboard")

metrics = requests.get("http://127.0.0.1:8000/ops/metrics").json()

st.subheader("Pipeline Metrics")
st.metric("Total Events", metrics["total_events"])
st.metric("Accepted Events", metrics["accepted_events"])
st.metric("Ingestion Success Rate", f"{metrics['ingestion_success_rate']*100:.2f}%")
st.metric("Duplicate Rate", f"{metrics['duplicate_rate']*100:.2f}%")
st.metric("Validation Rejection Rate", f"{metrics['validation_rejection_rate']*100:.2f}%")
st.metric("Avg Freshness Delay", f"{metrics['avg_freshness_delay_ms']:.2f} ms")