from dataclasses import dataclass
from datetime import datetime

@dataclass
class Config:
    id: str
    dataset_id: str
    path: str