import tempfile
import unittest
from pathlib import Path

from src.services.file_service import FileService


class FileServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FileService()

    def test_loads_sample_incidents_from_csv(self) -> None:
        incidents = self.service.load_incidents_from_csv("data/sample_incidents.csv")

        self.assertEqual(len(incidents), 30)
        self.assertEqual(incidents[0].title, "Email login fails")
        self.assertEqual(incidents[1].priority, "high")

    def test_writes_and_reads_json(self) -> None:
        incidents = self.service.load_incidents_from_csv("data/sample_incidents.csv")[:2]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "incidents.json"

            self.service.save_incidents_to_json(incidents, output_path)
            loaded = self.service.load_incidents_from_json(output_path)

            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].title, incidents[0].title)
            self.assertEqual(loaded[1].category, incidents[1].category)


if __name__ == "__main__":
    unittest.main()
