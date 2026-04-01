"""
Adapters (Infrastructure Layer) - Hexagonal Architecture

These are the implementations of the ports using specific technologies.
This layer depends on the core (ports), not the other way around.
"""

from typing import Optional, List

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, joinedload

from construction_api.ports import Repository
from construction_api.domain.entities import Project
from construction_api.adapters.orm import project_area_map, ProjectORM


class DummyProjectRepository(Repository[Project]):
    """Repository for Project entity with area-based filtering."""

    def __init__(self, db_session: Session):
        self._db_session = db_session

    def _to_domain(self, orm_project: ProjectORM) -> Project:
        """Convert ProjectORM to domain Project entity."""
        return Project(
            project_id=orm_project.project_id,
            project_name=orm_project.project_name,
            project_start=orm_project.project_start,
            project_end=orm_project.project_end,
            company_id=orm_project.company_id,
            company_name=orm_project.company.company_name if orm_project.company else None,
            description=orm_project.description,
            project_value=orm_project.project_value,
        )

    def get_by_id(self, id: str) -> Optional[Project]:
        orm_result = (
            self._db_session.query(ProjectORM)
            .options(joinedload(ProjectORM.company))
            .filter(ProjectORM.project_id == id)
            .first()
        )
        return self._to_domain(orm_result) if orm_result else None

    def list_all(self) -> List[Project]:
        orm_results = (
            self._db_session.query(ProjectORM)
            .options(joinedload(ProjectORM.company))
            .all()
        )
        return [self._to_domain(p) for p in orm_results]

    def list_by_filter(self, **filters) -> List[Project]:
        """Filter projects by area using the join table (case-insensitive, partial match)."""
        from sqlalchemy import func

        query = self._db_session.query(ProjectORM).options(
            joinedload(ProjectORM.company)
        )
        area = filters.get("area")
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            query = query.join(project_area_map).filter(
                func.lower(project_area_map.c.area).like(func.lower(area_pattern))
            )
        orm_results = query.all()
        return [self._to_domain(p) for p in orm_results]

    def list_by_filter_with_pagination(
        self, offset: int = 0, limit: int = 100, **filters
    ) -> List[Project]:
        """
        List entities with pagination at SQL level (LIMIT/OFFSET).

        This is efficient for large datasets as it doesn't load all rows into memory.
        Uses case-insensitive partial match for area.
        """
        from sqlalchemy import func

        query = self._db_session.query(ProjectORM).options(
            joinedload(ProjectORM.company)
        )
        area = filters.get("area")
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            query = query.join(project_area_map).filter(
                func.lower(project_area_map.c.area).like(func.lower(area_pattern))
            )
        orm_results = query.order_by(
            desc(ProjectORM.project_value),
            asc(ProjectORM.project_name),
        ).offset(offset).limit(limit).all()
        return [self._to_domain(p) for p in orm_results]

    def count_by_filter(self, **filters) -> int:
        """Count entities by dynamic filters (case-insensitive, partial match)."""
        from sqlalchemy import func

        query = self._db_session.query(ProjectORM)
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

    def get_projects_by_area(self, area: str) -> List[Project]:
        """Get all projects in a specific area (case-insensitive)."""
        from sqlalchemy import func

        orm_results = (
            self._db_session.query(ProjectORM)
            .options(joinedload(ProjectORM.company))
            .join(project_area_map)
            .filter(func.lower(project_area_map.c.area) == func.lower(area))
            .all()
        )
        return [self._to_domain(p) for p in orm_results]
