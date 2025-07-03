from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import time
import logging


from app.api.routers import api_router
from app.core.config import settings
from app.metrics.base import metrics_router
from app.metrics.http_metrics import HTTPMetrics
from app.middlewares.metrics_middleware import MetricsMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up application...")
    # await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application...")


def get_application() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="FastAPI application with PostgreSQL and SQLAlchemy",
        version="1.0.0",
        openapi_url="/api/openapi.json" if settings.ENVIRONMENT != "production" else None,
        docs_url="/api/docs/" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/api/redoc/" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan
    )

    # # Security middleware
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=settings.ALLOWED_CORS_ORIGINS
    # )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        return response

    # Add metrics middleware
    if settings.metrics_enabled:
        http_metrics = HTTPMetrics()
        app.add_middleware(MetricsMiddleware, http_metrics=http_metrics)

    # Include API routers with versioning
    app.include_router(api_router, prefix="/api")
    app.include_router(metrics_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}

    return app
