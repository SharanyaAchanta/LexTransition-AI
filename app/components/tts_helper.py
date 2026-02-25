"""TTS (Text-to-Speech) helper component for LexTransition AI."""
import os
import base64
import streamlit as st


def render_agent_audio(audio_path, title="🎙️ AI Agent Dictation"):
    """Wraps the audio player in a premium custom HTML card.
    
    Args:
        audio_path: Path to the audio file
        title: Title to display above the audio player
    """
    if not os.path.exists(audio_path):
        return
    
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    
    # Encode the audio so we can embed it directly in the HTML
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    # Custom CSS and HTML structure using flexible rgba colors for dark/light mode compatibility
    custom_html = f"""
    <div style="
        border: 1px solid rgba(128, 128, 128, 0.3);
        border-radius: 8px;
        padding: 12px 15px;
        background: rgba(128, 128, 128, 0.05);
        display: flex;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <div style="margin-right: 15px; font-size: 1.8em;">🤖</div>
        <div style="flex-grow: 1;">
            <div style="font-size: 0.9em; font-weight: 600; opacity: 0.8; margin-bottom: 6px; font-family: sans-serif;">
                {title}
            </div>
            <audio controls style="width: 100%; height: 35px; border-radius: 4px; outline: none;">
                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        </div>
    </div>
    """
    st.markdown(custom_html, unsafe_allow_html=True)


def generate_tts_and_play(text, filename, title="🎙️ Audio"):
    """Generate TTS audio and play it.
    
    Args:
        text: Text to convert to speech
        filename: Output filename for the audio
        title: Title to display above the audio player
        
    Returns:
        True if successful, False otherwise
    """
    from engine.tts_handler import tts_engine
    
    with st.spinner("🎙️ Agent is preparing audio..."):
        audio_path = tts_engine.generate_audio(text, filename)
        if audio_path and os.path.exists(audio_path):
            render_agent_audio(audio_path, title=title)
            return True
    return False
