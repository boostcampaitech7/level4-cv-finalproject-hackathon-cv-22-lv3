from abc import ABCMeta, abstractmethod
from inform.domain.inform import Inform

class IInformRepository(metaclass=ABCMeta):
    @abstractmethod
    def find_by_id(self, id: str) -> Inform:
        raise NotImplementedError

    @abstractmethod
    def find_by_dataset(self, dataset_id: str) -> Inform:
        raise NotImplementedError

    @abstractmethod
    def save(self, dataset_id: str, inform: Inform) -> Inform:
        raise NotImplementedError

    @abstractmethod
    def delete(self, dataset_id: str, id: str):
        raise NotImplementedError