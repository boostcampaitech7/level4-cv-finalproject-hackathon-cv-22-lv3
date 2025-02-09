from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from database import SessionLocal
from project.domain.project import Project as ProjectVO
from project.domain.repository.project_repo import IProjectRepository
from project.infra.db_models.project import Project
from utils.db_utils import row_to_dict

class ProjectRepository(IProjectRepository):
    def get_projects(
        self,
        user_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[ProjectVO]]:
        with SessionLocal() as db:
            query = (
                db.query(Project).filter(Project.user_id == user_id)
            )

            total_count = query.count()
            projects = (
                query.offset((page - 1) * items_per_page)
                .limit(items_per_page).all()
            )

        project_vos = [ProjectVO(**row_to_dict(project)) for project in projects]

        return total_count, project_vos

    def find_by_id(self, user_id: str, id: str) -> ProjectVO:
        with SessionLocal() as db:
            project = (
                db.query(Project)
                .filter(Project.user_id == user_id, Project.id == id)
                .first()
            )
            if not project:
                raise HTTPException(status_code=404, detail="해당 프로젝트를 찾을 수 없습니다.")  # 422 → 404

        return ProjectVO(**row_to_dict(project))


    def save(self, user_id: str, project_vo: ProjectVO):
        with SessionLocal() as db:
            new_project = Project(
                id=project_vo.id,
                user_id=user_id,
                title=project_vo.title,
                description=project_vo.description,
                created_at=project_vo.created_at,
                updated_at=project_vo.updated_at,
            )

            db.add(new_project)
            db.commit()

    def update(self, user_id: str, project_vo: ProjectVO) -> ProjectVO:
        with SessionLocal() as db:
            project = (
                db.query(Project)
                .filter(Project.user_id == user_id, Project.id == project_vo.id)
                .first()
            )
            if not project:
                raise HTTPException(status_code=422)

            project.title = project_vo.title
            project.description = project_vo.description

            db.add(project)
            db.commit()

            return ProjectVO(**row_to_dict(project))

    def delete(self, user_id: str, id: str):
        with SessionLocal() as db:
            project = db.query(Project).filter(
                Project.user_id == user_id, Project.id == id
            ).first()

            if not project:
                raise HTTPException(status_code=422)

            db.delete(project)
            db.commit()