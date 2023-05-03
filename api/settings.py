from typing import List, Optional

from pydantic import BaseSettings, validator

from utils.log import logger


class ApiSettings(BaseSettings):
    """Api settings that can be derived using environment variables.

    Reference: https://pydantic-docs.helpmanual.io/usage/settings/
    """

    # Api title and version
    title: str = "Api"
    version: str = "1.0"

    # Runtime env derived using the `runtime_env` environment variable.
    # Valid values are "dev", "stg", "prd"
    runtime_env: str = "dev"

    # Set to False to disable docs server at /docs and /redoc
    docs_enabled: bool = True

    # Host and port to run the api server on.
    host: str = "0.0.0.0"
    port: int = 9090

    # Database configuration
    db_host: Optional[str]
    db_port: Optional[str]
    db_user: Optional[str]
    db_pass: Optional[str]
    db_schema: Optional[str]
    db_driver: str = "mysql+mysqlconnector"

    # Redis configuration
    redis_host: Optional[str]
    redis_port: Optional[str]
    redis_pass: Optional[str]
    redis_schema: Optional[str]
    redis_driver: str = "redis"

    # API Keys
    openai_api_key: Optional[str]

    # Cors origin list to allow requests from.
    # This list is set using the set_cors_origin_list validator
    # which uses the runtime_env variable to set the
    # default cors origin list.
    cors_origin_list: Optional[List[str]] = None

    def get_db_uri(self) -> str:
        uri = "{}://{}{}@{}:{}/{}".format(
            self.db_driver,
            self.db_user,
            f":{self.db_pass}" if self.db_pass else "",
            self.db_host,
            self.db_port,
            self.db_schema,
        )
        if "None" in uri:
            logger.warning("No database provided, using in-memory sqlite")
            return "sqlite://"
        return uri

    def get_redis_uri(self) -> Optional[str]:
        uri = "{}://{}@{}:{}/{}".format(
            self.redis_driver,
            f":{self.redis_pass}" if self.redis_pass else "",
            self.redis_host,
            self.redis_port,
            self.redis_schema,
        )
        if "None" in uri:
            return None
        return uri

    @validator("runtime_env")
    def validate_runtime_env(cls, runtime_env):
        valid_runtime_envs = ["dev", "stg", "prd"]
        if runtime_env not in valid_runtime_envs:
            raise ValueError(f"Invalid runtime_env: {runtime_env}")
        return runtime_env

    @validator("cors_origin_list", always=True)
    def set_cors_origin_list(cls, cors_origin_list, values):
        valid_cors = cors_origin_list or []

        runtime_env = values.get("runtime_env")
        if runtime_env == "dev":
            # 9095 is the default port for streamlit
            # 3000 is the default port for create-react-app
            valid_cors.extend(["http://localhost:9095", "http://localhost:3000"])

        return valid_cors


# Create ApiSettings object
api_settings = ApiSettings()
