from dependency_injector import containers, providers
from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository
from project.application.project_service import ProjectService
from project.infra.repository.project_repo import ProjectRepository
from flow.application.flow_service import FlowService
from flow.infra.repository.flow_repo import FlowRepository
from dataset.application.dataset_service import DatasetService
from dataset.infra.repository.dataset_repo import DatasetRepository
from inform.application.inform_service import InformService
from inform.infra.repository.inform_repo import InformRepository
from fastapi import BackgroundTasks

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "user",
            "project",
            "flow",
            "dataset",
            "inform",
        ],
    )

    user_repo = providers.Factory(UserRepository)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
    )
    project_repo = providers.Factory(ProjectRepository)
    project_service = providers.Factory(ProjectService, project_repo=project_repo)
    flow_repo = providers.Factory(FlowRepository)
    flow_service = providers.Factory(FlowService, flow_repo=flow_repo)
    dataset_repo = providers.Factory(DatasetRepository)
    dataset_service = providers.Factory(DatasetService, dataset_repo=dataset_repo)
    inform_repo = providers.Factory(InformRepository)
    inform_service = providers.Factory(InformService, inform_repo=inform_repo)