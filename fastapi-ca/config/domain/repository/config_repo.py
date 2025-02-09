from abc import ABCMeta, abstractmethod
from config.domain.config import Config

class IConfigRepository(metaclass=ABCMeta):
    @abstractmethod
    def find_by_id(self, id: str) -> Config:
        raise NotImplementedError

    @abstractmethod
    def find_by_dataset(self, dataset_id: str) -> Config:
        raise NotImplementedError

    @abstractmethod
    def save(self, dataset_id: str, config: Config) -> Config:
        raise NotImplementedError

    @abstractmethod
    def delete(self, dataset_id: str, id: str):
        raise NotImplementedError