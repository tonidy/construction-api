"""
Adapters (Infrastructure Layer) - Hexagonal Architecture

These are the implementations of the ports using specific technologies.
This layer depends on the core (ports), not the other way around.
"""

from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from construction_api.ports import Repository
from construction_api.models import Project as ProjectModel, project_area_map


class ProjectRepository(Repository[ProjectModel]):
    """Repository for Project entity with area-based filtering."""

    def __init__(self, db_session: Session):
        self._db_session = db_session

    def get_by_id(self, id: str) -> Optional[ProjectModel]:
        return (
            self._db_session.query(ProjectModel)
            .options(joinedload(ProjectModel.company))
            .filter(ProjectModel.project_id == id)
            .first()
        )

    def list_all(self) -> List[ProjectModel]:
        return (
            self._db_session.query(ProjectModel)
            .options(joinedload(ProjectModel.company))
            .all()
        )

    def list_by_filter(self, **filters) -> List[ProjectModel]:
        """Filter projects by area using the join table (case-insensitive, partial match)."""
        from sqlalchemy import func

        query = self._db_session.query(ProjectModel).options(
            joinedload(ProjectModel.company)
        )
        area = filters.get("area")
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            query = query.join(project_area_map).filter(
                func.lower(project_area_map.c.area).like(func.lower(area_pattern))
            )
        return query.all()

    def list_by_filter_with_pagination(
        self, offset: int = 0, limit: int = 100, **filters
    ) -> List[ProjectModel]:
        """
        List entities with pagination at SQL level (LIMIT/OFFSET).

        This is efficient for large datasets as it doesn't load all rows into memory.
        Uses case-insensitive partial match for area.
        """
        from sqlalchemy import func

        query = self._db_session.query(ProjectModel).options(
            joinedload(ProjectModel.company)
        )
        area = filters.get("area")
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            query = query.join(project_area_map).filter(
                func.lower(project_area_map.c.area).like(func.lower(area_pattern))
            )
        return query.offset(offset).limit(limit).all()

    def count_by_filter(self, **filters) -> int:
        """Count entities by dynamic filters (case-insensitive, partial match)."""
        from sqlalchemy import func

        query = self._db_session.query(ProjectModel)
        area = filters.get("area")
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            query = query.join(project_area_map).filter(
                func.lower(project_area_map.c.area).like(func.lower(area_pattern))
            )
        return query.count()

    def get_original_area_case(self, area: str) -> Optional[str]:
        """Get the original case of an area from the database (case-insensitive)."""
        from sqlalchemy import func

        result = (
            self._db_session.query(project_area_map.c.area)
            .filter(func.lower(project_area_map.c.area) == func.lower(area))
            .first()
        )
        return result[0] if result else None

    def get_original_area_case_partial(self, area: str) -> Optional[str]:
        """Get the original case of an area from the database (partial match, case-insensitive)."""
        from sqlalchemy import func

        # Auto-wrap with wildcards for partial match
        area_pattern = f"%{area}%"
        result = (
            self._db_session.query(project_area_map.c.area)
            .filter(func.lower(project_area_map.c.area).like(func.lower(area_pattern)))
            .first()
        )
        return result[0] if result else None

    def get_areas_for_project(self, project_id: str) -> List[str]:
        """Get list of areas for a specific project."""
        result = (
            self._db_session.query(project_area_map.c.area)
            .filter(project_area_map.c.project_id == project_id)
            .all()
        )
        return [row[0] for row in result]

    def get_projects_by_area(self, area: str) -> List[ProjectModel]:
        """Get all projects in a specific area (case-insensitive)."""
        from sqlalchemy import func

        return (
            self._db_session.query(ProjectModel)
            .options(joinedload(ProjectModel.company))
            .join(project_area_map)
            .filter(func.lower(project_area_map.c.area) == func.lower(area))
            .all()
        )
