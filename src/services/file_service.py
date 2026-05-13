import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.exceptions import FileFormatError
from src.models.incident import Incident


class FileService:
    required_incident_fields = {
        "title",
        "description",
        "category",
        "affected_users",
        "reported_by",
        "created_at",
        "resolved_at",
        "status",
        "priority",
    }

    def load_incidents_from_csv(self, file_path: str | Path) -> list[Incident]:
        path = Path(file_path)
        try:
            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                self._validate_fields(reader.fieldnames)
                return [self._dict_to_incident(row) for row in reader]
        except OSError as error:
            raise FileFormatError(f"Cannot read CSV file {path}: {error}") from error
        except ValueError as error:
            raise FileFormatError(f"Invalid CSV data in {path}: {error}") from error

    def save_incidents_to_csv(self, incidents: list[Incident], file_path: str | Path) -> None:
        path = Path(file_path)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(self.required_incident_fields)
        try:
            with path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for incident in incidents:
                    writer.writerow(self._incident_to_dict(incident))
        except OSError as error:
            raise FileFormatError(f"Cannot write CSV file {path}: {error}") from error

    def load_incidents_from_json(self, file_path: str | Path) -> list[Incident]:
        path = Path(file_path)
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of incidents.")
            return [self._dict_to_incident(item) for item in data]
        except (OSError, json.JSONDecodeError, ValueError) as error:
            raise FileFormatError(f"Invalid JSON data in {path}: {error}") from error

    def save_incidents_to_json(self, incidents: list[Incident], file_path: str | Path) -> None:
        path = Path(file_path)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)
        data = [self._incident_to_dict(incident) for incident in incidents]
        try:
            with path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
        except OSError as error:
            raise FileFormatError(f"Cannot write JSON file {path}: {error}") from error

    def _validate_fields(self, fieldnames: list[str] | None) -> None:
        if fieldnames is None:
            raise ValueError("Missing header row.")
        missing_fields = self.required_incident_fields.difference(fieldnames)
        if missing_fields:
            raise ValueError(f"Missing fields: {', '.join(sorted(missing_fields))}.")

    def _dict_to_incident(self, data: dict[str, Any]) -> Incident:
        self._validate_fields(list(data.keys()))
        return Incident(
            title=str(data["title"]),
            description=str(data["description"]),
            category=str(data["category"]),
            affected_users=int(data["affected_users"]),
            reported_by=str(data["reported_by"]),
            created_at=self._parse_datetime(data.get("created_at")) or datetime.now(),
            resolved_at=self._parse_datetime(data.get("resolved_at")),
            status=str(data["status"]),
            priority=str(data["priority"]),
        )

    def _incident_to_dict(self, incident: Incident) -> dict[str, str | int]:
        return {
            "title": incident.title,
            "description": incident.description,
            "category": incident.category,
            "affected_users": incident.affected_users,
            "reported_by": incident.reported_by,
            "created_at": self._format_datetime(incident.created_at),
            "resolved_at": self._format_datetime(incident.resolved_at),
            "status": incident.status,
            "priority": incident.priority,
        }

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        return datetime.fromisoformat(str(value))

    @staticmethod
    def _format_datetime(value: datetime | None) -> str:
        return value.isoformat(sep=" ", timespec="seconds") if value else ""
