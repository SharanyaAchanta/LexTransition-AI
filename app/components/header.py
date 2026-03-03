import streamlit as st
import html as html_lib
from app.components.theme import toggle_theme

def render_header(nav_items, current_page):
    """Renders the top navigation bar and theme toggle."""
    # Theme Toggle Button
    col1, col2 = st.columns([10, 1])
    with col2:
        icon = "🌙" if st.session_state.theme == "dark" else "☀️"
        if st.button(icon, key="theme_toggle"):
            toggle_theme()
            st.rerun()

    # Generate Nav Links
    header_links = []
    for page, label in nav_items:
        page_html = html_lib.escape(page)
        label_html = html_lib.escape(label)
        active_class = "active" if current_page == page else ""
        current_theme = st.session_state.get("theme", "dark")
        header_links.append(
            f'<a class="top-nav-link {active_class}" href="?page={page_html}&theme={current_theme}" target="_self" '
            f'title="{label_html}" aria-label="{label_html}">{label_html}</a>'
        )

    # Render HTML
    st.markdown(
        f"""
        <a class="site-logo" href="?page=Home&theme={st.session_state.theme}" target="_self">
            <span class="logo-icon">⚖️</span><span class="logo-text">LexTransition AI</span>
        </a>
        <div class="top-header">
          <div class="top-header-inner">
            <div class="top-header-left">
              <a class="top-brand" href="?page=Home" target="_self">LexTransition AI</a>
            </div>
            <div class="top-header-center">
              <div class="top-nav">{''.join(header_links)}</div>
              <a class="top-cta" href="?page=Fact" target="_self">Get Started</a>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )