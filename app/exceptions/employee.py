# app/exceptions/employee.py

from starlette import status

from app.exceptions.base import ApiError


class EmployeeDepartmentNotFoundError(ApiError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Department not found"
