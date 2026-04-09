import whisper
import os

model = whisper.load_model("base")

def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        return "Audio file not found."

    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        return f"Transcription error: {str(e)}"