import pytest


@pytest.mark.anyio
async def test_create_department(client, override_dependencies):
    payload = {"name": "IT", "parent_id": None}

    resp = await client.post("/departments/", json=payload)

    assert resp.status_code == 201
    data = resp.json()

    assert data["name"] == "IT"
    assert data["parent_id"] is None
    assert "id" in data


@pytest.mark.anyio
async def test_create_department_conflict(client, override_dependencies):
    dept_service, _ = override_dependencies

    async def exists(name, parent_id):
        return True

    dept_service.get_department_by_name_and_parent_id = exists

    payload = {"name": "IT", "parent_id": None}

    resp = await client.post("/departments/", json=payload)

    assert resp.status_code in (400, 409)


@pytest.mark.anyio
async def test_delete_department(client):
    resp = await client.delete(
        "/departments/1",
        params={"mode": "reassign", "reassign_to_department_id": 2},
    )

    assert resp.status_code == 204
    assert resp.text == ""


@pytest.mark.anyio
async def test_update_department(client):
    payload = {"name": "New Name"}

    resp = await client.patch("/departments/1", json=payload)

    assert resp.status_code == 200
    data = resp.json()

    assert data["name"] == "New Name"
    assert data["id"] == 1


@pytest.mark.anyio
async def test_create_employee(client):
    payload = {
        "full_name": "John Doe",
        "position": "Engineer",
        "hired_at": "2024-01-01",
    }

    resp = await client.post("/departments/1/employees/", json=payload)

    assert resp.status_code == 201
    data = resp.json()

    assert data["full_name"] == "John Doe"
    assert data["department_id"] == 1


@pytest.mark.anyio
async def test_get_department_tree(client):
    resp = await client.get(
        "/departments/1",
        params={"depth": 2, "include_employees": True},
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["id"] == 1
    assert "children" in data
