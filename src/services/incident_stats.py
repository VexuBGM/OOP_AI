from collections import Counter
from functools import reduce
from itertools import groupby

from src.models.incident import Incident


class IncidentStats:
    def __init__(self, incidents: list[Incident]) -> None:
        self.incidents = incidents

    def by_priority(self, priority: str) -> list[Incident]:
        return list(filter(lambda incident: incident.priority == priority, self.incidents))

    def sorted_by_affected_users(self, descending: bool = True) -> list[Incident]:
        return sorted(
            self.incidents,
            key=lambda incident: incident.affected_users,
            reverse=descending,
        )

    def count_by_priority(self) -> dict[str, int]:
        return dict(Counter(map(lambda incident: incident.priority, self.incidents)))

    def count_by_category(self) -> dict[str, int]:
        sorted_incidents = sorted(self.incidents, key=lambda incident: incident.category)
        return {
            category: len(list(group))
            for category, group in groupby(sorted_incidents, key=lambda incident: incident.category)
        }

    def average_resolution_minutes(self) -> float:
        resolved_minutes = [
            int((incident.resolved_at - incident.created_at).total_seconds() / 60)
            for incident in self.incidents
            if incident.resolved_at is not None
        ]
        if not resolved_minutes:
            return 0.0
        total = reduce(lambda current, value: current + value, resolved_minutes, 0)
        return total / len(resolved_minutes)

    def top_serious_incidents(self, limit: int = 5) -> list[Incident]:
        priority_weight = {"high": 3, "medium": 2, "low": 1}
        serious_incidents = [
            incident
            for incident in self.incidents
            if incident.priority in priority_weight
        ]
        return sorted(
            serious_incidents,
            key=lambda incident: (
                priority_weight[incident.priority],
                incident.affected_users,
            ),
            reverse=True,
        )[:limit]
