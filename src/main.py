from src.ai.incident_classifier import IncidentClassifier
from src.events.event_manager import EventManager
from src.services.app_logger import AppLogger
from src.services.incident_manager import IncidentManager
from src.services.notification_service import NotificationService


def build_app() -> IncidentManager:
    event_manager = EventManager()
    classifier = IncidentClassifier()
    logger = AppLogger()
    notifications = NotificationService()

    event_manager.subscribe("on_incident_created", logger.log_event)
    event_manager.subscribe("on_priority_changed", logger.log_event)

    event_manager.subscribe("on_critical_detected", logger.log_event)
    event_manager.subscribe("on_critical_detected", logger.log_critical_incident)
    event_manager.subscribe("on_critical_detected", notifications.notify_support_team)

    return IncidentManager(classifier, event_manager)


def main() -> None:
    manager = build_app()

    manager.create_incident(
        title="Database outage",
        description="Main customer database is down and orders cannot be processed.",
        category="database",
        affected_users=74,
        reported_by="Maria Georgieva",
    )

    manager.create_incident(
        title="Printer not responding",
        description="Office printer on floor 2 is not responding.",
        category="hardware",
        affected_users=3,
        reported_by="Georgi Ivanov",
    )


if __name__ == "__main__":
    main()
