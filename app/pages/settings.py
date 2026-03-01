"""Settings page for LexTransition AI."""
import streamlit as st
from engine.system_status import get_system_status
from engine.resource_monitor import get_resource_usage

def render_settings_page():
    """Render the Settings/About page.
    
    Args:
        ENGINES_AVAILABLE: Boolean indicating if engines are available
    """
    st.markdown("## ⚙️ Settings / System Status")
    st.markdown("View system health and engine availability.")
    st.divider()

    status = get_system_status()

    st.markdown("### 🖥️ System Health Dashboard")

    col1, col2 = st.columns(2)

    items = list(status.items())

    for i, (name, ok) in enumerate(items):
        with (col1 if i % 2 == 0 else col2):
            if ok:
                st.success(f"🟢 {name} — Available")
            else:
                st.error(f"🔴 {name} — Not Available")

    st.info("If any module shows Not Available, please check installation or configuration.")

    st.markdown("### 📊 Resource Usage Monitor")

    usage = get_resource_usage()

    if usage:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("CPU Usage", f"{usage['cpu']} %")

        with col2:
            st.metric(
                "RAM Usage",
                f"{usage['ram_percent']} %",
                f"{usage['ram_used_gb']} / {usage['ram_total_gb']} GB"
            )

        with col3:
            st.metric(
                "Disk Usage",
                f"{usage['disk_percent']} %",
                f"{usage['disk_used_gb']} / {usage['disk_total_gb']} GB"
            )

    else:
        st.warning("Resource monitor unavailable.")