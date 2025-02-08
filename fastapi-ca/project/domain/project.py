from dataclasses import dataclass
from datetime import datetime

@dataclass
class Project:
    id: str
    user_id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime