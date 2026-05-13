
import pytest

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import app  # лучше импортировать реальный app
from app.core.config import get_settings
from app.api.deps.services import get_department_service, get_employee_service
from app.api.routes.departments import router as departments_router


class FakeSettings:
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    

@pytest.fixture
def app_fixture():
    app.dependency_overrides[get_settings] = lambda: FakeSettings()
    return app

@pytest.fixture
async def client(app_fixture):
    transport = ASGITransport(app=app_fixture)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def override_dependencies(app_fixture):
    dept_service = FakeDepartmentService()
    emp_service = FakeEmployeeService()

    app_fixture.dependency_overrides[get_department_service] = lambda: dept_service
    app_fixture.dependency_overrides[get_employee_service] = lambda: emp_service

    return dept_service, emp_service


class FakeDepartmentService:
    def __init__(self):
        self.storage = {}

    async def get_department_by_name_and_parent_id(self, name, parent_id):
        return None

    async def create_department(self, name, parent_id):
        return {"id": 1, "name": name, "parent_id": parent_id, "created_at":"2026-05-12T12:00:00Z"}

    async def delete_department(self, department_id, mode, reassign_to_department_id):
        return None

    async def update_department(self, department_id, **kwargs):
        return {"id": department_id, "parent_id": None,  "created_at":"2026-05-12T12:00:00Z", **kwargs}

    async def get_department_tree(self, department_id, depth, include_employees):
        return {
            "id": department_id,
            "name":"test dep",
            "parent_id": None,
            "children": [],
            "employees": [] if include_employees else None,
            "created_at":"2026-05-12T12:00:00Z"
        }


class FakeEmployeeService:
    async def create_employee(self, department_id, full_name, position, hired_at):
        return {
            "id": 1,
            "department_id": department_id,
            "full_name": full_name,
            "position": position,
            "hired_at": hired_at,
            "created_at":"2026-05-12T12:00:00Z"
        }