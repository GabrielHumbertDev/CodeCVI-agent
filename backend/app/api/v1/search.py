"""
Semantic search: find jobs similar to a CV (or CVs similar to a job)
using cosine similarity on nomic-embed-text embeddings.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.cv import CV
from app.models.job import Job
from app.services.embedding_service import embed_text, cosine_similarity, cv_to_embed_text

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class JobSearchResult(BaseModel):
    job_id: uuid.UUID
    title: str
    company: Optional[str]
    similarity: float


class CVSearchResult(BaseModel):
    cv_id: uuid.UUID
    filename: str
    similarity: float


class SemanticJobSearchRequest(BaseModel):
    cv_id: uuid.UUID
    top_k: int = 5


class SemanticCVSearchRequest(BaseModel):
    job_id: uuid.UUID
    top_k: int = 5


# ---------------------------------------------------------------------------
# Embed-on-demand helper
# ---------------------------------------------------------------------------

async def _ensure_cv_embedding(cv: CV, db: Session) -> Optional[list[float]]:
    """Generate and store embedding for a CV if it doesn't have one yet."""
    if cv.embedding:
        return cv.embedding
    if not cv.parsed_data:
        return None
    text = cv_to_embed_text(cv.parsed_data)
    embedding = await embed_text(text)
    if embedding:
        cv.embedding = embedding
        db.commit()
    return embedding


async def _ensure_job_embedding(job: Job, db: Session) -> Optional[list[float]]:
    """Generate and store embedding for a job if it doesn't have one yet."""
    if job.embedding:
        return job.embedding
    embedding = await embed_text(job.description)
    if embedding:
        job.embedding = embedding
        db.commit()
    return embedding


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/jobs-for-cv", response_model=list[JobSearchResult])
async def find_similar_jobs(
    payload: SemanticJobSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Find the most semantically similar jobs to a given CV."""
    cv = db.query(CV).filter(CV.id == payload.cv_id, CV.user_id == current_user.id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if cv.parse_status != "done":
        raise HTTPException(status_code=400, detail="CV must be parsed before searching.")

    cv_embedding = await _ensure_cv_embedding(cv, db)
    if not cv_embedding:
        raise HTTPException(status_code=503, detail="Could not generate CV embedding. Is Ollama running?")

    jobs = db.query(Job).filter(Job.user_id == current_user.id).all()
    if not jobs:
        return []

    results = []
    for job in jobs:
        job_embedding = await _ensure_job_embedding(job, db)
        if not job_embedding:
            continue
        sim = cosine_similarity(cv_embedding, job_embedding)
        results.append(JobSearchResult(
            job_id=job.id,
            title=job.title,
            company=job.company,
            similarity=round(sim, 4),
        ))

    results.sort(key=lambda r: r.similarity, reverse=True)
    return results[: payload.top_k]


@router.post("/cvs-for-job", response_model=list[CVSearchResult])
async def find_similar_cvs(
    payload: SemanticCVSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Find the most semantically similar CVs to a given job."""
    job = db.query(Job).filter(Job.id == payload.job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    job_embedding = await _ensure_job_embedding(job, db)
    if not job_embedding:
        raise HTTPException(status_code=503, detail="Could not generate job embedding. Is Ollama running?")

    cvs = db.query(CV).filter(CV.user_id == current_user.id, CV.parse_status == "done").all()
    if not cvs:
        return []

    results = []
    for cv in cvs:
        cv_embedding = await _ensure_cv_embedding(cv, db)
        if not cv_embedding:
            continue
        sim = cosine_similarity(job_embedding, cv_embedding)
        results.append(CVSearchResult(
            cv_id=cv.id,
            filename=cv.filename,
            similarity=round(sim, 4),
        ))

    results.sort(key=lambda r: r.similarity, reverse=True)
    return results[: payload.top_k]


@router.post("/embed-cv/{cv_id}", status_code=200)
async def embed_cv(
    cv_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger embedding generation for a CV."""
    cv = db.query(CV).filter(CV.id == cv_id, CV.user_id == current_user.id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if cv.parse_status != "done":
        raise HTTPException(status_code=400, detail="CV must be parsed first.")
    embedding = await _ensure_cv_embedding(cv, db)
    if not embedding:
        raise HTTPException(status_code=503, detail="Embedding generation failed.")
    return {"cv_id": cv_id, "embedding_dim": len(embedding), "status": "ok"}


@router.post("/embed-job/{job_id}", status_code=200)
async def embed_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger embedding generation for a job."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    embedding = await _ensure_job_embedding(job, db)
    if not embedding:
        raise HTTPException(status_code=503, detail="Embedding generation failed.")
    return {"job_id": job_id, "embedding_dim": len(embedding), "status": "ok"}
