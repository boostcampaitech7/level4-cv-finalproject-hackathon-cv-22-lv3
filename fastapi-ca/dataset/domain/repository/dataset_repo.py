from abc import ABCMeta, abstractmethod
from dataset.domain.dataset import Dataset

class IDatasetRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_datasets_by_project(
        self,
        project_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[Dataset]]:
        raise NotImplementedError

    def get_datasets_by_flow(
        self,
        flow_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[Dataset]]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> Dataset:
        raise NotImplementedError

    @abstractmethod
    def save(self, projct_id: str, flow_id: str | None, dataset: Dataset) -> Dataset:
        raise NotImplementedError

    @abstractmethod
    def update(self, flow_id: str | None, dataset: Dataset) -> Dataset:
        raise NotImplementedError

    @abstractmethod
    def delete(self, project_id: str, id: str):
        raise NotImplementedError