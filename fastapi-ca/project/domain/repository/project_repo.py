from abc import ABCMeta, abstractmethod
from project.domain.project import Project

class IProjectRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_projects(
        self,
        user_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[Project]]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id: str, id: str) -> Project:
        raise NotImplementedError

    @abstractmethod
    def save(self, user_id: str, project: Project) -> Project:
        raise NotImplementedError

    @abstractmethod
    def update(self, user_id: str, project: Project) -> Project:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: str, id: str):
        raise NotImplementedError