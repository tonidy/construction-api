"""Tests for the projects API endpoints."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Construction Projects API"}


def test_list_projects_by_area(client: TestClient, sample_projects):
    """Test listing projects filtered by area."""
    response = client.get("/api/v1/projects?area=London")
    assert response.status_code == 200

    data = response.json()
    assert data["area"] == "London"
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert data["total"] == 2
    assert len(data["projects"]) == 2

    # Verify project structure
    for project in data["projects"]:
        assert "project_name" in project
        assert "project_value" in project


def test_list_projects_by_area_no_results(client: TestClient, sample_projects):
    """Test listing projects for an area with no projects."""
    response = client.get("/api/v1/projects?area=NonExistent")
    assert response.status_code == 200

    data = response.json()
    assert data["area"] == "NonExistent"
    assert data["total"] == 0
    assert len(data["projects"]) == 0


def test_list_projects_pagination(client: TestClient, sample_projects):
    """Test pagination for project listing."""
    # Get first page
    response = client.get("/api/v1/projects?area=London&page=1&per_page=1")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["per_page"] == 1
    assert data["total"] == 2
    assert len(data["projects"]) == 1

    # Get second page
    response = client.get("/api/v1/projects?area=London&page=2&per_page=1")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 2
    assert data["per_page"] == 1
    assert data["total"] == 2
    assert len(data["projects"]) == 1


def test_get_project_by_id(client: TestClient, sample_projects):
    """Test getting a specific project by ID."""
    project_id = sample_projects[0].project_id
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == project_id
    assert data["project_name"] == "Test Project 1"
    assert data["company"] == "Test Company 1"
    assert data["project_value"] == 1000000


def test_get_project_not_found(client: TestClient, sample_projects):
    """Test getting a non-existent project."""
    response = client.get("/api/v1/projects/9999")
    assert response.status_code == 404

    data = response.json()
    assert data["title"] == "Resource Not Found"
    assert data["status"] == 404
    assert data["detail"] == "Project not found"
    assert data["instance"] == "/api/v1/projects/9999"


def test_list_projects_missing_area(client: TestClient):
    """Test that area parameter is required."""
    response = client.get("/api/v1/projects")
    assert response.status_code == 422

    data = response.json()
    assert data["title"] == "Request Validation Error"
    assert data["status"] == 422
    assert "area" in data["detail"]


def test_list_projects_invalid_pagination(client: TestClient, sample_projects):
    """Test invalid pagination parameters."""
    # Negative page
    response = client.get("/api/v1/projects?area=London&page=-1")
    assert response.status_code == 422
    data = response.json()
    assert data["title"] == "Request Validation Error"
    assert data["status"] == 422

    # per_page too low (must be >= 1)
    response = client.get("/api/v1/projects?area=London&per_page=0")
    assert response.status_code == 422
    data = response.json()
    assert data["title"] == "Request Validation Error"
    assert data["status"] == 422

    # Non-numeric page
    response = client.get("/api/v1/projects?area=London&page=abc")
    assert response.status_code == 422
    data = response.json()
    assert data["title"] == "Request Validation Error"
    assert data["status"] == 422

    # Non-numeric per_page
    response = client.get("/api/v1/projects?area=London&per_page=xyz")
    assert response.status_code == 422
    data = response.json()
    assert data["title"] == "Request Validation Error"
    assert data["status"] == 422
