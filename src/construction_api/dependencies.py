"""
Dependency Injection Container - Hexagonal Lite Architecture

This module provides the DI container and dependency providers for the application.
"""

from typing import Generator

from sqlalchemy.orm import Session

from construction_api.database import SessionLocal
from construction_api.adapters import ProjectRepository, DummyProjectRepository, RawProjectRepository
from construction_api.services import ProjectService
from construction_api.ports import ProjectServicePort


class DIContainer:
    """
    Dependency Injection Container for managing application dependencies.

    This container follows the hexagonal architecture pattern where:
    - Core business logic depends on abstractions (ports)
    - Infrastructure implementations (adapters) are injected at runtime
    """

    def __init__(self, get_db_session: callable = None):
        self._get_db_session = get_db_session or self._default_get_db_session

    @staticmethod
    def _default_get_db_session() -> Generator[Session, None, None]:
        """Default database session provider."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_db_session(self) -> Generator[Session, None, None]:
        """Get database session."""
        yield from self._get_db_session()

    def get_project_repository(self, db: Session) -> ProjectRepository:
        """Get ProjectRepository instance."""
        return ProjectRepository(db_session=db)
    
    def get_dummy_project_repository(self) -> DummyProjectRepository:
        return DummyProjectRepository()

    def get_project_service(self, db: Session) -> ProjectServicePort:
        """Get ProjectService instance (depends on ProjectRepository)."""
        project_repository = self.get_project_repository(db)
        return ProjectService(project_repo=project_repository)

    def get_raw_project_repository(self, db: Session) -> RawProjectRepository:
        """Get RawProjectRepository instance."""
        return RawProjectRepository(db_session=db)

    def get_project_service_with_raw_repo(self, db: Session) -> ProjectServicePort:
        """Get ProjectService instance using raw SQL repository."""
        project_repository = self.get_raw_project_repository(db)
        return ProjectService(project_repo=project_repository)


# Global DI container instance
_container: DIContainer = None


def get_container() -> DIContainer:
    """Get the global DI container instance."""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def set_container(container: DIContainer) -> None:
    """Set the global DI container (useful for testing with mocks)."""
    global _container
    _container = container


def reset_container() -> None:
    """Reset the global DI container to default."""
    global _container
    _container = DIContainer()


# Dependency providers for FastAPI routes
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_project_service_internal(db: Session) -> ProjectServicePort:
    """Internal function to create ProjectService."""
    container = get_container()
    return container.get_project_service(db)


def get_project_service() -> Generator[ProjectServicePort, None, None]:
    """
    FastAPI dependency for ProjectService.

    This is the main dependency that routes should use.
    It provides the application service layer following hexagonal architecture.

    Yields:
        ProjectServicePort: Project service instance
    """
    db = SessionLocal()
    try:
        yield _get_project_service_internal(db)
    finally:
        db.close()


def _get_project_service_with_raw_repo_internal(db: Session) -> ProjectServicePort:
    """Internal function to create ProjectService with raw repository."""
    container = get_container()
    return container.get_project_service_with_raw_repo(db)


def get_project_service_with_raw_repo() -> Generator[ProjectServicePort, None, None]:
    """
    FastAPI dependency for ProjectService using raw SQL repository.

    This dependency uses raw SQL queries instead of ORM for better performance.

    Yields:
        ProjectServicePort: Project service instance with raw SQL repository
    """
    db = SessionLocal()
    try:
        yield _get_project_service_with_raw_repo_internal(db)
    finally:
        db.close()
