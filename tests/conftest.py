"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from construction_api.database import Base
from construction_api.main import app
from construction_api.models import Project, Company, project_area_map
from construction_api.dependencies import get_db, get_project_service, reset_container
from construction_api.adapters import ProjectRepository
from construction_api.services import ProjectService


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_project_service():
        project_repository = ProjectRepository(db_session=db_session)
        return ProjectService(project_repo=project_repository)

    # Override dependencies for testing
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_project_service] = override_get_project_service

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        reset_container()


@pytest.fixture(scope="function")
def sample_projects(db_session):
    """Create sample projects for testing."""
    # Create companies
    companies = [
        Company(company_id="c-001", company_name="Test Company 1"),
        Company(company_id="c-002", company_name="Test Company 2"),
    ]
    for company in companies:
        db_session.add(company)
    db_session.commit()

    # Create projects
    projects = [
        Project(
            project_id="p-001",
            project_name="Test Project 1",
            project_start="2024-01-01 00:00:00",
            project_end="2025-12-31 00:00:00",
            company_id="c-001",
            description="Description for test project 1",
            project_value=1000000,
        ),
        Project(
            project_id="p-002",
            project_name="Test Project 2",
            project_start="2024-06-01 00:00:00",
            project_end="2026-06-30 00:00:00",
            company_id="c-002",
            description="Description for test project 2",
            project_value=2000000,
        ),
        Project(
            project_id="p-003",
            project_name="Test Project 3",
            project_start="2023-01-01 00:00:00",
            project_end="2024-12-31 00:00:00",
            company_id="c-001",
            description="Description for test project 3",
            project_value=1500000,
        ),
    ]

    for project in projects:
        db_session.add(project)
    db_session.commit()

    # Create area mappings
    area_mappings = [
        {"project_id": "p-001", "area": "London"},
        {"project_id": "p-002", "area": "London"},
        {"project_id": "p-003", "area": "Manchester"},
    ]
    for mapping in area_mappings:
        db_session.execute(project_area_map.insert().values(**mapping))
    db_session.commit()

    for project in projects:
        db_session.refresh(project)

    return projects
