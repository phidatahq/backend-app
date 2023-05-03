from typing import Tuple

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from api.settings import api_settings
from api.routes.v1_routes import v1_router
from api.utils.log import logger


def create_app() -> Tuple[FastAPI, Session, Engine]:
    """Create a FastAPI App

    Returns:
        FastAPI: FastAPI App
        Session: SQLAlchemy Session
        Engine: SQLAlchemy Engine
    """

    # Create FastAPI App
    app: FastAPI = FastAPI(
        title=api_settings.title,
        version=api_settings.version,
        docs_url="/docs" if api_settings.docs_enabled else None,
        redoc_url="/redoc" if api_settings.docs_enabled else None,
        openapi_url="/openapi.json" if api_settings.docs_enabled else None,
    )

    # Add v1 router
    app.include_router(v1_router)

    # Create SQLAlchemy Engine
    sqlalchemy_engine: Engine
    db_uri = api_settings.get_db_uri()
    sqlalchemy_engine = create_engine(db_uri, pool_pre_ping=True)

    # Create 2 types of database sessions:
    # 1. db_session: used for background tasks
    # 2. request_db_session: used for each request
    # db_session is a scoped session which means it is created on app startup (i.e. when it is first accessed)
    # This is used by background tasks and long-running processes
    db_session: Session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=sqlalchemy_engine)
    )  # type: ignore
    # request_db_session is a session created for each request
    # This is added to the request state so that it can be accessed by the request handler
    request_db_session: Session = sessionmaker(
        autocommit=False, autoflush=False, bind=sqlalchemy_engine
    )  # type: ignore

    # Add Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add Middleware Functions
    # A middleware is a function that is always executed for each request,
    # and handles the code executed before and after the request.
    # We need to have an independent database session/connection (SessionLocal) per request,
    # use the same session through the request and then close it after the request is finished.
    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        response = Response(
            "Internal server error", status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )

        try:
            request.state.db = request_db_session()
            response = await call_next(request)
        finally:
            request.state.db.close()
        # logger.debug(f"Final Response Headers: {response.headers}")
        return response

    if api_settings.runtime_env == "dev":
        logger.debug(f"ApiSettings: {api_settings.json(indent=2)}")

    return app, db_session, sqlalchemy_engine


# Create FastAPI App
app, db_session, sqlalchemy_engine = create_app()
