from fastapi import APIRouter
from app.routers import (
    auth, profile, skills, assessments, scores, careers,
    roadmap, simulator, market, mentor, ingest, admin
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(skills.router)
api_router.include_router(assessments.router)
api_router.include_router(scores.router)
api_router.include_router(careers.router)
api_router.include_router(roadmap.router)
api_router.include_router(simulator.router)
api_router.include_router(market.router)
api_router.include_router(mentor.router)
api_router.include_router(ingest.router)
api_router.include_router(admin.router)
