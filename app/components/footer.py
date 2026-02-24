"""Footer component for LexTransition AI."""
import streamlit as st
from engine.github_stats import get_github_stats


def render_footer():
    """Render the footer with GitHub stats and links."""
    gh_stats = get_github_stats()
    
    st.markdown(
        f"""
<div class="app-footer">
<div class="app-footer-inner" style="flex-direction: column; align-items: flex-start; gap: 12px;">
<div style="display: flex; align-items: center; gap: 15px; width: 100%; flex-wrap: wrap;">
<span class="top-chip">Offline Mode</span>
<span class="top-chip">Privacy First</span>
<a class="top-credit" href="?page=Privacy" target="_self">Privacy Policy</a>
<a class="top-credit" href="?page=FAQ" target="_self">FAQ</a>
</div>
<div style="display: flex; align-items: center; justify-content: space-between; width: 100%; flex-wrap: wrap; gap: 12px;">
<div class="footer-stats" style="display:flex; gap:10px; align-items: center;">
<div class="stat-item" title="Stars" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#eab308;">⭐</span> {gh_stats.get('stars', 0)}
</div>
<div class="stat-item" title="Forks" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#94a3b8;">🍴</span> {gh_stats.get('forks', 0)}
</div>
<div class="stat-item" title="Pull Requests" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#60a5fa;">🔄</span> {gh_stats.get('pull_requests', 0)}
</div>
<div class="stat-item" title="Open Issues" style="display:flex; align-items:center; gap:5px; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); color:#e2e8f0; font-size:12px; font-weight:600;">
<span style="color:#f87171;">🐞</span> {gh_stats.get('issues', 0)}
</div>
</div>
<div class="footer-socials" style="display:flex; gap:12px; align-items:center;">
<a href="?page=Community" target="_self" class="footer-social-link" title="Community Hub" style="display:flex; align-items:center; text-decoration:none; background:rgba(255, 255, 255, 0.05); border:1px solid rgba(255, 255, 255, 0.1); padding:6px; border-radius:6px; transition: all 0.2s ease;">
<span style="font-size:18px;">🤝</span>
</a>
<a href="https://github.com/SharanyaAchanta/LexTransition-AI" target="_blank" title="View Source on GitHub" style="display:flex; align-items:center; text-decoration:none; background:rgba(255, 255, 255, 0.05); border:1px solid rgba(255, 255, 255, 0.1); padding:6px; border-radius:6px; transition: all 0.2s ease;">
<img src="https://cdn.simpleicons.org/github/ffffff" height="18" alt="GitHub">
</a>
<a href="https://linkedin.com/in/sharanya-achanta-946297276" target="_blank" title="LinkedIn" style="opacity:0.8; transition:opacity 0.2s; display: flex;">
<img src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" height="18" alt="LinkedIn">
</a>
</div>
</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )
