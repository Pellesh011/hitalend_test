from fastapi import APIRouter, Depends, Path, Query
from starlette import status
from app.api.deps.services import get_department_service, get_employee_service
from app.api.schemas.departments import (
    DepartmentCreateSchema,
    DepartmentDeleteSchema,
    DepartmentResponseSchema,
    DepartmentTreeSchema,
    DepartmentUpdateSchema,
)
from app.api.schemas.employees import EmployeeCreateSchema, EmployeeResponseSchema
from app.api.schemas.error import ErrorResponseSchema
from app.exceptions.department import DepartmentAlreadyExistsError
from app.services.department import DepartmentService
from app.services.employee import EmployeeService

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "/",
    response_model=DepartmentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "model": ErrorResponseSchema,
            "description": "Department already exists",
        },
    },
)
async def create_department_endpoint(
    payload: DepartmentCreateSchema,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponseSchema:
    department = await service.get_department_by_name_and_parent_id(
        payload.name, payload.parent_id
    )
    if department:
        raise DepartmentAlreadyExistsError()

    department = await service.create_department(
        name=payload.name,
        parent_id=payload.parent_id,
    )
    return DepartmentResponseSchema.model_validate(department)


@router.delete(
    "/{department_id}",
    status_code=204,
    summary="Delete department",
    description=("Delete department with cascade or reassign mode"),
)
async def delete_department(
    department_id: int = Path(
        ...,
        description="Department ID",
    ),
    payload: DepartmentDeleteSchema = Depends(),
    service: DepartmentService = Depends(
        get_department_service,
    ),
):
    await service.delete_department(
        department_id=department_id,
        mode=payload.mode,
        reassign_to_department_id=payload.reassign_to_department_id,
    )

    return None


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponseSchema,
)
async def update_department(
    department_id: int,
    payload: DepartmentUpdateSchema,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponseSchema:
    department = await service.update_department(
        department_id=department_id,
        **payload.model_dump(exclude_unset=True),
    )
    return DepartmentResponseSchema.model_validate(department)


@router.post(
    "/{department_id}/employees/",
    response_model=EmployeeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create employee",
    description="""
Создаёт сотрудника в подразделении.
""",
    responses={
        404: {
            "model": ErrorResponseSchema,
            "description": "Department not found",
        },
    },
)
async def create_employee_endpoint(
    department_id: int,
    payload: EmployeeCreateSchema,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponseSchema:

    employee = await service.create_employee(
        department_id=department_id,
        full_name=payload.full_name,
        position=payload.position,
        hired_at=payload.hired_at,
    )

    return EmployeeResponseSchema.model_validate(employee)


@router.get(
    "/{department_id}",
    response_model=DepartmentTreeSchema,
)
async def get_department(
    department_id: int,
    depth: int = 1,
    include_employees: bool = True,
    service: DepartmentService = Depends(get_department_service),
):
    department = await service.get_department_tree(
        department_id=department_id,
        depth=depth,
        include_employees=include_employees,
    )

    return DepartmentTreeSchema.model_validate(department)
