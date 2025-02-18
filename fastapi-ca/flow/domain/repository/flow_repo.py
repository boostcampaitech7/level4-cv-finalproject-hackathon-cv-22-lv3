from abc import ABCMeta, abstractmethod
from flow.domain.flow import Flow

class IFlowRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_flows(
        self,
        project_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[Flow]]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, project_id: str, id: str) -> Flow:
        raise NotImplementedError

    @abstractmethod
    def save(self, projct_id: str, flow: Flow) -> Flow:
        raise NotImplementedError

    @abstractmethod
    def update(self, project_id: str, flow: Flow) -> Flow:
        raise NotImplementedError

    @abstractmethod
    def delete(self, project_id: str, id: str):
        raise NotImplementedError