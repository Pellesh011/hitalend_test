# app/repositories/employee.py

from datetime import date
from typing import Optional

from sqlalchemy import delete, select, update

from app.models.employees import Employee


class EmployeeRepository:
    def __init__(self, session):
        self.session = session

    async def create(
        self,
        department_id: int,
        full_name: str,
        position: str,
        hired_at: Optional[date],
    ) -> Employee:

        employee = Employee(
            department_id=department_id,
            full_name=full_name,
            position=position,
            hired_at=hired_at,
        )

        self.session.add(employee)

        await self.session.flush()

        return employee
    
    async def get_by_department_ids(
        self,
        department_ids: list[int],
    ):

        stmt = (
            select(Employee)
            .where(
                Employee.department_id.in_(
                    department_ids
                )
            )
            .order_by(Employee.full_name)
        )

        result = await self.session.execute(
            stmt
        )

        return result.scalars().all()
    
    async def reassign_department(
        self,
        from_department_id: int,
        to_department_id: int,
    ):
        stmt = (
            update(Employee)
            .where(
                Employee.department_id
                == from_department_id
            )
            .values(
                department_id=to_department_id
            )
        )

        await self.session.execute(stmt)

    async def reassign_departments(
        self,
        from_department_ids: int,
        to_department_id: int,
    ):
        stmt = (
            update(Employee)
            .where(
                Employee.department_id.in_(from_department_ids)
            )
            .values(
                department_id=to_department_id
            )
        )

        await self.session.execute(stmt)

    async def delete_by_department_ids(
        self,
        department_ids: list[int],
    ):
        stmt = delete(Employee).where(
            Employee.department_id.in_(
                department_ids
            )
        )

        await self.session.execute(stmt)