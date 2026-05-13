# app/api/deps/services.py

from fastapi import Depends

from app.db.session import get_session_factory
from app.services.department import (
    DepartmentService,
)

from app.services.employee import (
    EmployeeService,
)

from app.db.uow import UnitOfWork


def get_uow() -> UnitOfWork:
    return UnitOfWork()


def get_department_service():
    uow = UnitOfWork(get_session_factory())
    return DepartmentService(uow)


def get_employee_service():
    uow = UnitOfWork(get_session_factory())
    return EmployeeService(uow)
