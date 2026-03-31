from fastapi import APIRouter
from app.api.v1 import health, auth, cvs, jobs, match, tailor, cover_letters, applications

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cvs.router, prefix="/cvs", tags=["cvs"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(match.router, prefix="/match", tags=["match"])
api_router.include_router(tailor.router, prefix="/tailor", tags=["tailor"])
api_router.include_router(cover_letters.router, prefix="/cover-letters", tags=["cover-letters"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
