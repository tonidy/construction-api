"""
Ports (Application Core Interfaces) - Hexagonal Architecture

These are the interfaces that define what the application needs.
They are implemented by adapters in the infrastructure layer.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from construction_api.models import Project as ProjectModel

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Generic repository interface for data access."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        """List all entities."""
        pass

    @abstractmethod
    def list_by_filter(self, **filters) -> List[T]:
        """List entities by dynamic filters."""
        pass

    @abstractmethod
    def list_by_filter_with_pagination(
        self, offset: int = 0, limit: int = 100, **filters
    ) -> List[T]:
        """List entities by dynamic filters with pagination at query level."""
        pass

    @abstractmethod
    def count_by_filter(self, **filters) -> int:
        """Count entities by dynamic filters."""
        pass


class ProjectServicePort(ABC):
    """Application service interface for project operations."""

    @abstractmethod
    def get_project_by_id(self, project_id: str) -> Optional[ProjectModel]:
        """Get a project by its ID."""
        pass

    @abstractmethod
    def list_projects_by_area(
        self, area: str, page: int = 1, per_page: int = 10
    ) -> tuple[List[ProjectModel], int]:
        """List projects filtered by area with pagination."""
        pass
