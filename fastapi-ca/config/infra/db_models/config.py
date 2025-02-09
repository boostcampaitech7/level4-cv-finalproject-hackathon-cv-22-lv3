from datetime import datetime
from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Config(Base):
    __tablename__ = "Config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(36), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)