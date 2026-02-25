"""IPC to BNS Mapper page for LexTransition AI."""
import html as html_lib
import time
import streamlit as st
from app.components.tts_helper import render_agent_audio


def render(ENGINES_AVAILABLE):
    """Render the IPC → BNS Mapper page.
    
    Args:
        ENGINES_AVAILABLE: Boolean indicating if engines are available
    """
    st.markdown("## ✓ IPC → BNS Transition Mapper")
    st.markdown("Convert old IPC sections into new BNS equivalents with legal-grade accuracy.")
    st.divider()
    
    # Input Section
    st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("Enter IPC Section", placeholder="e.g., 420, 302, 378")
    with col2:
        st.write("#") # Spacer
        search_btn = st.button("🔍 Find BNS Eq.", use_container_width=True)

    # Import required functions
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.comparator import compare_ipc_bns
    from engine.llm import summarize as llm_summarize
    from engine.tts_handler import tts_engine

    # --- STEP 1: Handle Search Logic & State ---
    if search_query and search_btn:
        if ENGINES_AVAILABLE:
            with st.spinner("Searching database..."):
                res = map_ipc_to_bns(search_query.strip())
                if res:
                    st.session_state['last_result'] = res
                    st.session_state['last_query'] = search_query.strip()
                    # Reset analysis view for new search
                    st.session_state['active_analysis'] = None 
                    st.session_state['active_view_text'] = False
                else:
                    st.session_state['last_result'] = None
                    st.error(f"❌ Section IPC {search_query} not found in database.")
        else:
            st.error("❌ Engines are offline. Cannot perform database lookup.")

    st.divider()

    # --- STEP 2: Render Persistent Results ---
    # We check session_state instead of search_btn so results survive refreshes
    if st.session_state.get('last_result'):
        result = st.session_state['last_result']
        ipc = st.session_state['last_query']
        bns = result.get("bns_section", "N/A")
        notes = result.get("notes", "See source mapping.")
        source = result.get("source", "mapping_db")
        
        # Render Result Card
        st.markdown(f"""
        <div class="result-card">
            <div class="result-badge">Mapping • found</div>
            <div class="result-grid">
                <div class="result-col">
                    <div class="result-col-title">IPC Section</div>
                    <div style="font-size:20px;font-weight:700;color:var(--text-color);margin-top:6px;">{html_lib.escape(ipc)}</div>
                </div>
                <div class="result-col">
                    <div class="result-col-title">BNS Section</div>
                    <div style="font-size:20px;font-weight:700;color:var(--primary-color);margin-top:6px;">{html_lib.escape(bns)}</div>
                </div>
            </div>
            <ul class="result-list"><li>{html_lib.escape(notes)}</li></ul>
            <div style="font-size:12px;opacity:0.8;margin-top:10px;">Source: {html_lib.escape(source)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("###")

        # --- STEP 3: Action Buttons ---
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🤖 Analyze Differences (AI)", use_container_width=True):
                st.session_state['active_analysis'] = ipc
                st.session_state['active_view_text'] = False

        with col_b:
            if st.button("📄 View Raw Text", use_container_width=True):
                st.session_state['active_view_text'] = True
                st.session_state['active_analysis'] = None

        with col_c:
            if st.button("📝 Summarize Note", use_container_width=True):
                st.session_state['active_analysis'] = None
                st.session_state['active_view_text'] = False
                summary = llm_summarize(notes, question=f"Changes in {ipc}?")
                if summary: 
                    st.success(f"Summary: {summary}")

                    # --- TTS INTEGRATION START (Summary) ---
                    with st.spinner("🎙️ Agent is preparing audio..."):
                        audio_path = tts_engine.generate_audio(summary, "temp_summary.wav")
                        if audio_path and __import__('os').path.exists(audio_path):
                            render_agent_audio(audio_path, title="Legal Summary Dictation")
                    # --- TTS INTEGRATION END ---

                else:
                    st.error("❌ LLM Engine failed to generate summary.")

        # --- STEP 4: Persistent Views (Rendered outside the columns) ---
        
        # 1. AI Analysis View
        if st.session_state.get('active_analysis') == ipc:
            st.divider()
            with st.spinner("Talking to Ollama (AI)..."):
                comp_result = compare_ipc_bns(ipc)
                analysis_text = comp_result.get('analysis', "")
                
                # Check for tag defined in comparator.py
                if "ERROR:" in analysis_text or "Error" in analysis_text or "Connection Error" in analysis_text:
                    st.error(f"❌ AI Error: {analysis_text.replace('ERROR:', '')}")
                    st.info("💡 Make sure Ollama is running (`ollama serve`) and you have pulled the model (`ollama pull llama3`).")
                else:
                    # Final 3-column analysis layout
                    c1, c2, c3 = st.columns([1, 1.2, 1])
                    with c1:
                        st.markdown(f"**📜 IPC {ipc} Text**")
                        st.info(comp_result.get('ipc_text', 'No text available.'))
                    with c2:
                        st.markdown("**🤖 AI Comparison**")
                        st.success(analysis_text)

                    with c3:
                        st.markdown(f"**⚖️ {bns} Text**")
                        st.warning(comp_result.get('bns_text', 'No text available.'))

                    with c2:
                        # --- TTS INTEGRATION START (AI Analysis) ---
                        with st.spinner("🎙️ Agent is analyzing text for dictation..."):
                            audio_path = tts_engine.generate_audio(analysis_text, "temp_analysis.wav")
                            if audio_path and __import__('os').path.exists(audio_path):
                                render_agent_audio(audio_path, title="AI Transition Analysis")
                        # --- TTS INTEGRATION END ---

        # 2. Raw Text View
        elif st.session_state.get('active_view_text'):
            st.divider()
            v1, v2 = st.columns(2)
            with v1:
                st.markdown("**IPC Original Text**")
                st.text_area("ipc_raw", result.get('ipc_full_text', 'No text found in DB'), height=250, disabled=True)
            with v2:
                st.markdown("**BNS Updated Text**")
                st.text_area("bns_raw", result.get('bns_full_text', 'No text found in DB'), height=250, disabled=True)

    # Add Mapping Form (for when sections aren't found)
    with st.expander("➕ Add New Mapping to Database"):
        n_ipc = st.text_input("New IPC Section", value=search_query)
        n_bns = st.text_input("New BNS Section")
        n_ipc_text = st.text_area("IPC Legal Text")
        n_bns_text = st.text_area("BNS Legal Text")
        n_notes = st.text_input("Short Summary/Note")
        
        if st.button("Save to Database"):
            if not n_ipc or not n_bns:
                st.warning("⚠️ IPC and BNS section numbers are required.")
            else:
                success = add_mapping(n_ipc, n_bns, n_ipc_text, n_bns_text, n_notes)
                if success:
                    st.success(f"✅ IPC {n_ipc} successfully mapped to {n_bns} and saved.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Database Error: Failed to save mapping. Is the database file locked or missing?")

        st.markdown("<br>", unsafe_allow_html=True)
