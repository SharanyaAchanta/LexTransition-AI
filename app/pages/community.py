"""Community Hub page for LexTransition AI."""
import streamlit as st
from engine.github_stats import get_github_stats


def render_community_page():
    """Render the Community Hub page."""
    st.markdown("## 🤝 Community Hub")
    st.markdown("Join us in building the future of offline legal technology in India.")
    st.divider()
    
    gh_stats = get_github_stats()
    
    # Stats Dashboard
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("⭐ Stars", gh_stats.get('stars', 0))
    with c2:
        st.metric("🍴 Forks", gh_stats.get('forks', 0))
    with c3:
        st.metric("🔄 Pull Requests", gh_stats.get('pull_requests', 0))
    with c4:
        st.metric("🐞 Open Issues", gh_stats.get('issues', 0))
        
    st.write("###")
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.markdown("""
        ### 🚀 How to Contribute
        Whether you are a developer, a legal professional, or a student, your help is invaluable!
        
        - **Report Bugs**: Found an edge case in transition mapping? Let us know.
        - **Improve Mappings**: Help us verify more sections between IPC and BNS.
        - **Code**: Check out our 'Good First Issues' on GitHub.
        - **Documentation**: Help us make the legal explanations clearer for everyone.
        """)
        
        st.markdown("""
        <a href="https://github.com/SharanyaAchanta/LexTransition-AI" target="_blank" style="text-decoration:none;">
            <div style="background:rgba(203, 166, 99, 0.1); border:1px solid rgba(203, 166, 99, 0.4); padding:20px; border-radius:10px; text-align:center;">
                <h3 style="color:#cb924f; margin:0;">View on GitHub</h3>
                <p style="color:#94a3b8; margin:10px 0 0;">Browse the source code, issues, and discussions.</p>
            </div>
        </a>
        """, unsafe_allow_html=True)
        
    with col_side:
        st.markdown("""
        ### 📜 Project Info
        - **License**: MIT
        - **Stack**: Python, Streamlit, Ollama
        - **Goal**: Privacy-first legal awareness.
        """)
        st.info("💡 **Tip**: Mention this project on LinkedIn to help more legal professionals transition to the new laws!")
