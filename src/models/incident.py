from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Incident:
    title: str
    description: str
    category: str
    affected_users: int
    reported_by: str
    priority: str = "low"
    status: str = "open"
    incident_id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None

    def change_priority(self, new_priority: str) -> str:
        old_priority = self.priority
        self.priority = new_priority
        return old_priority

    def mark_in_progress(self) -> None:
        self.status = "in_progress"

    def resolve(self) -> None:
        self.status = "resolved"
        self.resolved_at = datetime.now()

    def short_info(self) -> str:
        return f"#{self.incident_id or '-'} {self.title} ({self.priority})"
