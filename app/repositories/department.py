from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy import text

from app.models.departments import Department


class DepartmentRepository:
    def __init__(self, session):
        self.session = session

    async def get(self, department_id: int) -> Department:
        return await self.session.get(Department, department_id)

    async def get_department_tree(
        self,
        department_id: int,
        depth: int = 1,
    ):
        query = text(
            """
            WITH RECURSIVE department_tree AS (
            
                SELECT
                    d.id,
                    d.name,
                    d.parent_id,
                    d.created_at,
                    0 AS level
                FROM departments d
                WHERE d.id = :department_id

                UNION ALL

                SELECT
                    child.id,
                    child.name,
                    child.parent_id,
                    child.created_at,
                    dt.level + 1
                FROM departments child
                JOIN department_tree dt
                    ON child.parent_id = dt.id
                WHERE dt.level < :depth
            )

            SELECT *
            FROM department_tree
            ORDER BY level, id
            """
        )

        result = await self.session.execute(
            query,
            {
                "department_id": department_id,
                "depth": depth,
            },
        )

        return result.mappings().all()

    async def get_department_by_name_and_parent_id(
        self, name: str, parent_id: Optional[int]
    ) -> Optional[Department]:

        stmt = select(Department).where(
            Department.name == name,
            Department.parent_id == parent_id,
        )

        result = await self.session.execute(stmt)

        return result.scalars().first()

    async def create(self, name: str, parent_id: Optional[int]) -> Department:
        department = Department(
            name=name,
            parent_id=parent_id,
        )

        self.session.add(department)
        await self.session.flush()

        return department

    async def would_create_cycle(
        self, department_id: int, new_parent_id: Optional[int]
    ) -> bool:

        if new_parent_id is None:
            return False

        query = text(
            """
            WITH RECURSIVE subtree AS (

                SELECT id, parent_id
                FROM departments
                WHERE id = :department_id

                UNION ALL

                SELECT d.id, d.parent_id
                FROM departments d
                JOIN subtree s
                    ON d.parent_id = s.id
            )

            SELECT 1
            FROM subtree
            WHERE id = :new_parent_id
            LIMIT 1
            """
        )

        result = await self.session.execute(
            query,
            {
                "department_id": department_id,
                "new_parent_id": new_parent_id,
            },
        )

        return result.scalar() is not None

    async def get_subtree_ids(
        self,
        department_id: int,
    ) -> list[int]:
        query = text(
            """
            WITH RECURSIVE subtree AS (

                SELECT id
                FROM departments
                WHERE id = :id

                UNION ALL

                SELECT d.id
                FROM departments d
                JOIN subtree s
                    ON d.parent_id = s.id
            )

            SELECT id FROM subtree
            """
        )

        result = await self.session.execute(
            query,
            {"id": department_id},
        )

        return [row[0] for row in result.all()]

    async def get_childrens(self, id: int) -> list[int]:
        stmt = select(Department.id).where(Department.parent_id == id)
        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def delete_by_ids(self, ids: list[int]):
        stmt = delete(Department).where(Department.id.in_(ids))

        await self.session.execute(stmt)

    async def delete_subtree(
        self,
        department_id: int,
    ):
        ids = await self.get_subtree_ids(department_id)

        stmt = delete(Department).where(Department.id.in_(ids))

        await self.session.execute(stmt)

    async def update_department(
        self,
        department,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
    ):
        if name is not None:
            department.name = name

        if parent_id is not None:
            department.parent_id = parent_id

        await self.session.flush()

        return department

    async def update_departments_parent(
        self,
        ids: list[int],
        parent_id: int = None,
    ):

        stmt = (
            update(Department).where(Department.id.in_(ids)).values(parent_id=parent_id)
        )

        await self.session.execute(stmt)
        await self.session.flush()
