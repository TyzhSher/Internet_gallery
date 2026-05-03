"""Обработчики исключений для единого формата ошибок API."""
from fastapi import Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    """Обработчик HTTPException с единым форматом ответа."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": getattr(exc, "code", "HTTP_ERROR"),
                "message": exc.detail,
                "path": request.url.path,
            }
        }
    )


async def validation_exception_handler(
    request: Request,  # pylint: disable=unused-argument
    exc: RequestValidationError
) -> JSONResponse:
    """
    Обработчик ошибок валидации запросов.
    
    Возвращает формат:
    {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "errors": [...]
        }
    }
    """
    errors = []
    for error in exc.errors():
        loc_parts = [
            str(loc) for loc in error["loc"] 
            if loc not in ("__root__", "body")
        ]
        field = ".".join(loc_parts) if loc_parts else "body"
        
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "errors": errors,
            }
        }
    )


async def pydantic_validation_handler(
    request: Request,  # pylint: disable=unused-argument
    exc: ValidationError
) -> JSONResponse:
    """Обработчик внутренних ошибок валидации Pydantic."""
    errors = [
        {
            "field": ".".join(map(str, e["loc"])), 
            "message": e["msg"], 
            "type": e["type"]
        } 
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR", 
                "message": "Validation failed", 
                "errors": errors,
            }
        }
    )