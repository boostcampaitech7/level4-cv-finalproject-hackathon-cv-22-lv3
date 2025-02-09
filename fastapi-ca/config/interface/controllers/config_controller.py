from dataclasses import asdict
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from common.auth import CurrentUser, get_current_user
from config.application.config_service import ConfigService
from containers import Container

router = APIRouter(prefix="/configs")

class ConfigResponse(BaseModel):
    id: str
    dataset_id: str
    path: str

class CreateConfigBody(BaseModel):
    path: str

@router.post("{dataset_id}", status_code=201)
@inject
def create_config(
    body: CreateConfigBody,
    dataset_id: str,
    config_service: ConfigService = Depends(Provide[Container.config_service]),
) -> ConfigResponse:
    created_config = config_service.create_config(
        dataset_id=dataset_id,
        path=body.path,
    )

    return created_config

@router.get("/{id}")
@inject
def get_config(
    id: str,
    config_service: ConfigService = Depends(Provide[Container.config_service]),
) -> ConfigResponse:
    config = config_service.get_config(
        id=id,
    )

    return config

@router.get("/{dataset_id}")
@inject
def get_config_by_dataset(
    dataset_id: str,
    config_service: ConfigService = Depends(Provide[Container.config_service]),
) -> ConfigResponse:
    config = config_service.get_config(
        dataset_id=dataset_id,
    )

    return config

@router.delete("/{id}/{dataset_id}", status_code=204)
@inject
def delete_config(
    id: str,
    dataset_id: str,
    config_service: ConfigService = Depends(Provide[Container.config_service]),
):
    config_service.delete_config(
        dataset_id=dataset_id,
        id=id,
    )
