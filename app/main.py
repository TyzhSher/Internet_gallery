"""Точка входа FastAPI приложения Internet Gallery."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.config import settings
from app.database import Base, engine
from app.exceptions import (
    http_exception_handler,
    pydantic_validation_handler,
    validation_exception_handler,
)
from app.middleware.rate_limiter import rate_limit_middleware
from app.routers import (
    analytics,
    catalog,
    export,
    favorites,
    paintings,
    recommendations,
    users,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):  # pylint: disable=unused-argument
    """Lifecycle manager: инициализация БД при старте."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name, 
    version="2.0.0", 
    lifespan=lifespan, 
    docs_url="/api/docs"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(rate_limit_middleware)

# Exception handlers
app.add_exception_handler(
    RequestValidationError, 
    validation_exception_handler
)
app.add_exception_handler(
    ValidationError, 
    pydantic_validation_handler
)
app.add_exception_handler(
    HTTPException, 
    http_exception_handler
)

# Routers
app.include_router(users.router)
app.include_router(paintings.router)
app.include_router(favorites.router)
app.include_router(catalog.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(export.router)


@app.get("/api/health")
def health_check() -> dict:
    """Endpoint для проверки работоспособности сервиса."""
    return {"status": "healthy", "version": app.version}


@app.get("/")
def root() -> dict:
    """Корневой эндпоинт с информацией об API."""
    return {
        "message": "Internet Gallery API v2", 
        "docs": "/api/docs"
    }