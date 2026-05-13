class DomainError(Exception):
    """Base domain exception."""


class ApiError(DomainError):
    status_code = 400
    detail = "API Error"
