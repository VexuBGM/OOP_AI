import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.models.event_args import IncidentEventArgs
from src.models.incident import Incident
from src.services.app_logger import AppLogger


class AppLoggerTests(unittest.TestCase):
    def test_writes_log_events_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "app.log"
            logger = AppLogger(log_path)
            incident = Incident(
                title="Database outage",
                description="Main customer database is down.",
                category="database",
                affected_users=74,
                reported_by="Maria Georgieva",
                priority="high",
            )

            with redirect_stdout(io.StringIO()):
                logger.log_event(
                    IncidentEventArgs(
                        event_name="on_incident_created",
                        incident=incident,
                        message="Created incident.",
                    )
                )

            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn("on_incident_created: Created incident.", log_text)
            self.assertEqual(len(logger.logs), 1)


if __name__ == "__main__":
    unittest.main()
