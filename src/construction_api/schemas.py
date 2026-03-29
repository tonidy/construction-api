from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from construction_api.domain.entities import Project


class ProjectResponse(BaseModel):
    id: str
    project_name: str
    project_start: str
    project_end: str
    company: str
    description: Optional[str] = None
    project_value: int
    areas: List[str] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_domain(
        cls, project: Project, areas: Optional[List[str]] = None
    ) -> ProjectResponse:
        """Convert Project domain entity to ProjectResponse."""
        return cls(
            id=project.project_id,
            project_name=project.project_name,
            project_start=project.project_start,
            project_end=project.project_end,
            company=project.company_name,
            description=project.description,
            project_value=project.project_value,
            areas=areas or [],
        )


class ProjectListResponse(BaseModel):
    area: str
    page: int
    per_page: int
    total: int
    projects: List[ProjectResponse]


class ProjectAreasResponse(BaseModel):
    project_id: str
    project_name: str
    areas: List[str]
