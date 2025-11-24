from fastapi import APIRouter
from app.api.v1.endpoints import experiments, health

api_router = APIRouter()

api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

