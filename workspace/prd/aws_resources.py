from os import getenv

from phidata.app.fastapi import FastApiServer
from phidata.app.streamlit import StreamlitApp
from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import (
    AwsResourceGroup,
    CacheCluster,
    CacheSubnetGroup,
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
    subnet_ids=ws_settings.private_subnets,
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- Elasticache Subnet Group
prd_redis_subnet_group = CacheSubnetGroup(
    name=f"{ws_settings.prd_key}-cache-sg",
    enabled=ws_settings.prd_redis_enabled,
    subnet_ids=ws_settings.private_subnets,
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- Backend database instance #1
db_engine = "postgres"
prd_db_instance = DbInstance(
    name=f"{ws_settings.prd_key}-db-a",
    engine=db_engine,
    enabled=ws_settings.prd_postgres_enabled,
    engine_version="14.5",
    allocated_storage=100,
    # NOTE: For production, use a larger instance type.
    # Last checked price: $0.152 per hour = ~$110 per month
    db_instance_class="db.m6g.large",
    availability_zone=ws_settings.aws_az1,
    db_subnet_group=prd_db_subnet_group,
    enable_performance_insights=True,
    vpc_security_group_ids=ws_settings.security_groups,
    secrets_file=ws_settings.ws_dir.joinpath("secrets/prd_postgres_secrets.yml"),
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- Redis cache
prd_redis_cluster = CacheCluster(
    name=f"{ws_settings.prd_key}-cache",
    engine="redis",
    enabled=ws_settings.prd_redis_enabled,
    num_cache_nodes=1,
    # NOTE: For production, use a larger instance type.
    # Last checked price: $0.068 per hour = ~$50 per month
    cache_node_type="cache.m6g.large",
    security_group_ids=ws_settings.security_groups,
    cache_subnet_group=prd_redis_subnet_group,
    preferred_availability_zone=ws_settings.aws_az1,
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
#     "DB_HOST": prd_db_instance.get_db_host(),
#     "DB_PORT": prd_db_instance.get_db_port(),
#     "DB_USER": prd_db_instance.get_master_username(),
#     "DB_PASS": prd_db_instance.get_master_user_password(),
#     "DB_SCHEMA": prd_db_instance.get_db_name(),
#     # Redis configuration
#     "REDIS_HOST": prd_redis_cluster.get_db_host(),
#     "REDIS_PORT": prd_redis_cluster.get_db_port(),
#     "REDIS_SCHEMA": 1,
#     # Celery configuration
#     "CELERY_REDIS_DB": 2,
#     # Upgrade database on startup
#     "UPGRADE_DB": True,
#     # Wait for database and redis to be ready
#     "WAIT_FOR_DB": True,
#     "WAIT_FOR_REDIS": True,
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
        s3_buckets=[prd_data_s3_bucket],
    ),
)
