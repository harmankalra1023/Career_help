import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.config import settings
from app.services.llm.client import get_llm_client

router = APIRouter(prefix="/me/mentor", tags=["mentor"])


class ChatMessage(BaseModel):
    message: str
    target_role: Optional[str] = "Backend Engineer"


class ChatResponse(BaseModel):
    provider: str
    model: str
    reply: str
    suggested_actions: List[str]


@router.get("/status")
async def get_llm_status():
    has_groq_key = bool(settings.GROQ_API_KEY and "your_" not in settings.GROQ_API_KEY.lower())
    return {
        "provider": settings.LLM_PROVIDER,
        "model": settings.GROQ_MODEL if settings.LLM_PROVIDER == "groq" else settings.LLM_MODEL,
        "has_api_key": has_groq_key,
        "base_url": settings.GROQ_BASE_URL,
        "status": "ready" if (has_groq_key or settings.LLM_PROVIDER == "mock") else "api_key_required"
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_with_mentor(msg: ChatMessage):
    client = get_llm_client()
    system_prompt = (
        f"You are the Digital Career Twin AI Mentor advising a candidate targeting the '{msg.target_role}' role. "
        "Keep advice practical, action-oriented, evidence-grounded, and concise (under 3 paragraphs)."
    )

    try:
        reply = await client.generate(
            prompt=msg.message,
            system_prompt=system_prompt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        provider=settings.LLM_PROVIDER,
        model=settings.GROQ_MODEL if settings.LLM_PROVIDER == "groq" else settings.LLM_MODEL,
        reply=reply,
        suggested_actions=[
            "Prioritize Docker containerization milestone",
            "Review verified skill gaps",
            "Take RIASEC assessment"
        ]
    )
