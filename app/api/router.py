from fastapi import APIRouter

from app.api.jobs import router as jobs_router

router = APIRouter(prefix="/api")
router.include_router(jobs_router)