import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse


from app.exceptions.base import ApiError
from app.exceptions.department import DepartmentValidationError


logger = logging.getLogger("app")


async def domain_exception_handler(request: Request, exc: Exception):
    tb = traceback.extract_tb(exc.__traceback__)

    last_frame = tb[-1] if tb else None

    logger.error(
        {
            "event": "exception",
            "type": exc.__class__.__name__,
            "message": str(exc),
            "file": last_frame.filename if last_frame else None,
            "function": last_frame.name if last_frame else None,
        }
    )

    return JSONResponse(
        status_code=getattr(exc, "status_code", 500),
        content={"detail": str(exc)},
    )


async def api_exception_handler(
    request: Request,
    exc: ApiError,
):
    tb = traceback.extract_tb(exc.__traceback__)

    last_frame = tb[-1] if tb else None

    logger.error(
        {
            "event": "exception",
            "type": exc.__class__.__name__,
            "message": exc.detail,
            "file": last_frame.filename if last_frame else None,
            "function": last_frame.name if last_frame else None,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
    )


async def department_validation_handler(
    request: Request,
    exc: DepartmentValidationError,
):
    return JSONResponse(
        status_code=409,
        content={
            "error": "department_validation_error",
            "message": exc.message,
        },
    )
