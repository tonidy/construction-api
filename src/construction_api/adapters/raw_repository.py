"""
Raw SQL Repository Adapter - Infrastructure Layer

This repository implements the Repository interface using raw SQL queries
instead of SQLAlchemy ORM, providing direct SQL control and better performance.
"""

from typing import Optional, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from construction_api.ports import Repository
from construction_api.domain.entities import Project


class RawProjectRepository(Repository[Project]):
    """Repository for Project entity using raw SQL queries."""

    def __init__(self, db_session: Session):
        self._db_session = db_session

    def _row_to_project(self, row) -> Project:
        """Convert a database row to a domain Project entity."""
        return Project(
            project_id=row.project_id,
            project_name=row.project_name,
            project_start=row.project_start,
            project_end=row.project_end,
            company_id=row.company_id,
            company_name=row.company_name if hasattr(row, 'company_name') else None,
            description=row.description,
            project_value=row.project_value,
        )

    def get_by_id(self, id: str) -> Optional[Project]:
        """Get project by ID using raw SQL."""
        result = self._db_session.execute(
            text("""
                SELECT 
                    p.project_id,
                    p.project_name,
                    p.project_start,
                    p.project_end,
                    p.company_id,
                    c.company_name,
                    p.description,
                    p.project_value
                FROM projects p
                LEFT JOIN companies c ON p.company_id = c.company_id
                WHERE p.project_id = :id
            """),
            {"id": id}
        ).first()
        
        return self._row_to_project(result) if result else None

    def list_all(self) -> List[Project]:
        """List all projects using raw SQL."""
        results = self._db_session.execute(
            text("""
                SELECT 
                    p.project_id,
                    p.project_name,
                    p.project_start,
                    p.project_end,
                    p.company_id,
                    c.company_name,
                    p.description,
                    p.project_value
                FROM projects p
                LEFT JOIN companies c ON p.company_id = c.company_id
            """)
        ).fetchall()
        
        return [self._row_to_project(row) for row in results]

    def list_by_filter(self, **filters) -> List[Project]:
        """Filter projects by area using raw SQL (case-insensitive, partial match)."""
        area = filters.get("area")
        
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            results = self._db_session.execute(
                text("""
                    SELECT DISTINCT
                        p.project_id,
                        p.project_name,
                        p.project_start,
                        p.project_end,
                        p.company_id,
                        c.company_name,
                        p.description,
                        p.project_value
                    FROM projects p
                    LEFT JOIN companies c ON p.company_id = c.company_id
                    INNER JOIN project_area_map pam ON p.project_id = pam.project_id
                    WHERE LOWER(pam.area) LIKE LOWER(:area_pattern)
                """),
                {"area_pattern": area_pattern}
            ).fetchall()
        else:
            results = self._db_session.execute(
                text("""
                    SELECT 
                        p.project_id,
                        p.project_name,
                        p.project_start,
                        p.project_end,
                        p.company_id,
                        c.company_name,
                        p.description,
                        p.project_value
                    FROM projects p
                    LEFT JOIN companies c ON p.company_id = c.company_id
                """)
            ).fetchall()
        
        return [self._row_to_project(row) for row in results]

    def list_by_filter_with_pagination(
        self, offset: int = 0, limit: int = 100, **filters
    ) -> List[Project]:
        """
        List projects with pagination at SQL level using raw SQL.
        
        This is efficient for large datasets as it doesn't load all rows into memory.
        Uses case-insensitive partial match for area.
        """
        area = filters.get("area")
        
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            results = self._db_session.execute(
                text("""
                    SELECT DISTINCT
                        p.project_id,
                        p.project_name,
                        p.project_start,
                        p.project_end,
                        p.company_id,
                        c.company_name,
                        p.description,
                        p.project_value
                    FROM projects p
                    LEFT JOIN companies c ON p.company_id = c.company_id
                    INNER JOIN project_area_map pam ON p.project_id = pam.project_id
                    WHERE LOWER(pam.area) LIKE LOWER(:area_pattern)
                    ORDER BY p.project_value DESC, p.project_name ASC
                    LIMIT :limit OFFSET :offset
                """),
                {"area_pattern": area_pattern, "limit": limit, "offset": offset}
            ).fetchall()
        else:
            results = self._db_session.execute(
                text("""
                    SELECT 
                        p.project_id,
                        p.project_name,
                        p.project_start,
                        p.project_end,
                        p.company_id,
                        c.company_name,
                        p.description,
                        p.project_value
                    FROM projects p
                    LEFT JOIN companies c ON p.company_id = c.company_id
                    ORDER BY p.project_value DESC, p.project_name ASC
                    LIMIT :limit OFFSET :offset
                """),
                {"limit": limit, "offset": offset}
            ).fetchall()
        
        return [self._row_to_project(row) for row in results]

    def count_by_filter(self, **filters) -> int:
        """Count projects by dynamic filters using raw SQL (case-insensitive, partial match)."""
        area = filters.get("area")
        
        if area:
            # Auto-wrap with wildcards for partial match
            area_pattern = f"%{area}%"
            result = self._db_session.execute(
                text("""
                    SELECT COUNT(DISTINCT p.project_id) as count
                    FROM projects p
                    INNER JOIN project_area_map pam ON p.project_id = pam.project_id
                    WHERE LOWER(pam.area) LIKE LOWER(:area_pattern)
                """),
                {"area_pattern": area_pattern}
            ).scalar()
        else:
            result = self._db_session.execute(
                text("SELECT COUNT(*) as count FROM projects")
            ).scalar()
        
        return result

    def get_original_area_case(self, area: str) -> Optional[str]:
        """Get the original case of an area from the database (case-insensitive)."""
        result = self._db_session.execute(
            text("""
                SELECT area
                FROM project_area_map
                WHERE LOWER(area) = LOWER(:area)
                LIMIT 1
            """),
            {"area": area}
        ).scalar()
        
        return result

    def get_original_area_case_partial(self, area: str) -> Optional[str]:
        """Get the original case of an area from the database (partial match, case-insensitive)."""
        # Auto-wrap with wildcards for partial match
        area_pattern = f"%{area}%"
        result = self._db_session.execute(
            text("""
                SELECT area
                FROM project_area_map
                WHERE LOWER(area) LIKE LOWER(:area_pattern)
                LIMIT 1
            """),
            {"area_pattern": area_pattern}
        ).scalar()
        
        return result

    def get_areas_for_project(self, project_id: str) -> List[str]:
        """Get list of areas for a specific project using raw SQL."""
        results = self._db_session.execute(
            text("""
                SELECT area
                FROM project_area_map
                WHERE project_id = :project_id
            """),
            {"project_id": project_id}
        ).fetchall()
        
        return [row[0] for row in results]

    def get_projects_by_area(self, area: str) -> List[Project]:
        """Get all projects in a specific area using raw SQL (case-insensitive)."""
        results = self._db_session.execute(
            text("""
                SELECT DISTINCT
                    p.project_id,
                    p.project_name,
                    p.project_start,
                    p.project_end,
                    p.company_id,
                    c.company_name,
                    p.description,
                    p.project_value
                FROM projects p
                LEFT JOIN companies c ON p.company_id = c.company_id
                INNER JOIN project_area_map pam ON p.project_id = pam.project_id
                WHERE LOWER(pam.area) = LOWER(:area)
            """),
            {"area": area}
        ).fetchall()
        
        return [self._row_to_project(row) for row in results]
