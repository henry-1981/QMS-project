from fastapi import APIRouter
from app.api.v1 import auth, design_changes, agents

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(design_changes.router, prefix="/design-changes", tags=["design-changes"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
