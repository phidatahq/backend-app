import datetime
from typing import Optional

from sqlalchemy.schema import Column
from sqlalchemy.types import BigInteger, DateTime, String, Text

from db.tables import BaseTable
from utils.dttm import current_utc


class JobRuns(BaseTable):
    """
    Table for storing job runs.
    """

    __tablename__ = "job_runs"

    id_job_run = Column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False, index=True
    )
    job_name = Column(Text, nullable=False)
    status = Column(String(128), nullable=False, index=True)
    start_ts = Column(DateTime(timezone=True), default=current_utc)
    update_ts = Column(DateTime(timezone=True), default=current_utc)
    end_ts = Column(DateTime)

    def __init__(
        self,
        job_name: str,
        status: Optional[str] = None,
        start_ts: Optional[datetime.datetime] = current_utc(),
    ):
        self.job_name = job_name
        self.status = status
        self.start_ts = start_ts
