import streamlit as st
import os

# UI Components
from app.components.ui_helpers import render_agent_audio

# --- SELF-CONTAINED ENGINE IMPORTS ---
from engine import glossary as glossary_engine
from engine.tts_handler import tts_engine

# --- MAIN PAGE FUNCTION ---
def render_glossary_page():
    """Render the Legal Glossary page."""
    st.markdown("## 📖 Legal Glossary")
    st.markdown("Understand complex legal terms, Latin maxims, and procedural terminology used in Indian Law.")
    st.divider()

    # Search and Filtering
    col1, col2 = st.columns([3, 1])
    with col1:
        g_search = st.text_input("Search terms...", placeholder="e.g., Habeas Corpus, Mens Rea, Evidence")
    with col2:
        categories = ["All"] + glossary_engine.get_categories()
        g_cat = st.selectbox("Category", categories)

    # Alphabet filtering
    st.write("Browse by Letter:")
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    cols = st.columns(len(letters))
    selected_letter = None
    for i, l in enumerate(letters):
        if cols[i].button(l, key=f"letter_{l}", use_container_width=True):
            selected_letter = l

    # Results logic
    if g_search:
        results = glossary_engine.search_terms(g_search)
        st.markdown(f"**Found {len(results)} results for \"{g_search}\"**")
    elif selected_letter:
        results = glossary_engine.get_terms_by_letter(selected_letter)
        st.markdown(f"**Terms starting with \"{selected_letter}\"**")
    elif g_cat != "All":
        results = glossary_engine.get_terms_by_category(g_cat)
        st.markdown(f"**Category: {g_cat}**")
    else:
        results = glossary_engine.get_all_terms(limit=20)
        st.markdown("**Recent/Common Terms**")

    st.write("---")

    if not results:
        st.info("No matching terms found. Try searching for something else.")
    else:
        for term in results:
            with st.expander(f"**{term['term']}**"):
                st.markdown(f"**Definition:** {term['definition']}")
                if term['related_sections']:
                    st.markdown(f"**Related Sections:** `{term['related_sections']}`")
                if term['examples']:
                    st.markdown(f"**Example:** *{term['examples']}*")
                st.caption(f"Category: {term['category']}")
                
                if st.button(f"🎙️ Speak Definition", key=f"tts_{term['term']}"):
                    with st.spinner("Preparing audio..."):
                        audio_path = tts_engine.generate_audio(term['definition'], f"temp_term_{term['term']}.wav")
                        if audio_path and os.path.exists(audio_path):
                            render_agent_audio(audio_path, title=f"Term: {term['term']}")