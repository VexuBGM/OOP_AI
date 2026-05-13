import unittest

from src.services.file_service import FileService
from src.services.incident_stats import IncidentStats


class IncidentStatsTests(unittest.TestCase):
    def setUp(self) -> None:
        incidents = FileService().load_incidents_from_csv("data/sample_incidents.csv")
        self.stats = IncidentStats(incidents)

    def test_counts_incidents_by_priority(self) -> None:
        counts = self.stats.count_by_priority()

        self.assertEqual(counts["high"], 11)
        self.assertEqual(counts["medium"], 10)
        self.assertEqual(counts["low"], 9)

    def test_filters_by_priority(self) -> None:
        high_incidents = self.stats.by_priority("high")

        self.assertEqual(len(high_incidents), 11)
        self.assertTrue(all(incident.priority == "high" for incident in high_incidents))

    def test_calculates_average_resolution_time(self) -> None:
        self.assertAlmostEqual(self.stats.average_resolution_minutes(), 71.3, places=1)

    def test_returns_top_serious_incidents(self) -> None:
        top = self.stats.top_serious_incidents(3)

        self.assertEqual([incident.title for incident in top], [
            "Database outage",
            "Order service timeout",
            "Website error",
        ])


if __name__ == "__main__":
    unittest.main()
