from src.ai.incident_classifier import IncidentClassifier
from src.events.event_manager import EventManager
from src.models.event_args import IncidentEventArgs
from src.models.incident import Incident


class IncidentManager:
    def __init__(self, classifier: IncidentClassifier, event_manager: EventManager) -> None:
        self.classifier = classifier
        self.event_manager = event_manager
        self.incidents: list[Incident] = []
        self._next_id = 1

    def create_incident(
        self,
        title: str,
        description: str,
        category: str,
        affected_users: int,
        reported_by: str,
    ) -> Incident:
        incident = Incident(
            incident_id=self._next_id,
            title=title,
            description=description,
            category=category,
            affected_users=affected_users,
            reported_by=reported_by,
        )
        self._next_id += 1

        predicted_priority = self.classifier.predict_priority(incident)
        old_priority = incident.change_priority(predicted_priority)
        self.incidents.append(incident)

        self.event_manager.notify(
            "on_incident_created",
            IncidentEventArgs(
                event_name="on_incident_created",
                incident=incident,
                message=f"Created incident {incident.short_info()}.",
            ),
        )

        if old_priority != predicted_priority:
            self.event_manager.notify(
                "on_priority_changed",
                IncidentEventArgs(
                    event_name="on_priority_changed",
                    incident=incident,
                    message=f"Priority changed from {old_priority} to {predicted_priority}.",
                    old_value=old_priority,
                    new_value=predicted_priority,
                ),
            )

        if incident.priority == "high":
            self.event_manager.notify(
                "on_critical_detected",
                IncidentEventArgs(
                    event_name="on_critical_detected",
                    incident=incident,
                    message=f"Critical incident detected: {incident.short_info()}.",
                ),
            )

        return incident
