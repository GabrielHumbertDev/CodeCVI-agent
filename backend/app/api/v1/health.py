from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services.ai_client import call_ai

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "cv-platform-backend",
    }


@router.get("/health/ai")
async def ai_health_check():
    try:
        text = await call_ai("Say OK in one word.", "You are a helpful assistant.")
        return {"status": "ok", "ai_response": text}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
