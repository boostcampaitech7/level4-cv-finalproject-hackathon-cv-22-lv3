from dataclasses import asdict
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from common.auth import CurrentUser, get_current_user
from dataset.application.dataset_service import DatasetService
from containers import Container

router = APIRouter(prefix="/datasets")

class DatasetResponse(BaseModel):
    id: str
    project_id: str
    flow_id: str | None
    name: str
    size: float
    path: str

class CreateDatasetBody(BaseModel):
    project_id: str
    flow_id: str | None = None
    name: str
    size: float
    path: str

@router.post("", status_code=201)
@inject
def create_dataset(
    body: CreateDatasetBody,
    dataset_service: DatasetService = Depends(Provide[Container.dataset_service]),
) -> DatasetResponse:
    created_dataset = dataset_service.create_dataset(
        project_id=body.project_id,
        flow_id=body.flow_id,
        name=body.name,
        size=body.size,
        path=body.path,
    )

    return created_dataset

class GetDatasetsResponse(BaseModel):
    total_count: int
    page: int
    datasets: list[DatasetResponse]

@router.get("/project/{project_id}")
@inject
def get_datasets_by_project(
    project_id: str,
    page: int = 1,
    items_per_page: int = 10,
    dataset_service: DatasetService = Depends(Provide[Container.dataset_service]),
) -> GetDatasetsResponse:
    total_count, datasets = dataset_service.get_datasets_by_project(
        project_id=project_id,
        page=page,
        items_per_page=items_per_page,
    )

    return {
        "total_count": total_count,
        "page": page,
        "datasets": datasets,
    }

@router.get("/flow/{flow_id}")
@inject
def get_datasets_by_flow(
    flow_id: str,
    page: int = 1,
    items_per_page: int = 10,
    dataset_service: DatasetService = Depends(Provide[Container.dataset_service]),
) -> GetDatasetsResponse:
    total_count, datasets = dataset_service.get_datasets_by_flow(
        flow_id=flow_id,
        page=page,
        items_per_page=items_per_page,
    )

    return {
        "total_count": total_count,
        "page": page,
        "datasets": datasets,
    }

@router.get("/{id}")
@inject
def get_dataset(
    id: str,
    dataset_service: DatasetService = Depends(Provide[Container.dataset_service]),
) -> DatasetResponse:
    dataset = dataset_service.get_dataset(
        id=id,
    )

    return dataset

class UpdateDatasetBody(BaseModel):
    id: str
    flow_id: str | None

# 기존 PUT 엔드포인트를 PATCH로 변경하고 URL 구조 수정
@router.patch("/{id}")  # URL 구조 단순화
@inject
def update_dataset(
    id: str,
    body: UpdateDatasetBody,
    dataset_service: DatasetService = Depends(Provide[Container.dataset_service]),
) -> DatasetResponse:
    dataset = dataset_service.update_dataset(
        id=id,  # URL에서 받은 id 사용
        flow_id=body.flow_id,  # body에서 flow_id만 받음
    )

    return dataset


@router.delete("/{id}/{project_id}", status_code=204)
@inject
def delete_dataset(
    id: str,
    project_id: str,
    dataset_service: DatasetService = Depends(Provide[Container.dataset_service]),
):
    dataset_service.delete_dataset(
        project_id=project_id,
        id=id,
    )
