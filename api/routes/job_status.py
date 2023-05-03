from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.endpoints import endpoints
from utils.log import logger

######################################################
## Router for Running Jobs
######################################################

job_status_router = APIRouter(prefix=endpoints.STATUS, tags=["Job Status"])


# -*- Pydantic models for request and response
class JobStatusRequest(BaseModel):
    job_name: str


class JobStatusResponse(BaseModel):
    job_status: str


@job_status_router.post("/job")
def job_status(job_status_request: JobStatusRequest):
    logger.info(f"Checking status for {job_status_request.job_name}")
    try:
        # TODO: Get job status
        return JobStatusResponse(job_status="success")
    except Exception as e:
        logger.error(f"Failed to get status for {job_status_request.job_name}: {e}")
        return JobStatusResponse(job_status="failed")
