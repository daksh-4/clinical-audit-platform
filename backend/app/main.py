"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.db.session import engine
from app.db.base import Base
from app.core.logging import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    """
    # Startup
    setup_logging()
    # Create database tables (in production, use Alembic migrations)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Clinical Audit Platform - Open infrastructure for clinician-led audits",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

logger = get_logger(__name__)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    errors = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", []) if p is not None)
        errors.append(
            {
                "loc": loc,
                "msg": err.get("msg"),
                "type": err.get("type"),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
            "request_id": request_id,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", None)
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": detail,
            "request_id": request_id,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    request_id = getattr(request.state, "request_id", None)
    logger.exception(
        "Database error",
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error",
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers.
    Checks database and Redis connectivity.
    """
    from sqlalchemy import text
    from app.db.session import AsyncSessionLocal
    import redis.asyncio as aioredis
    
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "checks": {}
    }
    
    # Check database
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client = aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        await redis_client.close()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Clinical Audit Platform API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }
