import streamlit as st
import base64

def render_agent_audio(audio_path, title="🎙️ AI Agent Dictation"):
    """Wraps the audio player in a premium custom HTML card."""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    custom_html = f"""
    <div style="border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 8px; padding: 12px 15px; background: rgba(128, 128, 128, 0.05); display: flex; align-items: center; margin-top: 10px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="margin-right: 15px; font-size: 1.8em;">🤖</div>
        <div style="flex-grow: 1;">
            <div style="font-size: 0.9em; font-weight: 600; opacity: 0.8; margin-bottom: 6px; font-family: sans-serif;">{title}</div>
            <audio controls style="width: 100%; height: 35px; border-radius: 4px; outline: none;">
                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            </audio>
        </div>
    </div>
    """
    st.markdown(custom_html, unsafe_allow_html=True)

def copy_to_clipboard(text, label="Copy"):
    """Render copy-to-clipboard button."""
    import streamlit.components.v1 as components
    if not text: return
    button_id = f"copy_btn_{abs(hash(text))}"
    
    html_code = f"""
        <button id="{button_id}" style="background:#2563eb; color:white; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:12px; margin-bottom:6px;">
            📋 {label}
        </button>
        <script>
        const btn = document.getElementById("{button_id}");
        btn.onclick = function() {{
            navigator.clipboard.writeText(`{text}`);
            btn.innerText = "✅ Copied";
        }};
        </script>
    """
    components.html(html_code, height=40)