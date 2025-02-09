from fastapi import HTTPException
from database import SessionLocal
from config.domain.config import Config as ConfigVO
from config.domain.repository.config_repo import IConfigRepository
from config.infra.db_models.config import Config
from utils.db_utils import row_to_dict

class ConfigRepository(IConfigRepository):
    def find_by_id(self, id: str) -> ConfigVO:
        with SessionLocal() as db:
            config = (
                db.query(Config)
                .filter(Config.id == id)
                .first()
            )
            if not config:
                raise HTTPException(status_code=422)

        return ConfigVO(**row_to_dict(config))

    def find_by_dataset(self, dataset_id) -> ConfigVO:
        with SessionLocal() as db:
            config = (
                db.query(Config)
                .filter(Config.dataset_id == dataset_id)
                .first()
            )
            if not config:
                raise HTTPException(status_code=422)

        return ConfigVO(**row_to_dict(config))

    def save(self, config_vo: ConfigVO):
        with SessionLocal() as db:
            new_config = Config(
                id=config_vo.id,
                dataset_id=config_vo.dataset_id,
                path=config_vo.path,
            )

            db.add(new_config)
            db.commit()

    def delete(self, dataset_id: str, id: str):
        with SessionLocal() as db:
            config = db.query(Config).filter(
                Config.dataset_id == dataset_id, Config.id == id
            ).first()

            if not config:
                raise HTTPException(status_code=422)

            db.delete(config)
            db.commit()