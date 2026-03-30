from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from generator import generate

app = FastAPI(title="CV Platform AI Service", version="0.1.0")


class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = ""


class GenerateResponse(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-service"}


@app.post("/generate", response_model=GenerateResponse)
async def generate_endpoint(payload: GenerateRequest):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    try:
        text = await generate(payload.prompt, payload.system_prompt or "")
        return GenerateResponse(text=text)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
