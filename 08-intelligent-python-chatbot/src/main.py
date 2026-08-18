from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.chatbot import ChatbotEngine

app = FastAPI(
    title="Intelligent Context-Aware Python Chatbot API",
    version="1.0.0",
    description="Conversational AI Engine Powered by NLTK Tokenization, Bag-of-Words Intent Classification, and Context Retention State Machine"
)

# Initialize Chatbot Engine instance
chatbot_engine = ChatbotEngine()

# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    message: str = Field(..., example="What are your business hours?")
    session_id: Optional[str] = Field(default="default_session", example="user_12345")

class ChatResponse(BaseModel):
    response: str
    tag: str
    confidence: float
    context: str
    session_id: str


# --- REST Routes ---

@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {
        "status": "alive",
        "service": "Intelligent Context-Aware Chatbot API",
        "intents_loaded": len(chatbot_engine.intents),
        "vocabulary_size": len(chatbot_engine.vocabulary)
    }


@app.post("/api/v1/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_endpoint(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message prompt cannot be empty.")

    result = chatbot_engine.get_response(req.message, session_id=req.session_id)
    return ChatResponse(
        response=result["response"],
        tag=result["tag"],
        confidence=result["confidence"],
        context=result["context"],
        session_id=req.session_id
    )


@app.get("/api/v1/intents", status_code=status.HTTP_200_OK)
def get_intents():
    return {
        "total_intents": len(chatbot_engine.intents),
        "tags": chatbot_engine.tags,
        "intents": chatbot_engine.intents
    }


@app.post("/api/v1/reload", status_code=status.HTTP_200_OK)
def reload_intents():
    """Reloads dataset patterns from intents.json file."""
    chatbot_engine.load_intents()
    return {
        "status": "success",
        "intents_count": len(chatbot_engine.intents),
        "vocabulary_size": len(chatbot_engine.vocabulary)
    }
