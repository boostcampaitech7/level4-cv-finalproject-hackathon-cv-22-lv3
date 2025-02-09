from datetime import datetime
from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Dataset(Base):
    __tablename__ = "Dataset"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    flow_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[float] = mapped_column(Float, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)