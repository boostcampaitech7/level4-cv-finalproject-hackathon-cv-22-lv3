from dataclasses import asdict
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from common.auth import CurrentUser, get_current_user
from flow.application.flow_service import FlowService
from containers import Container

router = APIRouter(prefix="/flows")

class FlowResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

class CreateFlowBody(BaseModel):
    project_id: str
    title: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=0)

@router.post("", status_code=201)
@inject
def create_flow(
    body: CreateFlowBody,
    flow_service: FlowService = Depends(Provide[Container.flow_service]),
) -> FlowResponse:
    created_flow = flow_service.create_flow(
        project_id=body.project_id,
        title=body.title,
        description=body.description,
    )

    return created_flow

class GetFlowsResponse(BaseModel):
    total_count: int
    page: int
    flows: list[FlowResponse]

@router.get("")
@inject
def get_flows(
    project_id: str,
    page: int = 1,
    items_per_page: int = 10,
    flow_service: FlowService = Depends(Provide[Container.flow_service]),
) -> GetFlowsResponse:
    total_count, flows = flow_service.get_flows(
        project_id=project_id,
        page=page,
        items_per_page=items_per_page,
    )

    return {
        "total_count": total_count,
        "page": page,
        "flows": flows,
    }

@router.get("/{id}")
@inject
def get_flow(
    id: str,
    project_id,
    flow_service: FlowService = Depends(Provide[Container.flow_service]),
) -> FlowResponse:
    flow = flow_service.get_flow(
        project_id=project_id,
        id=id,
    )

    return flow

class UpdateFlowBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, min_length=0)

@router.put("/{id}")
@inject
def update_flow(
    id: str,
    project_id,
    body: UpdateFlowBody,
    flow_service: FlowService = Depends(Provide[Container.flow_service]),
) -> FlowResponse:
    flow = flow_service.update_flow(
        project_id=project_id,
        id=id,
        title=body.title,
        description=body.description,
    )

    return flow


@router.delete("/{id}/{project_id}", status_code=204)
@inject
def delete_flow(
    id: str,
    project_id,
    flow_service: FlowService = Depends(Provide[Container.flow_service]),
):
    flow_service.delete_flow(
        project_id=project_id,
        id=id,
    )
