from os import getenv

from phidata.app.redis import Redis
from phidata.app.mysql import MySQLDb
from phidata.app.fastapi import FastApiServer
from phidata.app.streamlit import StreamlitApp
from phidata.docker.config import DockerConfig
from phidata.docker.resource.image import DockerImage

from workspace.dev.jupyter.lab import dev_jupyter_lab
from workspace.settings import ws_settings

#
# -*- Docker resources for the dev environment
#

# -*- MySQL database
dev_db = MySQLDb(
    name=f"{ws_settings.ws_name}-db",
    enabled=ws_settings.dev_mysql_enabled,
    mysql_database="dev",
    mysql_root_password=ws_settings.ws_name,
    # Connect to this db on port 9315
    container_host_port=9315,
)

# -*- Redis cache
dev_redis = Redis(
    name=f"{ws_settings.ws_name}-redis",
    enabled=ws_settings.dev_redis_enabled,
    redis_password=ws_settings.ws_name,
    command=["redis-server", "--save", "60", "1"],
    container_host_port=9316,
)

# -*- Dev Image
dev_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    # platform="linux/amd64",
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
    use_cache=ws_settings.use_cache,
)

container_env = {
    "RUNTIME_ENV": "dev",
    # Database configuration
    "DB_HOST": dev_db.get_db_host_docker(),
    "DB_PORT": dev_db.get_db_port_docker(),
    "DB_USER": dev_db.get_db_user(),
    "DB_PASS": dev_db.get_db_password(),
    "DB_SCHEMA": dev_db.get_db_schema(),
    # Redis configuration
    "REDIS_HOST": dev_redis.get_db_host_docker(),
    "REDIS_PORT": dev_redis.get_db_port_docker(),
    "REDIS_SCHEMA": 1,
    # Upgrade database on startup
    "UPGRADE_DB": True,
    # Wait for database and redis to be ready
    "WAIT_FOR_DB": True,
    "WAIT_FOR_REDIS": True,
    # Get the OpenAI API key from the environment if available
    "OPENAI_API_KEY": getenv("OPENAI_API_KEY", ""),
}

# -*- FastApiServer running on port 9090
dev_fastapi = FastApiServer(
    name=f"{ws_settings.ws_name}-api",
    enabled=ws_settings.dev_api_enabled,
    image=dev_image,
    command="api start -r",
    env=container_env,
    mount_workspace=True,
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/api_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/api_secrets.yml"),
)

# -*- StreamlitApp running on port 9095
dev_streamlit = StreamlitApp(
    name=f"{ws_settings.ws_name}-app",
    enabled=ws_settings.dev_app_enabled,
    image=dev_image,
    command="app start Home",
    env=container_env,
    mount_workspace=True,
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/app_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/app_secrets.yml"),
)

# -*- DockerConfig defining the dev resources
dev_docker_config = DockerConfig(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    apps=[dev_db, dev_redis, dev_streamlit, dev_fastapi, dev_jupyter_lab],
)
