"""
Search History Activity View for LexTransition-AI
Displays user search history and allows clearing the log.
"""
import streamlit as st
from engine import history_manager

def render_history_page():
    st.markdown("## 🕑 Search History")
    st.markdown("View your recent mapping/search activity.")
    st.divider()

    history = history_manager.load_history()
    if not history:
        st.info("No search history found.")
    else:
        # Show as table
        st.write("### Recent Searches")
        st.dataframe([
            {
                "Time": h["timestamp"],
                "Query": h["query"],
                "Result": h["result"][:100] + ("..." if len(h["result"]) > 100 else "")
            }
            for h in reversed(history)
        ])

    if st.button("🗑️ Clear History", use_container_width=True):
        history_manager.clear_history()
        st.success("Search history cleared.")
        st.experimental_rerun()

# For Streamlit page discovery
if __name__ == "__main__":
    render_history_page()
