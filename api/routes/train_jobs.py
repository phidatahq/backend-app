from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.endpoints import endpoints
from api.utils.log import logger

######################################################
## Router for Training Jobs
######################################################

train_jobs_router = APIRouter(prefix=endpoints.TRAIN, tags=["Train Jobs"])


# -*- Pydantic models for request and response
class TrainJobRequest(BaseModel):
    job_name: str = "test"


class TrainJobResponse(BaseModel):
    job_status: str = "failed"


@train_jobs_router.post("/job")
def train_job(train_job_request: TrainJobRequest):
    logger.info(f"Received request to train {train_job_request.job_name}")
    try:
        logger.info(f"Training {train_job_request.job_name}")
        # TODO: Train job
        logger.info(f"Training {train_job_request.job_name} complete")
        return TrainJobResponse(job_status="success")
    except Exception as e:
        logger.error(f"Training {train_job_request.job_name} failed: {e}")
        return TrainJobResponse(job_status="failed")
