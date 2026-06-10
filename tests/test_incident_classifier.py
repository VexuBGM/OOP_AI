import unittest

from src.ai.incident_classifier import IncidentClassifier
from src.exceptions import ClassificationError
from src.models.incident import Incident


class IncidentClassifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = IncidentClassifier()

    def test_predicts_high_priority_for_database_outage(self) -> None:
        incident = Incident(
            title="Database outage",
            description="Main customer database is down.",
            category="database",
            affected_users=74,
            reported_by="Maria Georgieva",
        )

        self.assertEqual(self.classifier.predict_priority(incident), "high")

    def test_predicts_low_priority_for_small_hardware_issue(self) -> None:
        incident = Incident(
            title="Printer not responding",
            description="Office printer on floor 2 is not responding.",
            category="hardware",
            affected_users=3,
            reported_by="Georgi Ivanov",
        )

        self.assertEqual(self.classifier.predict_priority(incident), "low")

    def test_predicts_medium_priority_for_slow_network_issue(self) -> None:
        incident = Incident(
            title="VPN connection slow",
            description="Remote users report slow VPN connection.",
            category="network",
            affected_users=18,
            reported_by="Elena Dimitrova",
        )

        self.assertEqual(self.classifier.predict_priority(incident), "medium")

    def test_matches_most_sample_priorities(self) -> None:
        from src.services.file_service import FileService

        incidents = FileService().load_incidents_from_csv("data/sample_incidents.csv")
        matches = [
            incident
            for incident in incidents
            if self.classifier.predict_priority(incident) == incident.priority
        ]

        self.assertGreaterEqual(len(matches), 27)

    def test_raises_custom_error_for_invalid_incident_data(self) -> None:
        incident = Incident(
            title="",
            description="Invalid incident",
            category="hardware",
            affected_users=-1,
            reported_by="Tester",
        )

        with self.assertRaises(ClassificationError):
            self.classifier.predict_priority(incident)


if __name__ == "__main__":
    unittest.main()
