from fastapi import FastAPI

from app.api.middlewares.trace_middleware import TraceMiddleware
from app.core.logging_config import setup_logging

from app.api.routes.departments import router as departments_router

from app.exceptions.base import ApiError

from app.exceptions.department import DepartmentValidationError
from app.exceptions.handlers import (
    api_exception_handler,
    department_validation_handler,
    domain_exception_handler,
)


setup_logging()


app = FastAPI(
    title="Organization API",
    description="""
API для управления подразделениями и сотрудниками.
""",
    version="1.0.0",
    contact={
        "name": "Backend Team",
        "email": "backend@example.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_exception_handler(Exception, domain_exception_handler)

app.add_exception_handler(
    DepartmentValidationError,
    department_validation_handler,
)

app.add_exception_handler(
    ApiError,
    api_exception_handler,
)

app.add_middleware(TraceMiddleware)


app.include_router(departments_router)
