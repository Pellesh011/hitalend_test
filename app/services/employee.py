# app/services/employee.py

from datetime import date
from typing import Optional

from app.exceptions.employee import (
    EmployeeDepartmentNotFoundError,
)

from app.models.employees import Employee
from app.db.uow import UnitOfWork


class EmployeeService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_employee(
        self,
        department_id: int,
        full_name: str,
        position: str,
        hired_at: Optional[date],
    ) -> Employee:

        async with self.uow as uow:

            department = await uow.departments.get(
                department_id
            )

            if not department:
                raise (
                    EmployeeDepartmentNotFoundError()
                )

            employee = await uow.employees.create(
                department_id=department_id,
                full_name=full_name,
                position=position,
                hired_at=hired_at,
            )

            return employee