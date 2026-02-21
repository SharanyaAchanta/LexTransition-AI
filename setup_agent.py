import os
import urllib.request
import zipfile
import platform

def download_file(url, dest_path):
    print(f"⏳ Downloading {os.path.basename(dest_path)}...")
    urllib.request.urlretrieve(url, dest_path)
    print(f"✅ Saved to {dest_path}")

def setup_tts():
    print("🚀 Initializing Lextransition-AI TTS Agent Setup...")
    
    # 1. Create Model Directory
    os.makedirs("models/tts", exist_ok=True)
    
    # 2. Download Voice Model & Config
    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    model_path = "models/tts/en_US-lessac-medium.onnx"
    config_path = model_path + ".json"
    
    if not os.path.exists(model_path):
        download_file(base_url, model_path)
        download_file(base_url + ".json", config_path)
    else:
        print("✅ Voice model already exists. Skipping download.")

    # 3. Handle Windows-Specific Piper Binary
    if platform.system() == "Windows":
        piper_exe_path = "piper_bin/piper/piper.exe"
        if not os.path.exists(piper_exe_path):
            print("🪟 Windows OS detected. Fetching standalone Piper binary...")
            zip_url = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
            zip_path = "piper_windows.zip"
            
            download_file(zip_url, zip_path)
            
            print("📦 Extracting Piper binary...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("piper_bin")
                
            os.remove(zip_path)
            print("✅ Piper binary extraction complete.")
        else:
            print("✅ Windows Piper binary already exists. Skipping download.")
    else:
        print("🐧 Non-Windows OS detected. Relying on standard piper-tts Python package.")

    print("\n🎉 TTS Agent Setup Complete! You are ready to run the app.")

if __name__ == "__main__":
    setup_tts()