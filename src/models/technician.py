from dataclasses import dataclass, field

from src.models.incident import Incident


@dataclass
class Technician:
    name: str
    specialty: str
    active_cases: list[Incident] = field(default_factory=list)

    def can_handle(self, incident: Incident) -> bool:
        return self.specialty == incident.category

    def assign_incident(self, incident: Incident) -> None:
        self.active_cases.append(incident)
        incident.mark_in_progress()

    @property
    def active_cases_count(self) -> int:
        return len(self.active_cases)
