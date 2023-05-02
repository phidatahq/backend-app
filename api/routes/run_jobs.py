from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.endpoints import endpoints
from api.utils.log import logger

######################################################
## Router for Running Jobs
######################################################

run_jobs_router = APIRouter(prefix=endpoints.RUN, tags=["Run Jobs"])


# -*- Pydantic models for request and response
class RunJobRequest(BaseModel):
    job_name: str = "test"


class RunJobResponse(BaseModel):
    job_status: str = "failed"


@run_jobs_router.post("/job")
def run_job(run_job_request: RunJobRequest):
    logger.info(f"Received request to run {run_job_request.job_name}")
    try:
        logger.info(f"Running {run_job_request.job_name}")
        # TODO: Run job
        logger.info(f"Run {run_job_request.job_name} complete")
        return RunJobResponse(job_status="success")
    except Exception as e:
        logger.error(f"Run {run_job_request.job_name} failed: {e}")
        return RunJobResponse(job_status="failed")
