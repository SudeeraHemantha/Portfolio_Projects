from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.assistant import JarvisAssistant
from src.commands import get_system_metrics

app = FastAPI(
    title="Jarvis Voice-Activated Desktop Assistant API",
    version="1.0.0",
    description="Voice Recognition (STT), pyttsx3 Text-to-Speech (TTS), and System Automation Engine"
)

# Initialize Assistant Instance
jarvis = JarvisAssistant()

# --- Pydantic Schemas ---
class VoiceCommandRequest(BaseModel):
    command: str = Field(..., example="System status report")

class VoiceCommandResponse(BaseModel):
    command_input: str
    action_taken: str
    spoken_response: str
    data: Optional[dict] = None


# --- REST Routes ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {
        "status": "alive",
        "service": "Jarvis Voice Assistant API",
        "wake_word": jarvis.wake_word,
        "tts_engine": "pyttsx3 active" if jarvis.synthesizer.tts_engine else "silent mode"
    }


@app.post("/api/v1/voice/command", response_model=VoiceCommandResponse, status_code=status.HTTP_200_OK)
def execute_voice_command(req: VoiceCommandRequest):
    if not req.command or not req.command.strip():
        raise HTTPException(status_code=400, detail="Voice command prompt cannot be empty.")

    res = jarvis.process_prompt(req.command)
    return VoiceCommandResponse(
        command_input=req.command,
        action_taken=res.get("action", "unknown"),
        spoken_response=res.get("spoken_response", ""),
        data=res.get("data")
    )


@app.get("/api/v1/system/status", status_code=status.HTTP_200_OK)
def get_system_status_api():
    """Queries current host system performance metrics."""
    return get_system_metrics()
