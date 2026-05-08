from dataclasses import dataclass, field
from datetime import datetime

from src.models.incident import Incident


@dataclass
class IncidentEventArgs:
    event_name: str
    incident: Incident
    message: str
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
