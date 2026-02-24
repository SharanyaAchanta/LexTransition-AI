"""Header navigation component for LexTransition AI."""
import html as html_lib
import streamlit as st
from app.config import NAV_ITEMS


def render_header():
    """Render the header navigation bar."""
    header_links = []
    for page, label in NAV_ITEMS:
        page_html = html_lib.escape(page)
        label_html = html_lib.escape(label)
        active_class = "active" if st.session_state.current_page == page else ""
        current_theme = st.session_state.get("theme", "dark")

        header_links.append(
            f'<a class="top-nav-link {active_class}" href="?page={page_html}&theme={current_theme}" target="_self" '
            f'title="{label_html}" aria-label="{label_html}">{label_html}</a>'
        )

    st.markdown(
        f"""
<a class="site-logo" href="?page=Home&theme={st.session_state.theme}" target="_self"><span class="logo-icon">⚖️</span><span class="logo-text">LexTransition AI</span></a>

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
