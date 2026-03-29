"""
Application Services - Hexagonal Architecture Core

Business logic and application services. This is the heart of the application.
"""

from typing import Optional, List

from construction_api.ports import ProjectServicePort, Repository
from construction_api.domain.entities import Project


class ProjectService(ProjectServicePort):
    """
    Application service for project operations.

    This is part of the application core and contains business logic.
    It depends on repository abstractions (ports), not concrete implementations.
    """

    def __init__(self, project_repo: Repository[Project]):
        self._project_repo = project_repo

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Get a project by its ID."""
        return self._project_repo.get_by_id(project_id)

    def list_projects_by_area(
        self, area: str, page: int = 1, per_page: int = 10
    ) -> tuple[List[Project], int, str]:
        """
        List projects filtered by area with pagination.

        Pagination is performed at the database query level for efficiency.
        Page is 1-based.
        Returns: (projects, total, original_area_case)
        """
        total = self._project_repo.count_by_filter(area=area)
        offset = (page - 1) * per_page
        projects = self._project_repo.list_by_filter_with_pagination(
            area=area, offset=offset, limit=per_page
        )
        # Get original area case from database (partial match)
        original_area = self._project_repo.get_original_area_case_partial(area) or area
        return projects, total, original_area

    def get_areas_for_project(self, project_id: str) -> List[str]:
        """Get list of areas for a specific project."""
        return self._project_repo.get_areas_for_project(project_id)
