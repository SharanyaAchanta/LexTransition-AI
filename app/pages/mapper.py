"""IPC to BNS Mapper page for LexTransition AI."""
import streamlit as st
import os
import re
import time
import html as html_lib

# UI Components
from app.components.ui_helpers import copy_to_clipboard, render_agent_audio

# Intent and Audio Engines
from engine.stt_handler import get_stt_engine
from streamlit_mic_recorder import mic_recorder
from engine.intent_parser import parse_intent
from engine.tts_handler import tts_engine
from engine.bookmark_manager import add_bookmark
from engine.autocomplete import get_suggestions
from engine.pdf_exporter import generate_pdf_report
import base64

# --- SELF-CONTAINED ENGINE CHECK ---
try:
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.comparator import compare_ipc_bns
    from engine.llm import summarize as llm_summarize
    ENGINES_AVAILABLE = True
except Exception as e:
    ENGINES_AVAILABLE = False
    
# Stub for LLM if it fails
if not ENGINES_AVAILABLE:
    def llm_summarize(text, question=None): return None

def render_mapper_page():
    """Render the IPC → BNS Mapper page.
    
    Args:
        ENGINES_AVAILABLE: Boolean indicating if engines are available
    """
    st.markdown("## ✓ IPC → BNS Transition Mapper")
    st.markdown("Convert old IPC sections into new BNS equivalents with legal-grade accuracy.")
    st.divider()
    
    # Input Section Wrapper
    st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)
    
    # --- 3-column layout: Input | Mic | Search ---
    col1, col2, col3 = st.columns([3,1,1])

    with col1:
        search_query = st.text_input(
            "Search",
            value=st.session_state.get('mapper_search_val', ''),
            placeholder="e.g., 420, 302, 378",
            label_visibility="collapsed"
        )

        suggestions = get_suggestions(search_query)

        if suggestions:
            selected = st.selectbox(
                "",
                suggestions,
                index=None,
                placeholder="Suggestions...",
                key="autocomplete_select"
            )

            if selected:
                st.session_state['mapper_search_val'] = selected
                st.session_state['auto_search'] = True
                st.rerun()

    with col2:
        audio_dict = mic_recorder(
            start_prompt="🎙️ Speak",
            stop_prompt="🛑 Stop",
            key='mapper_mic',
            use_container_width=True
        )

    with col3:
        search_btn = st.button("🔍 Find BNS Eq.", use_container_width=True)

    # --- Process Audio ---
    audio_val = audio_dict['bytes'] if audio_dict else None
    
    if audio_val and audio_val != st.session_state.get("last_audio_mapper"):
        st.session_state["last_audio_mapper"] = audio_val 
        
        temp_path = "temp_audio/mapper_audio.wav"
        os.makedirs("temp_audio", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(audio_val)
            
        with st.spinner("🎙️ Agent is listening..."):
            stt_engine = get_stt_engine() 
            text = stt_engine.transcribe_audio(temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            if text and text.strip() and not text.startswith("Error:"):
                intent_data = parse_intent(text)
                target = intent_data.get("target")
                action = intent_data.get("action")
                payload = intent_data.get("payload")
                
                voice_query = target if target else text.strip()
                
                st.session_state['mapper_search_val'] = voice_query
                st.session_state['auto_search'] = True 
                
                # --- SAFELY INJECT UI TRIGGERS ---
                if action == "analyze":
                    st.session_state['auto_analyze'] = True
                    
                elif action == "raw_text":
                    st.session_state['auto_raw_text'] = True
                    
                elif action == "summarize":
                    st.session_state['auto_summarize'] = True
                    
                elif action == "bookmark_add":
                    st.session_state['auto_bookmark_trigger'] = True
                    st.session_state['auto_bookmark_note'] = payload if payload else ""
                    
                elif action == "export_pdf":
                    st.session_state['auto_export_pdf'] = True
                    
                st.rerun()

    # --- Auto-Search from Voice ---
    if st.session_state.get('auto_search'):
        search_btn = True # Spoof the button click
        st.session_state['auto_search'] = False # Instantly reset the flag

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
        copy_text = f"IPC {ipc} → BNS {bns}\nNotes: {notes}\nSource: {source}"
        copy_to_clipboard(copy_text, "Copy Mapping")
        st.text_input(
"Optional Notes",
key="bookmark_notes_input",
placeholder="Add your personal notes here..."
)
        
        st.write("###")

        # --- STEP 3: Action Buttons ---
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            # Catch Analyze
            if st.button("🤖 Analyze Differences (AI)", use_container_width=True) or st.session_state.pop('auto_analyze', False):
                st.session_state['active_analysis'] = ipc
                st.session_state['active_view_text'] = False

        with col_b:
            # Catch Raw Text
            if st.button("📄 View Raw Text", use_container_width=True) or st.session_state.pop('auto_raw_text', False):
                st.session_state['active_view_text'] = True
                st.session_state['active_analysis'] = None

        with col_c:
            # Catch Summarize
            if st.button("📝 Summarize Note", use_container_width=True) or st.session_state.pop('auto_summarize', False):
                st.session_state['active_analysis'] = None
                st.session_state['active_view_text'] = False
                summary = llm_summarize(notes, question=f"Changes in {ipc}?")
                if summary: 
                    st.success(f"Summary: {summary}")

                    # TTS INTEGRATION
                    with st.spinner("🎙️ Agent is preparing audio..."):
                        audio_path = tts_engine.generate_audio(summary, "temp_summary.wav")
                        if audio_path and os.path.exists(audio_path):
                            render_agent_audio(audio_path, title="Legal Summary Dictation")
                else:
                    st.error("❌ LLM Engine failed to generate summary.")

        with col_d:
            # Catch Export PDF
            if st.button("📄 Export PDF", use_container_width=True) or st.session_state.pop('auto_export_pdf', False):
                try:
                    mapping_data = {
                        "IPC Section": ipc,
                        "BNS Section": bns,
                        "Notes": notes,
                        "Source": source,
                    }
                    pdf_path = generate_pdf_report(
                        filename=f"mapping_{ipc}.pdf",
                        mapping_data=mapping_data,
                    )
                    
                    # Read the file bytes
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()

                    # --- AUTO-DOWNLOAD JAVASCRIPT INJECTION ---
                    # Encode PDF to base64
                    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                    filename = f"mapping_{ipc}.pdf"
                    
                    # Create an invisible HTML link and force JavaScript to click it instantly
                    auto_download_html = f"""
                        <a id="auto-dl-{ipc}" href="data:application/pdf;base64,{b64_pdf}" download="{filename}"></a>
                        <script>
                            document.getElementById('auto-dl-{ipc}').click();
                        </script>
                    """
                    # Inject the code invisibly into the app
                    st.components.v1.html(auto_download_html, height=0)

                    st.success("✅ PDF generated and downloaded automatically!")

                    # Fallback button just in case the user has strict pop-up blockers enabled
                    st.download_button(
                        "⬇ Click if download didn't start",
                        pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                    )

                except Exception as e:
                    st.error(f"❌ Failed to generate PDF: {e}")

            # Catch Bookmark (Using the safer boolean trigger!)
            auto_bookmark_trigger = st.session_state.pop('auto_bookmark_trigger', False)
            auto_bookmark_note = st.session_state.pop('auto_bookmark_note', "")
            
            if st.button("🔖 Save to Bookmarks", use_container_width=True) or auto_bookmark_trigger:
                try:
                    section = f"IPC {ipc} → {bns}"
                    title = notes if notes else f"IPC {ipc}"
                    # Check if it was voice-triggered; if not, grab the text input
                    user_notes = auto_bookmark_note if auto_bookmark_trigger else st.session_state.get("bookmark_notes_input", "")

                    add_bookmark(section, title, user_notes)
                    st.success("✅ Saved to bookmarks successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to save bookmark: {e}") 
        
        # Catch Copy Mapping (Placed outside columns since it uses JS clipboard component)
        if st.session_state.pop('auto_copy_mapping', False):
            # We show a toast because web browsers block auto-copying without a physical mouse click
            st.toast("📋 Mapping copied! (Note: Please click the 'Copy Mapping' icon to confirm browser clipboard access).")           

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
                        copy_to_clipboard(analysis_text, "Copy Analysis")

                    with c3:
                        st.markdown(f"**⚖️ {bns} Text**")
                        st.warning(comp_result.get('bns_text', 'No text available.'))

                    with c2:
                        # --- TTS INTEGRATION START (AI Analysis) ---
                        with st.spinner("🎙️ Agent is analyzing text for dictation..."):
                            audio_path = tts_engine.generate_audio(analysis_text, "temp_analysis.wav")
                            if audio_path and os.path.exists(audio_path):
                                # Replace st.audio with your new custom UI function
                                render_agent_audio(audio_path, title="AI Transition Analysis")
                        # --- TTS INTEGRATION END ---

        # 2. Raw Text View
        elif st.session_state.get('active_view_text'):
            st.divider()
            v1, v2 = st.columns(2)
            with v1:
                st.markdown("**IPC Original Text**")
                copy_to_clipboard(result.get('ipc_full_text', ''), "Copy IPC Text")
                st.text_area(
                    "ipc_raw",
                    result.get('ipc_full_text', 'No text found in DB'),
                    height=250,
                    disabled=True
                )
            with v2:
                st.markdown("**BNS Updated Text**")
                copy_to_clipboard(result.get('bns_full_text', ''), "Copy BNS Text")
                st.text_area(
                    "bns_raw",
                    result.get('bns_full_text', 'No text found in DB'),
                    height=250,
                    disabled=True
                )

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
