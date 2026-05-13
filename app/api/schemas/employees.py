# app/api/schemas/employee.py

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EmployeeCreateSchema(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        json_schema_extra={"example": "John Doe"},
    )

    position: str = Field(
        ...,
        min_length=1,
        max_length=255,
        json_schema_extra={"example": "Backend Developer"},
    )

    hired_at: Optional[date] = Field(
        default=None,
        json_schema_extra={"example": "2026-05-12"},
    )


class EmployeeResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: Optional[date]
    created_at: datetime


class EmployeeSchema(BaseModel):
    id: int
    full_name: str
    position: str
    hired_at: Optional[date]
    created_at: datetime
