from datetime import datetime
from ulid import ULID
from config.domain.config import Config
from config.domain.repository.config_repo import IConfigRepository

class ConfigService:
    def __init__(
        self,
        config_repo: IConfigRepository,
    ):
        self.config_repo = config_repo
        self.ulid = ULID()

    def get_config(self, id: str) -> Config:
        return self.config_repo.find_by_id(id)

    def get_config_by_dataset(self, dataset_id: str) -> Config:
        return self.config_repo.find_by_dataset(id)

    def create_config(
        self,
        id: str,
        dataset_id: str,
        path: str,
    ) -> Config:
        config = Config(
            id=self.ulid.generate(),
            dataset_id=dataset_id,
            path=path,
        )

        self.config_repo.save(config)

        return config

    def delete_config(self, dataset_id: str, id: str):
        return self.config_repo.delete(dataset_id, id)