"""Domain entities - pure business logic classes without SQLAlchemy dependencies."""

from dataclasses import dataclass


@dataclass
class Company:
    """Company domain entity."""

    company_id: str
    company_name: str


@dataclass
class Project:
    """Project domain entity."""

    project_id: str
    project_name: str
    project_start: str
    project_end: str
    company_id: str | None = None
    company_name: str | None = None
    description: str | None = None
    project_value: int = 0
