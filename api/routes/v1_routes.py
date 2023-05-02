from fastapi import APIRouter

from api.routes.health_checks import health_checks_router
from api.routes.train_jobs import train_jobs_router
from api.routes.run_jobs import run_jobs_router
from api.routes.job_status import job_status_router


v1_router = APIRouter(prefix="/v1")
v1_router.include_router(health_checks_router)
v1_router.include_router(train_jobs_router)
v1_router.include_router(run_jobs_router)
v1_router.include_router(job_status_router)
