from datetime import datetime
from ulid import ULID
from project.domain.project import Project
from project.domain.repository.project_repo import IProjectRepository

class ProjectService:
    def __init__(
        self,
        project_repo: IProjectRepository,
    ):
        self.project_repo = project_repo
        self.ulid = ULID()

    def get_projects(
        self,
        user_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[Project]]:
        return self.project_repo.get_projects(
            user_id=user_id,
            page=page,
            items_per_page=items_per_page,
        )

    def get_project(self, user_id: str, id: str) -> Project:
        return self.project_repo.find_by_id(user_id, id)

    def create_project(
        self,
        user_id: str,
        title: str,
        description: str,
    ) -> Project:
        now = datetime.now()

        project = Project(
            id=self.ulid.generate(),
            user_id=user_id,
            title=title,
            description=description,
            created_at=now,
            updated_at=now,
        )

        self.project_repo.save(user_id, project)

        return project

    def update_project(
        self,
        user_id: str,
        id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> Project:
        project = self.project_repo.find_by_id(user_id, id)
        if title:
            project.title = title
        if description:
            project.description = description

        return self.project_repo.update(user_id, project)

    def delete_project(self, user_id: str, id: str):
        return self.project_repo.delete(user_id, id)