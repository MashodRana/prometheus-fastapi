import uvicorn
from app.core.config import settings




if __name__ == "__main__":
    """Entrypoint of the application."""
    uvicorn.run(
        "app.core.main:get_application",
        workers=settings.WORKERS_COUNT,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        factory=True,
    )
