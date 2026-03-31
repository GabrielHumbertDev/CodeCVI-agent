"""
Embedding service: generates vector embeddings via Ollama nomic-embed-text.
Stores as plain float lists (JSONB) — swappable to pgvector later.
"""
import httpx
import numpy as np
from typing import Optional
from app.core.config import get_settings

settings = get_settings()
TIMEOUT = 30.0


async def embed_text(text: str) -> Optional[list[float]]:
    """
    Call Ollama /api/embeddings and return a float list.
    Returns None if embedding fails (non-fatal — CV/job still saved).
    """
    if not text or not text.strip():
        return None
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{settings.ollama_url}/api/embeddings",
                json={"model": settings.embedding_model, "prompt": text[:4000]},
            )
            response.raise_for_status()
            return response.json()["embedding"]
    except Exception:
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two float lists."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def cv_to_embed_text(parsed_data: dict) -> str:
    """Build a single text blob from parsed CV data for embedding."""
    parts = [
        parsed_data.get("name", ""),
        parsed_data.get("summary", "") or "",
        " ".join(parsed_data.get("skills", [])),
    ]
    for exp in parsed_data.get("experience", []):
        parts.append(exp.get("title", ""))
        parts.append(exp.get("description", "") or "")
    for edu in parsed_data.get("education", []):
        parts.append(edu.get("degree", ""))
    parts.append(parsed_data.get("raw_text", "") or "")
    return " ".join(p for p in parts if p).strip()
