from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.api.schemas.employees import EmployeeSchema
from app.exceptions.department import DepartmentValidationError


class DepartmentCreateSchema(BaseModel):
    name: str = Field(
        ...,
        json_schema_extra={"example": "Backend Team"},
        min_length=1,
        max_length=200,
    )

    parent_id: Optional[int] = Field(
        default=None,
        json_schema_extra={"example": 1},
    )

class DepartmentDeleteSchema(BaseModel):
    mode: Literal["cascade", "reassign"] = Field(
        ...,
        description="Delete mode: cascade or reassign",
    )

    reassign_to_department_id: Optional[int] = Field(
        default=None,
        description=(
            "Required only when mode=reassign"
        ),
    )

    @model_validator(mode="after")
    def validate_reassign(self):
        if self.mode == "reassign":
            if self.reassign_to_department_id is None:
                raise DepartmentValidationError(
                    "reassign_to_department_id is required when mode=reassign"
                )

        return self

class DepartmentResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Backend Team",
                "parent_id": None,
                "created_at": "2026-05-12T12:00:00Z",
            }
        },
    )

    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime


class DepartmentTreeSchema(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime

    employees: list[EmployeeSchema] = []

    children: list["DepartmentTreeSchema"] = []

DepartmentTreeSchema.model_rebuild()



class DepartmentUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None)
    parent_id: Optional[int] = Field(default=None)