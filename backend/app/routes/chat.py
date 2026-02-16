from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.database.connection import get_db
from app.services.chatbot_service import ChatbotService

router = APIRouter()

# Schema Definition
class ChatContext(BaseModel):
    prediction_id: Optional[int] = None
    universe: Optional[str] = "mundo"
    session_id: Optional[str] = None # Added log to support session awareness
    provider: Optional[str] = "deepseek"

class ChatMessageRequest(BaseModel):
    message: str
    context: Optional[ChatContext] = None

class ChatMessageResponse(BaseModel):
    text: str
    actions: List[str] = []

# Dependency
def get_chatbot_service():
    return ChatbotService()

@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    req: ChatMessageRequest, 
    db: Session = Depends(get_db),
    chatbot: ChatbotService = Depends(get_chatbot_service)
):
    """
    Process a user message through the Katula AI Analyst.
    """
    try:
        # Convert Pydantic context to dict for service
        context_dict = req.context.dict() if req.context else {}
        
        response = chatbot.process_message(db, req.message, context_dict)
        
        return ChatMessageResponse(
            text=response.get("text", "Je ne sais pas quoi dire."),
            actions=response.get("actions", [])
        )
    except Exception as e:
        print(f"Error in Chatbot API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
