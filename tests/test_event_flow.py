import unittest

from src.ai.incident_classifier import IncidentClassifier
from src.events.event_manager import EventManager
from src.services.incident_manager import IncidentManager


class EventFlowTests(unittest.TestCase):
    def test_high_priority_incident_triggers_all_expected_events(self) -> None:
        event_manager = EventManager()
        manager = IncidentManager(IncidentClassifier(), event_manager)
        received_events: list[str] = []

        def collect_event(event_args) -> None:
            received_events.append(event_args.event_name)

        event_manager.subscribe("on_incident_created", collect_event)
        event_manager.subscribe("on_priority_changed", collect_event)
        event_manager.subscribe("on_critical_detected", collect_event)

        incident = manager.create_incident(
            title="Database outage",
            description="Main customer database is down.",
            category="database",
            affected_users=74,
            reported_by="Maria Georgieva",
        )

        self.assertEqual(incident.priority, "high")
        self.assertEqual(
            received_events,
            ["on_incident_created", "on_priority_changed", "on_critical_detected"],
        )

    def test_low_priority_incident_does_not_trigger_critical_event(self) -> None:
        event_manager = EventManager()
        manager = IncidentManager(IncidentClassifier(), event_manager)
        received_events: list[str] = []

        def collect_event(event_args) -> None:
            received_events.append(event_args.event_name)

        event_manager.subscribe("on_incident_created", collect_event)
        event_manager.subscribe("on_priority_changed", collect_event)
        event_manager.subscribe("on_critical_detected", collect_event)

        incident = manager.create_incident(
            title="Printer not responding",
            description="Office printer on floor 2 is not responding.",
            category="hardware",
            affected_users=3,
            reported_by="Georgi Ivanov",
        )

        self.assertEqual(incident.priority, "low")
        self.assertEqual(received_events, ["on_incident_created"])

    def test_unsubscribe_removes_event_listener(self) -> None:
        event_manager = EventManager()
        received_events: list[str] = []

        def collect_event(event_args) -> None:
            received_events.append(event_args.event_name)

        event_manager.subscribe("on_incident_created", collect_event)
        event_manager.unsubscribe("on_incident_created", collect_event)

        manager = IncidentManager(IncidentClassifier(), event_manager)
        manager.create_incident(
            title="Printer not responding",
            description="Office printer on floor 2 is not responding.",
            category="hardware",
            affected_users=3,
            reported_by="Georgi Ivanov",
        )

        self.assertEqual(received_events, [])


if __name__ == "__main__":
    unittest.main()
