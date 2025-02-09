from fastapi import HTTPException
from database import SessionLocal
from dataset.domain.dataset import Dataset as DatasetVO
from dataset.domain.repository.dataset_repo import IDatasetRepository
from dataset.infra.db_models.dataset import Dataset
from utils.db_utils import row_to_dict

class DatasetRepository(IDatasetRepository):
    def get_datasets_by_project(
        self,
        project_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[DatasetVO]]:
        with SessionLocal() as db:
            query = (
                db.query(Dataset).filter(Dataset.project_id == project_id)
            )

            total_count = query.count()
            datasets = (
                query.offset((page - 1) * items_per_page)
                .limit(items_per_page).all()
            )

        dataset_vos = [DatasetVO(**row_to_dict(dataset)) for dataset in datasets]

        return total_count, dataset_vos

    def get_datasets_by_flow(
        self,
        flow_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[DatasetVO]]:
        with SessionLocal() as db:
            query = (
                db.query(Dataset).filter(Dataset.flow_id == flow_id)
            )

            total_count = query.count()
            datasets = (
                query.offset((page - 1) * items_per_page)
                .limit(items_per_page).all()
            )

        dataset_vos = [DatasetVO(**row_to_dict(dataset)) for dataset in datasets]

        return total_count, dataset_vos

    def find_by_id(self, id: str) -> DatasetVO:
        with SessionLocal() as db:
            dataset = (
                db.query(Dataset)
                .filter(Dataset.id == id)
                .first()
            )
            if not dataset:
                raise HTTPException(status_code=422)

        return DatasetVO(**row_to_dict(dataset))

    def save(self, dataset_vo: DatasetVO):
        with SessionLocal() as db:
            new_dataset = Dataset(
                id=dataset_vo.id,
                project_id=dataset_vo.project_id,
                flow_id=dataset_vo.flow_id,
                name=dataset_vo.name,
                size=dataset_vo.size,
                path=dataset_vo.path,
            )

            db.add(new_dataset)
            db.commit()

    def update(self, flow_id: str | None, dataset_vo: DatasetVO) -> DatasetVO:
        with SessionLocal() as db:
            dataset = (
                db.query(Dataset)
                .filter(Dataset.id == dataset_vo.id)
                .first()
            )
            if not dataset:
                raise HTTPException(status_code=422)

            dataset.flow_id = flow_id

            db.add(dataset)
            db.commit()

            return DatasetVO(**row_to_dict(dataset))

    def delete(self, project_id: str, id: str):
        with SessionLocal() as db:
            dataset = db.query(Dataset).filter(
                Dataset.project_id == project_id, Dataset.id == id
            ).first()

            if not dataset:
                raise HTTPException(status_code=422)

            db.delete(dataset)
            db.commit()