from fastapi import APIRouter, Depends, HTTPException, Query

from construction_api.dependencies import get_project_service
from construction_api.ports import ProjectServicePort
from construction_api.schemas import (
    ProjectListResponse,
    ProjectResponse,
    ProjectAreasResponse,
)

router = APIRouter()


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects_by_area(
    area: str = Query(
        ..., description="Filter projects by area (case-insensitive, partial match)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(10, ge=1, description="Items per page"),
    project_service: ProjectServicePort = Depends(get_project_service),
):
    """
    List construction projects filtered by area.

    - **area**: Required. The area to filter projects by (case-insensitive, partial match).
      Examples: "lee" matches "Leeds", "man" matches "Manchester".
    - **page**: Page number (1-based, default: 1).
    - **per_page**: Items per page (default: 10).
    """
    projects, total, original_area = project_service.list_projects_by_area(
        area=area, page=page, per_page=per_page
    )

    return ProjectListResponse(
        area=original_area,
        page=page,
        per_page=per_page,
        total=total,
        projects=[
            ProjectResponse.from_domain(p, areas=[original_area]) for p in projects
        ],
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    project_service: ProjectServicePort = Depends(get_project_service),
):
    """
    Get a specific project by ID.

    - **project_id**: The ID of the project to retrieve.
    """
    project = project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    areas = project_service.get_areas_for_project(project_id)
    return ProjectResponse.from_domain(project, areas=areas)


@router.get("/projects/{project_id}/areas", response_model=ProjectAreasResponse)
async def get_project_areas(
    project_id: str,
    project_service: ProjectServicePort = Depends(get_project_service),
):
    """
    Get all areas for a specific project.

    - **project_id**: The ID of the project.
    """
    project = project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    areas = project_service.get_areas_for_project(project_id)
    return ProjectAreasResponse(
        project_id=project.project_id,
        project_name=project.project_name,
        areas=areas,
    )
