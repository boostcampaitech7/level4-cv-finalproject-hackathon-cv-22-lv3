from dataclasses import asdict
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from common.auth import CurrentUser, get_current_user
from inform.application.inform_service import InformService
from containers import Container

router = APIRouter(prefix="/informs")

class InformResponse(BaseModel):
    id: str
    dataset_id: str
    model_config_path: str
    user_config_path: str

@router.post("/{dataset_id}", status_code=201)
@inject
def create_inform(
    dataset_id: str,
    inform_service: InformService = Depends(Provide[Container.inform_service]),
) -> InformResponse:
    created_inform = inform_service.create_inform(
        dataset_id=dataset_id,
    )

    return InformResponse(**asdict(created_inform))

@router.get("/{id}")
@inject
def get_inform(
    id: str,
    inform_service: InformService = Depends(Provide[Container.inform_service]),
) -> InformResponse:
    inform = inform_service.get_inform(
        id=id,
    )

    return InformResponse(**asdict(inform))

@router.get("/dataset/{dataset_id}")
@inject
def get_inform_by_dataset(
    dataset_id: str,
    inform_service: InformService = Depends(Provide[Container.inform_service]),
) -> InformResponse:
    inform = inform_service.get_inform_by_dataset(
        dataset_id=dataset_id,
    )

    return InformResponse(**asdict(inform))

class ConfigUpdates(BaseModel):
    target_feature: str
    controllable_feature: list[str]
    necessary_feature: list[str]
    limited_feature: int
    model: dict

@router.patch("/{id}")
@inject
def update_inform(
    id: str,
    config_updates: ConfigUpdates,
    inform_service: InformService = Depends(Provide[Container.inform_service]),
) -> InformResponse:
    inform = inform_service.update_inform(id, config_updates.dict())

    return inform

@router.delete("/{id}/{dataset_id}", status_code=204)
@inject
def delete_inform(
    id: str,
    dataset_id: str,
    inform_service: InformService = Depends(Provide[Container.inform_service]),
):
    inform_service.delete_inform(
        dataset_id=dataset_id,
        id=id,
    )