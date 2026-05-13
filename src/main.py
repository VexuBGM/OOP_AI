from src.ai.incident_classifier import IncidentClassifier
from src.events.event_manager import EventManager
from src.services.database_service import DatabaseService
from src.services.file_service import FileService
from src.services.app_logger import AppLogger
from src.services.incident_manager import IncidentManager
from src.services.incident_stats import IncidentStats
from src.services.notification_service import NotificationService


def build_app(use_database: bool = False) -> IncidentManager:
    event_manager = EventManager()
    classifier = IncidentClassifier()
    logger = AppLogger()
    notifications = NotificationService()
    database = DatabaseService() if use_database else None

    event_manager.subscribe("on_incident_created", logger.log_event)
    event_manager.subscribe("on_priority_changed", logger.log_event)

    event_manager.subscribe("on_critical_detected", logger.log_event)
    event_manager.subscribe("on_critical_detected", logger.log_critical_incident)
    event_manager.subscribe("on_critical_detected", notifications.notify_support_team)

    return IncidentManager(classifier, event_manager, database)


def main() -> None:
    manager = build_app(use_database=True)

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

    file_service = FileService()
    sample_incidents = file_service.load_incidents_from_csv("data/sample_incidents.csv")
    stats = IncidentStats(sample_incidents)

    print("\nSample data analysis:")
    print(f"Incidents by priority: {stats.count_by_priority()}")
    print(f"Incidents by category: {stats.count_by_category()}")
    print(f"Average resolution time: {stats.average_resolution_minutes():.1f} minutes")


if __name__ == "__main__":
    main()
