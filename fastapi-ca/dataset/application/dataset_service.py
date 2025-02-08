from datetime import datetime
from ulid import ULID
from dataset.domain.dataset import Dataset
from dataset.domain.repository.dataset_repo import IDatasetRepository

class DatasetService:
    def __init__(
        self,
        dataset_repo: IDatasetRepository,
    ):
        self.dataset_repo = dataset_repo
        self.ulid = ULID()

    def get_datasets_by_project(
        self,
        page: int,
        items_per_page: int,
        project_id: str,
    ) -> tuple[int, list[Dataset]]:
        return self.dataset_repo.get_datasets_by_project(
            project_id=project_id,
            page=page,
            items_per_page=items_per_page,
        )

    def get_datasets_by_flow(
        self,
        page: int,
        items_per_page: int,
        flow_id: str,
    ) -> tuple[int, list[Dataset]]:
        return self.dataset_repo.get_datasets_by_flow(
            flow_id=flow_id,
            page=page,
            items_per_page=items_per_page,
        )

    def get_dataset(self, id: str) -> Dataset:
        return self.dataset_repo.find_by_id(id)

    def create_dataset(
        self,
        project_id: str,
        flow_id: str,
        name: str,
        size: float,
        path: str,
    ) -> Dataset:
        dataset = Dataset(
            id=self.ulid.generate(),
            project_id=project_id,
            flow_id=flow_id,
            name=name,
            size=size,
            path=path,
        )

        self.dataset_repo.save(dataset)

        return dataset

    def update_dataset(
        self,
        id: str,
        flow_id: str
    ) -> Dataset:
        dataset = self.dataset_repo.find_by_id(id)
        if flow_id:
            dataset.flow_id=flow_id
        else:
            dataset.flow_id=None

        return self.dataset_repo.update(flow_id, dataset)

    def delete_dataset(self, project_id: str, id: str):
        return self.dataset_repo.delete(project_id, id)