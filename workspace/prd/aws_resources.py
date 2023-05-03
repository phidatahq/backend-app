from os import getenv

from phidata.app.fastapi import FastApiServer
from phidata.app.streamlit import StreamlitApp
from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import (
    AwsResourceGroup,
    DbInstance,
    DbSubnetGroup,
    EcsCluster,
    S3Bucket,
)

from workspace.prd.docker_resources import prd_image
from workspace.settings import ws_settings

#
# -*- AWS Resources for the prd environment
#

# -*- Settings
launch_type = "FARGATE"
api_key = f"{ws_settings.prd_key}-api"
app_key = f"{ws_settings.prd_key}-app"
# Skip resource creation when running `phi ws up`
skip_create: bool = False
# Skip resource  deletion when running `phi ws down`
skip_delete: bool = False

# -*- S3 bucket for prd data
prd_data_s3_bucket = S3Bucket(
    name=f"{ws_settings.prd_key}-data",
    acl="private",
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- RDS Database Subnet Group
prd_db_subnet_group = DbSubnetGroup(
    name=f"{ws_settings.prd_key}-db-sg",
    enabled=ws_settings.prd_postgres_enabled,
    subnet_ids=ws_settings.subnet_ids,
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- Database Instance
db_engine = "mysql"
prd_db = DbInstance(
    name=f"{ws_settings.prd_key}-db",
    engine=db_engine,
    enabled=ws_settings.prd_mysql_enabled,
    engine_version="8.0.32",
    allocated_storage=100,
    # NOTE: For production, use a larger instance type.
    # Last checked price: $0.152 per hour = ~$110 per month
    db_instance_class="db.m6g.large",
    availability_zone=ws_settings.aws_az1,
    db_subnet_group=prd_db_subnet_group,
    enable_performance_insights=True,
    # vpc_security_group_ids=ws_settings.security_groups,
    secrets_file=ws_settings.ws_root.joinpath(
        "workspace/secrets/prd_mysql_secrets.yml"
    ),
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- ECS cluster for running services
prd_ecs_cluster = EcsCluster(
    name=f"{ws_settings.prd_key}-cluster",
    ecs_cluster_name=ws_settings.prd_key,
    capacity_providers=[launch_type],
)

# container_env = {
#     "BUILD_ENV": "prd",
#     # Database configuration
#     "DB_HOST": prd_db.get_db_host(),
#     "DB_PORT": prd_db.get_db_port(),
#     "DB_USER": prd_db.get_master_username(),
#     "DB_PASS": prd_db.get_master_user_password(),
#     "DB_SCHEMA": prd_db.get_db_name(),
#     # Upgrade database on startup
#     "UPGRADE_DB": True,
#     # Wait for database and redis to be ready
#     "WAIT_FOR_DB": True,
#     # Get the OpenAI API key from the environment if available
#     "OPENAI_API_KEY": getenv("OPENAI_API_KEY", ""),
# }

# -*- StreamlitApp running on ECS
prd_streamlit = StreamlitApp(
    name=app_key,
    enabled=ws_settings.prd_app_enabled,
    image=prd_image,
    command=["app", "start", "Home"],
    ecs_task_cpu="512",
    ecs_task_memory="1024",
    ecs_cluster=prd_ecs_cluster,
    aws_subnets=ws_settings.subnet_ids,
    # aws_security_groups=ws_settings.security_groups,
    # Get the OpenAI API key from the environment if available
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from a file
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/app_secrets.yml"),
)

# -*- FastApiServer running on ECS
prd_fastapi = FastApiServer(
    name=api_key,
    enabled=ws_settings.prd_api_enabled,
    image=prd_image,
    command=["api", "start"],
    ecs_task_cpu="512",
    ecs_task_memory="1024",
    ecs_cluster=prd_ecs_cluster,
    aws_subnets=ws_settings.subnet_ids,
    # aws_security_groups=ws_settings.security_groups,
    # Get the OpenAI API key from the environment if available
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from a file
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/api_secrets.yml"),
)

#
# -*- AwsConfig defining the prd resources
#
prd_aws_config = AwsConfig(
    env=ws_settings.prd_env,
    apps=[prd_streamlit, prd_fastapi],
    resources=AwsResourceGroup(
        db_subnet_groups=[prd_db_subnet_group],
        db_instances=[prd_db],
        s3_buckets=[prd_data_s3_bucket],
    ),
)
