from starlette import status

from app.exceptions.base import ApiError


class DepartmentNotFoundError(ApiError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Department not found"


class DepartmentAlreadyExistsError(ApiError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Department already exists " "within the same parent"


class DepartmentCycleError(ApiError):
    status_code = 409
    detail = "Cannot move department " "inside its subtree"


class DepartmentValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
