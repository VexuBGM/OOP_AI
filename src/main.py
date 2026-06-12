import argparse

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


def run_final_demo() -> None:
    manager = build_app(use_database=True)
    if manager.database_service is not None:
        manager.database_service.clear_all()

    print("=== Final demo: AI incident management system ===")

    critical_incident = manager.create_incident(
        title="Database outage",
        description="Main customer database is down and orders cannot be processed.",
        category="database",
        affected_users=74,
        reported_by="Maria Georgieva",
    )

    small_incident = manager.create_incident(
        title="Printer not responding",
        description="Office printer on floor 2 is not responding.",
        category="hardware",
        affected_users=3,
        reported_by="Georgi Ivanov",
    )

    file_service = FileService()
    sample_incidents = file_service.load_incidents_from_csv("data/sample_incidents.csv")
    stats = IncidentStats(sample_incidents)

    database = manager.database_service
    saved_incidents = database.list_incidents() if database is not None else []
    history = database.list_history() if database is not None else []

    print("\nCreated incidents:")
    for incident in (critical_incident, small_incident):
        print(f"- {incident.short_info()} | category={incident.category} | users={incident.affected_users}")

    print("\nDatabase check:")
    print(f"Saved incidents in SQLite: {len(saved_incidents)}")
    print(f"History records: {len(history)}")

    print("\nSample data analysis:")
    print(f"Incidents by priority: {stats.count_by_priority()}")
    print(f"Incidents by category: {stats.count_by_category()}")
    print(f"Average resolution time: {stats.average_resolution_minutes():.1f} minutes")

    print("\nTop serious incidents from CSV:")
    for incident in stats.top_serious_incidents(limit=5):
        print(f"- {incident.title} | {incident.priority} | users={incident.affected_users}")

    print("\nAI explanation:")
    print("The classifier adds points for affected users, risky categories and keywords.")
    print("Score 0-2 => low, 3-5 => medium, 6+ => high.")


def run_menu() -> None:
    manager = build_app(use_database=True)
    file_service = FileService()

    while True:
        print("\n=== Incident system menu ===")
        print("1. Create incident")
        print("2. List database incidents")
        print("3. Show CSV statistics")
        print("4. Run final demo")
        print("0. Exit")

        choice = input("Choose option: ").strip()

        if choice == "1":
            title = input("Title: ").strip()
            description = input("Description: ").strip()
            category = input("Category: ").strip()
            affected_users = int(input("Affected users: ").strip())
            reported_by = input("Reported by: ").strip()
            incident = manager.create_incident(
                title=title,
                description=description,
                category=category,
                affected_users=affected_users,
                reported_by=reported_by,
            )
            print(f"Created: {incident.short_info()}")
        elif choice == "2":
            if manager.database_service is None:
                print("Database is not enabled.")
                continue
            incidents = manager.database_service.list_incidents()
            if not incidents:
                print("No incidents saved yet.")
            for incident in incidents:
                print(
                    f"- {incident.short_info()} | {incident.category} | "
                    f"{incident.status} | users={incident.affected_users}"
                )
        elif choice == "3":
            sample_incidents = file_service.load_incidents_from_csv("data/sample_incidents.csv")
            stats = IncidentStats(sample_incidents)
            print(f"Incidents by priority: {stats.count_by_priority()}")
            print(f"Incidents by category: {stats.count_by_category()}")
            print(f"Average resolution time: {stats.average_resolution_minutes():.1f} minutes")
        elif choice == "4":
            run_final_demo()
        elif choice == "0":
            break
        else:
            print("Unknown option.")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI incident management demo")
    parser.add_argument(
        "--menu",
        action="store_true",
        help="Start an interactive console menu instead of the automatic final demo.",
    )
    args = parser.parse_args()

    if args.menu:
        run_menu()
    else:
        run_final_demo()


if __name__ == "__main__":
    main()
