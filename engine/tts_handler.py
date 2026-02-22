import os
import re
import subprocess
import shutil
import platform
from gtts import gTTS

class LegalTTSAgent:
    def __init__(self, model_path="models/tts/en_US-lessac-medium.onnx", piper_exe="piper_bin/piper/piper.exe"):
        self.model_path = model_path
        
        # 1. Platform-specific binary resolution
        if platform.system() == "Windows":
            self.piper_exe = piper_exe
        else:
            # On Linux/Docker/Streamlit Cloud, search for 'piper' in system PATH
            self.piper_exe = shutil.which("piper")

        # 2. Set the environment flag
        self.is_local_ready = self.piper_exe and os.path.exists(self.piper_exe) and os.path.exists(self.model_path)
        
        if self.is_local_ready:
            print("TTS Agent loaded successfully: Offline Piper Engine.")
        else:
            print("Local files missing (Cloud Environment). TTS gracefully defaulting to gTTS.")

    def sanitize_legal_text(self, text):
        """Translates raw markdown and abbreviations into natural speech."""
        text = re.sub(r'[*#_]', '', text)
        replacements = {
            r'\bu/s\b': 'under section',
            r'\bCrPC\b': 'Code of Criminal Procedure',
            r'\bBNSS\b': 'Bharatiya Nagarik Suraksha Sanhita',
            r'\bSec\.\b': 'Section',
            r'\bFIR\b': 'First Information Report'
        }
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text.strip()

    def generate_audio(self, text, filename="agent_voice.wav"):
        """Routes audio generation to Local (Piper) or Cloud (gTTS) based on the environment."""
        clean_text = self.sanitize_legal_text(text)
        
        # Ensure temp directory exists
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        output_file = os.path.join(temp_dir, filename)
        
        # --- Local Deployement ---
        if self.is_local_ready:
            command = [
                self.piper_exe,
                "--model", self.model_path,
                "--output_file", output_file
            ]
            try:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, stderr = process.communicate(input=clean_text.encode('utf-8'))
                
                if os.path.exists(output_file) and os.path.getsize(output_file) > 44:
                    return output_file
                else:
                    print(f"Piper failed: {stderr.decode('utf-8')}. Falling back to Cloud TTS...")
                    # If Piper fails mid-run, use gTTS
            except Exception as e:
                print(f"Subprocess error: {e}. Falling back to Cloud TTS...")

        # --- Cloud Deployement ---
        try:
            tts = gTTS(text=clean_text, lang='en', slow=False)
            tts.save(output_file)
            return output_file
        except Exception as e:
            print(f"Both local and cloud TTS has failed: {e}")
            return None

# Initialize singleton
tts_engine = LegalTTSAgent()