from fastapi import HTTPException
from database import SessionLocal
from inform.domain.inform import Inform as InformVO
from inform.domain.repository.inform_repo import IInformRepository
from inform.infra.db_models.inform import Inform
from dataset.infra.db_models.dataset import Dataset
from utils.db_utils import row_to_dict
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from process import process_1, process_2, process_3

class InformRepository(IInformRepository):
    def find_by_id(self, id: str) -> InformVO:
        with SessionLocal() as db:
            inform = (
                db.query(Inform)
                .filter(Inform.id == id)
                .first()
            )
            if not inform:
                raise HTTPException(status_code=404, detail="Inform not found")

        return InformVO(**row_to_dict(inform))

    def find_by_dataset(self, dataset_id: str) -> InformVO:
        with SessionLocal() as db:
            inform = (
                db.query(Inform)
                .filter(Inform.dataset_id == dataset_id)
                .first()
            )
            if not inform:
                raise HTTPException(status_code=404, detail="Inform not found")

        return InformVO(**row_to_dict(inform))

    def save(self, inform_vo: InformVO) -> InformVO:
        with SessionLocal() as db:
            dataset = (
                db.query(Dataset)
                .filter(Dataset.id == inform_vo.dataset_id)
                .first()
            )
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            model_config_path, user_config_path, original_df = process_1(dataset.path)

            new_inform = Inform(
                id=inform_vo.id,
                dataset_id=inform_vo.dataset_id,
                model_config_path=model_config_path,
                user_config_path=user_config_path,
            )

            db.add(new_inform)
            db.commit()
            db.refresh(new_inform)

        return InformVO(**row_to_dict(new_inform))

    def update(self, id: str, config_updates: dict) -> InformVO:
        with SessionLocal() as db:
            inform = (
                db.query(Inform)
                .filter(Inform.id == id)
                .first()
            )
            if not inform:
                raise HTTPException(status_code=404, detail="Inform not found")

            dataset = (
                db.query(Dataset)
                .filter(Dataset.id == inform.dataset_id)
                .first()
            )
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            model_config_path = inform.model_config_path
            original_df = pd.read_csv(dataset.path)

            model_config_path, model, test_df, preprocessed_df, preprocessor = process_2(config_updates, model_config_path, original_df)

            db.add(inform)
            db.commit()
            db.refresh(inform)

            return InformVO(**row_to_dict(inform))

    def delete(self, dataset_id: str, id: str):
        with SessionLocal() as db:
            inform = db.query(Inform).filter(
                Inform.dataset_id == dataset_id, Inform.id == id
            ).first()

            if not inform:
                raise HTTPException(status_code=404, detail="Inform not found")

            db.delete(inform)
            db.commit()