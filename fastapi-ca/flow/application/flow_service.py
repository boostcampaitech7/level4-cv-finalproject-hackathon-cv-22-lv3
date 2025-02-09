from datetime import datetime
from ulid import ULID
from flow.domain.flow import Flow
from flow.domain.repository.flow_repo import IFlowRepository

class FlowService:
    def __init__(
        self,
        flow_repo: IFlowRepository,
    ):
        self.flow_repo = flow_repo
        self.ulid = ULID()

    def get_flows(
        self,
        page: int,
        items_per_page: int,
        project_id: str,
    ) -> tuple[int, list[Flow]]:
        return self.flow_repo.get_flows(
            project_id=project_id,
            page=page,
            items_per_page=items_per_page,
        )

    def get_flow(self, user_id: str, id: str) -> Flow:
        return self.flow_repo.find_by_id(project_id, id)

    def create_flow(
        self,
        project_id: str,
        title: str,
        description: str,
    ) -> Flow:
        now = datetime.now()

        flow = Flow(
            id=self.ulid.generate(),
            project_id=project_id,
            title=title,
            description=description,
            created_at=now,
            updated_at=now,
        )

        self.flow_repo.save(flow)

        return flow

    def update_flow(
        self,
        project_id: str,
        id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> Flow:
        flow = self.flow_repo.find_by_id(project_id, id)
        if title:
            flow.title = title
        if description:
            flow.description = description

        return self.flow_repo.update(project_id, flow)

    def delete_flow(self, project_id: str, id: str):
        return self.flow_repo.delete(project_id, id)