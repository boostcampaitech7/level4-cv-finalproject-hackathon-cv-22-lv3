from datetime import datetime
from ulid import ULID
from inform.domain.inform import Inform
from inform.domain.repository.inform_repo import IInformRepository

class InformService:
    def __init__(
        self,
        inform_repo: IInformRepository,
    ):
        self.inform_repo = inform_repo
        self.ulid = ULID()

    def get_inform(self, id: str) -> Inform:
        return self.inform_repo.find_by_id(id)

    def get_inform_by_dataset(self, dataset_id: str) -> Inform:
        return self.inform_repo.find_by_dataset(dataset_id)

    def create_inform(
        self,
        dataset_id: str,
    ) -> Inform:
        inform = Inform(
            id=str(self.ulid.generate()),
            dataset_id=dataset_id,
            model_config_path="",
            user_config_path="",
        )

        return self.inform_repo.save(inform)

    def update_inform(
        self,
        id: str,
        config_updates: dict,
    ) -> Inform:
        inform = self.inform_repo.find_by_id(id)
        return self.inform_repo.update(id, config_updates)

    def delete_inform(self, dataset_id: str, id: str):
        return self.inform_repo.delete(dataset_id, id)