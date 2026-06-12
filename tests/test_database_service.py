import tempfile
import unittest
from pathlib import Path

from src.models.incident import Incident
from src.services.database_service import DatabaseService


class DatabaseServiceTests(unittest.TestCase):
    def test_saves_loads_updates_and_deletes_incident(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = DatabaseService(Path(temp_dir) / "test.db")
            incident = Incident(
                title="Database outage",
                description="Main customer database is down.",
                category="database",
                affected_users=74,
                reported_by="Maria Georgieva",
                priority="high",
            )

            incident_id = database.save_incident(incident)
            loaded = database.get_incident(incident_id)

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.title, "Database outage")
            self.assertEqual(loaded.priority, "high")

            database.update_incident_status(incident_id, "resolved")
            updated = database.get_incident(incident_id)
            self.assertEqual(updated.status, "resolved")

            database.delete_incident(incident_id)
            self.assertIsNone(database.get_incident(incident_id))

    def test_saves_history_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = DatabaseService(Path(temp_dir) / "test.db")

            database.add_history(1, "priority_changed", "low", "high")
            history = database.list_history(1)

            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["action"], "priority_changed")
            self.assertEqual(history[0]["old_value"], "low")
            self.assertEqual(history[0]["new_value"], "high")

    def test_clears_demo_database_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = DatabaseService(Path(temp_dir) / "test.db")
            incident = Incident(
                title="Database outage",
                description="Main customer database is down.",
                category="database",
                affected_users=74,
                reported_by="Maria Georgieva",
                priority="high",
            )

            incident_id = database.save_incident(incident)
            database.add_history(incident_id, "created")
            database.clear_all()

            self.assertEqual(database.list_incidents(), [])
            self.assertEqual(database.list_history(), [])


if __name__ == "__main__":
    unittest.main()
