import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from src.exceptions import DatabaseOperationError
from src.models.incident import Incident
from src.models.technician import Technician


class DatabaseService:
    def __init__(self, database_path: str | Path = "data/incidents.db") -> None:
        self.database_path = Path(database_path)
        if self.database_path.parent != Path("."):
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    def initialize_database(self) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS incidents (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        affected_users INTEGER NOT NULL,
                        reported_by TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        resolved_at TEXT,
                        status TEXT NOT NULL,
                        priority TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS technicians (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        specialty TEXT NOT NULL,
                        active_cases INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        incident_id INTEGER,
                        action TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (incident_id) REFERENCES incidents(id)
                    )
                    """
                )
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot initialize database: {error}") from error

    def save_incident(self, incident: Incident) -> int:
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT OR REPLACE INTO incidents (
                        id, title, description, category, affected_users, reported_by,
                        created_at, resolved_at, status, priority
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        incident.incident_id,
                        incident.title,
                        incident.description,
                        incident.category,
                        incident.affected_users,
                        incident.reported_by,
                        self._format_datetime(incident.created_at),
                        self._format_datetime(incident.resolved_at),
                        incident.status,
                        incident.priority,
                    ),
                )
                incident_id = incident.incident_id or int(cursor.lastrowid)
                incident.incident_id = incident_id
                return incident_id
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot save incident: {error}") from error

    def get_incident(self, incident_id: int) -> Incident | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM incidents WHERE id = ?",
                    (incident_id,),
                ).fetchone()
            return self._row_to_incident(row) if row else None
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot load incident: {error}") from error

    def list_incidents(self) -> list[Incident]:
        try:
            with self._connect() as connection:
                rows = connection.execute("SELECT * FROM incidents ORDER BY id").fetchall()
            return [self._row_to_incident(row) for row in rows]
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot list incidents: {error}") from error

    def update_incident_status(self, incident_id: int, status: str) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    "UPDATE incidents SET status = ? WHERE id = ?",
                    (status, incident_id),
                )
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot update incident status: {error}") from error

    def delete_incident(self, incident_id: int) -> None:
        try:
            with self._connect() as connection:
                connection.execute("DELETE FROM history WHERE incident_id = ?", (incident_id,))
                connection.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot delete incident: {error}") from error

    def save_technician(self, technician: Technician) -> int:
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO technicians (name, specialty, active_cases)
                    VALUES (?, ?, ?)
                    """,
                    (technician.name, technician.specialty, technician.active_cases_count),
                )
                return int(cursor.lastrowid)
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot save technician: {error}") from error

    def add_history(
        self,
        incident_id: int | None,
        action: str,
        old_value: str | None = None,
        new_value: str | None = None,
    ) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO history (incident_id, action, old_value, new_value, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        incident_id,
                        action,
                        old_value,
                        new_value,
                        datetime.now().isoformat(timespec="seconds"),
                    ),
                )
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot save history: {error}") from error

    def list_history(self, incident_id: int | None = None) -> list[dict[str, str | int | None]]:
        query = "SELECT * FROM history"
        params: tuple[int, ...] = ()
        if incident_id is not None:
            query += " WHERE incident_id = ?"
            params = (incident_id,)
        query += " ORDER BY id"

        try:
            with self._connect() as connection:
                rows = connection.execute(query, params).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            raise DatabaseOperationError(f"Cannot list history: {error}") from error

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def _format_datetime(value: datetime | None) -> str | None:
        return value.isoformat(sep=" ", timespec="seconds") if value else None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def _row_to_incident(self, row: sqlite3.Row) -> Incident:
        return Incident(
            incident_id=row["id"],
            title=row["title"],
            description=row["description"],
            category=row["category"],
            affected_users=row["affected_users"],
            reported_by=row["reported_by"],
            created_at=self._parse_datetime(row["created_at"]) or datetime.now(),
            resolved_at=self._parse_datetime(row["resolved_at"]),
            status=row["status"],
            priority=row["priority"],
        )
