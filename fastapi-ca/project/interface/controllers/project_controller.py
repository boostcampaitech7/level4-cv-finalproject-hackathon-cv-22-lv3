from dataclasses import asdict
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from common.auth import CurrentUser, get_current_user
from project.application.project_service import ProjectService
from containers import Container

router = APIRouter(prefix="/projects")

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

class CreateProjectBody(BaseModel):
    title: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=0)

@router.post("", status_code=201)
@inject
def create_project(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CreateProjectBody,
    project_service: ProjectService = Depends(Provide[Container.project_service]),
) -> ProjectResponse:
    created_project = project_service.create_project(
        user_id=current_user.id,
        title=body.title,
        description=body.description,
    )

    return created_project

class GetProjectsResponse(BaseModel):
    total_count: int
    page: int
    projects: list[ProjectResponse]

@router.get("")
@inject
def get_projects(
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_current_user),
    project_service: ProjectService = Depends(Provide[Container.project_service]),
) -> GetProjectsResponse:
    total_count, projects = project_service.get_projects(
        user_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )

    return {
        "total_count": total_count,
        "page": page,
        "projects": projects,
    }

@router.get("/{id}")
@inject
def get_project(
    id: str,  # id 추가
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    project_service: ProjectService = Depends(Provide[Container.project_service]),
) -> ProjectResponse:
    project = project_service.get_project(
        user_id=current_user.id,
        id=id,  # id 전달
    )

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")  # 404로 변경

    return project


class UpdateProjectBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, min_length=0)

@router.put("/{id}")
@inject
def update_project(
    id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateProjectBody,
    project_service: ProjectService = Depends(Provide[Container.project_service]),
) -> ProjectResponse:
    project = project_service.update_project(
        user_id=current_user.id,
        id=id,
        title=body.title,
        description=body.description,
    )

    return project


@router.delete("/{id}", status_code=204)
@inject
def delete_project(
    id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    project_service: ProjectService = Depends(Provide[Container.project_service]),
):
    project_service.delete_project(
        user_id=current_user.id,
        id=id,
    )
