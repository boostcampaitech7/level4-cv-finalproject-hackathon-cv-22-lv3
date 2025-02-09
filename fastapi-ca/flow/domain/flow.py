from dataclasses import dataclass
from datetime import datetime

@dataclass
class Flow:
    id: str
    project_id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime