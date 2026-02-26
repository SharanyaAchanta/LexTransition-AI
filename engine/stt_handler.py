import os
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
            

# Attempt to import the local engine
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

class LegalSTTAgent:
    def __init__(self):
        """Initializes the Agent and loads the model into RAM exactly once."""
        self.is_local_ready = FASTER_WHISPER_AVAILABLE
        self.model = None
        
        if self.is_local_ready:
            try:
                print("✅ Loading local faster-whisper model into RAM...")
                self.model = WhisperModel("base", device="cpu", compute_type="int8")
            except Exception as e:
                print(f"☁️ Cloud Environment / Missing libraries detected ({e}).")
                self.is_local_ready = False
        else:
            print("☁️ Cloud Environment Detected. STT gracefully defaulting to SpeechRecognition.")

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Routes the transcription to the Local Model or Cloud Fallback."""
        
        # --- Local Deployment ---
        if self.is_local_ready and self.model:
            try:
                # Transcribe the audio file locally
                segments, _ = self.model.transcribe(audio_file_path, beam_size=5)
                text = " ".join([segment.text for segment in segments])
                return text.strip()
            except Exception as e:
                print(f"⚠️ Local Whisper failed during transcription: {e}. Falling back to Cloud...")

        # --- Cloud Deployment ---
        try:
            print("Routing audio to SpeechRecognition fallback...")
            # Load the raw audio file
            audio = AudioSegment.from_file(audio_file_path)
            
            # Export it to a temporary true WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                audio.export(temp_wav.name, format="wav")
                true_wav_path = temp_wav.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(true_wav_path) as source:
                audio_data = recognizer.record(source)
                result = recognizer.recognize_google(audio_data) # Ping G-Web Speech API
                
            # Clean up the converted temp file
            if os.path.exists(true_wav_path):
                os.remove(true_wav_path)
                
            return result
            
        except ImportError:
            print("Missing pydub. Please run: pip install pydub")
            return "Error: Missing pydub library for audio conversion."
        except Exception as e:
            print(f"Both local and cloud STT failed: {e}")
            return "Error: Could not transcribe audio."


@st.cache_resource(show_spinner=False, ttl=3600)
def get_stt_engine():
    """Ensures the Agent is only created once per session"""
    return LegalSTTAgent()
