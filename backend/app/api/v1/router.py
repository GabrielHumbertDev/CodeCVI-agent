from fastapi import APIRouter
from app.api.v1 import health, auth, cvs

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cvs.router, prefix="/cvs", tags=["cvs"])
