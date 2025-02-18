from dataclasses import dataclass
from datetime import datetime

@dataclass
class Inform:
    id: str
    dataset_id: str
    model_config_path: str
    user_config_path: str