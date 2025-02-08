from dependency_injector import containers, providers
from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository
from project.application.project_service import ProjectService
from project.infra.repository.project_repo import ProjectRepository
from flow.application.flow_service import FlowService
from flow.infra.repository.flow_repo import FlowRepository
from dataset.application.dataset_service import DatasetService
from dataset.infra.repository.dataset_repo import DatasetRepository
from config.application.config_service import ConfigService
from config.infra.repository.config_repo import ConfigRepository
from fastapi import BackgroundTasks
from user.application.email_service import EmailService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "user",
            "project",
            "flow",
            "dataset",
            "config",
        ],
    )

    email_service = providers.Factory(EmailService)
    user_repo = providers.Factory(UserRepository)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        email_service=email_service
    )
    project_repo = providers.Factory(ProjectRepository)
    project_service = providers.Factory(ProjectService, project_repo=project_repo)
    flow_repo = providers.Factory(FlowRepository)
    flow_service = providers.Factory(FlowService, flow_repo=flow_repo)
    dataset_repo = providers.Factory(DatasetRepository)
    dataset_service = providers.Factory(DatasetService, dataset_repo=dataset_repo)
    config_repo = providers.Factory(ConfigRepository)
    config_service = providers.Factory(ConfigService, config_repo=config_repo)