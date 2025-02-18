from dataclasses import dataclass
from datetime import datetime

@dataclass
class Dataset:
    id: str
    project_id: str
    flow_id: str | None
    name: str
    size: float
    path: str