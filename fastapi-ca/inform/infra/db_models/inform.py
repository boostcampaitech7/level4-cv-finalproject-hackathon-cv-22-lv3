from datetime import datetime
from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Inform(Base):
    __tablename__ = "Inform"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(36), nullable=False)
    model_config_path: Mapped[str] = mapped_column(Text, nullable=False)
    user_config_path: Mapped[str] = mapped_column(Text, nullable=False)