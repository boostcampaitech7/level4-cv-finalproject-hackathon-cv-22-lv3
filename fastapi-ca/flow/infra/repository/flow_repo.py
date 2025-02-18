from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from database import SessionLocal
from flow.domain.flow import Flow as FlowVO
from flow.domain.repository.flow_repo import IFlowRepository
from flow.infra.db_models.flow import Flow
from utils.db_utils import row_to_dict

class FlowRepository(IFlowRepository):
    def get_flows(
        self,
        project_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[FlowVO]]:
        with SessionLocal() as db:
            query = (
                db.query(Flow).filter(Flow.project_id == project_id)
            )

            total_count = query.count()
            flows = (
                query.offset((page - 1) * items_per_page)
                .limit(items_per_page).all()
            )

        flow_vos = [FlowVO(**row_to_dict(flow)) for flow in flows]

        return total_count, flow_vos

    def find_by_id(self, project_id: str, id: str) -> FlowVO:
        with SessionLocal() as db:
            flow = (
                db.query(Flow)
                .filter(Flow.project_id == project_id, Flow.id == id)
                .first()
            )
            if not flow:
                raise HTTPException(status_code=422)

        return FlowVO(**row_to_dict(flow))

    def save(self, flow_vo: FlowVO):
        with SessionLocal() as db:
            new_flow = Flow(
                id=flow_vo.id,
                project_id=flow_vo.project_id,
                title=flow_vo.title,
                description=flow_vo.description,
                created_at=flow_vo.created_at,
                updated_at=flow_vo.updated_at,
            )

            db.add(new_flow)
            db.commit()

    def update(self, project_id: str, flow_vo: FlowVO) -> FlowVO:
        with SessionLocal() as db:
            flow = (
                db.query(Flow)
                .filter(Flow.project_id == project_id,Flow.id == flow_vo.id)
                .first()
            )
            if not flow:
                raise HTTPException(status_code=422)

            flow.title = flow_vo.title
            flow.content = flow_vo.content
            flow.memo_date = flow_vo.memo_date

            db.add(flow)
            db.commit()

            return FlowVO(**row_to_dict(flow))

    def delete(self, project_id: str, id: str):
        with SessionLocal() as db:
            flow = db.query(Flow).filter(
                Flow.project_id == project_id, Flow.id == id
            ).first()

            if not flow:
                raise HTTPException(status_code=422)

            db.delete(flow)
            db.commit()