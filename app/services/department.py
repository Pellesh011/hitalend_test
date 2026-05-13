from sqlalchemy.util import defaultdict

from app.exceptions.base import ApiError
from app.exceptions.department import DepartmentCycleError, DepartmentNotFoundError
from app.exceptions.employee import EmployeeDepartmentNotFoundError

from typing import Optional

import logging

logger = logging.getLogger(__name__)

class DepartmentService:
    def __init__(self, uow):
        self.uow = uow

    async def create_department(
        self,
        name: str,
        parent_id:Optional[int],
    ):
        async with self.uow as uow:
            if parent_id:
                parent = await uow.departments.get(parent_id)
                if not parent:
                    logger.info("Department not found")
                    raise EmployeeDepartmentNotFoundError()

            department = await uow.departments.create(
                name=name,
                parent_id=parent_id,
            )

            return department

    
    async def get_department_by_name_and_parent_id(
        self,
        name: str,
        parent_id:Optional[int],
    ):
        async with self.uow as uow:
            department = await uow.departments.get_department_by_name_and_parent_id(name, parent_id)
            return department
        
    async def get_department_tree(
        self,
        department_id: int,
        depth: int = 1,
        include_employees: bool = True,
    ):

        depth = min(depth, 5)

        async with self.uow as uow:

            rows = await (
                uow.departments.get_department_tree(
                    department_id=department_id,
                    depth=depth,
                )
            )

            if not rows:
                logger.info("Department not found")
                raise DepartmentNotFoundError()

            nodes = {}
            children_map = defaultdict(list)

            for row in rows:

                node = {
                    "id": row["id"],
                    "name": row["name"],
                    "parent_id": row["parent_id"],
                    "created_at": row["created_at"],
                    "children": [],
                }

                if include_employees:
                    node["employees"] = []

                nodes[row["id"]] = node

                if row["parent_id"]:
                    children_map[
                        row["parent_id"]
                    ].append(node)

            for node_id, node in nodes.items():
                node["children"] = children_map.get(
                    node_id,
                    [],
                )

            root = nodes[department_id]

            if include_employees:

                employees = await (
                    uow.employees.get_by_department_ids(
                        list(nodes.keys())
                    )
                )

                for employee in employees:

                    nodes[
                        employee.department_id
                    ]["employees"].append(
                        {
                            "id": employee.id,
                            "full_name": employee.full_name,
                            "position": employee.position,
                            "hired_at": employee.hired_at,
                            "created_at": employee.created_at,
                        }
                    )

            return root
        

    async def update_department(
        self,
        department_id: int,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
    ):
        async with self.uow as uow:

            department = await uow.departments.get(department_id)

            if not department:
                logger.info("Department not found")
                raise DepartmentNotFoundError()


            if parent_id is not None:

                if parent_id == department_id:
                    logger.info("Cannot set parent to itself")
                    raise DepartmentCycleError(
                        "Cannot set parent to itself"
                    )


                if await uow.departments.would_create_cycle(
                    department_id=department_id,
                    new_parent_id=parent_id,
                ):
                    raise DepartmentCycleError(
                        "Move would create cycle"
                    )


            updated = await uow.departments.update_department(
                department=department,
                name=name,
                parent_id=parent_id,
            )

            return updated

    async def delete_department(
        self,
        department_id: int,
        mode: str,
        reassign_to_department_id: Optional[int]
    ):
        async with self.uow as uow:

            department = await uow.departments.get(
                department_id
            )

            if not department:
                raise DepartmentNotFoundError()

            if mode == "reassign":

                if not reassign_to_department_id:
                    raise ApiError(
                        "reassign_to_department_id is required"
                    )

                if reassign_to_department_id == department_id:
                    raise ApiError(
                        "Cannot reassign to same department"
                    )

                if await uow.departments.would_create_cycle(
                    department_id=department_id,
                    new_parent_id=reassign_to_department_id,
                ):
                    raise DepartmentCycleError()

                await uow.employees.reassign_department(
                    from_department_id=department_id,
                    to_department_id=reassign_to_department_id,
                )
                children_ids = await uow.departments.get_childrens(id=department_id)

                await uow.departments.update_departments_parent(
                    ids=children_ids,
                    parent_id=reassign_to_department_id
                )

                await uow.departments.delete_by_ids(
                    ids=[department_id]
                )
                
            elif mode == "cascade":
                subtree_ids = await (
                    uow.departments.get_subtree_ids(
                        department_id
                    )
                )

                await uow.employees.delete_by_department_ids(
                    subtree_ids
                )

                await uow.departments.delete_by_ids(
                    subtree_ids
                )

            else:
                raise ApiError("Invalid mode")

            return None