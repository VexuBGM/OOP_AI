from pathlib import Path

from src.models.event_args import IncidentEventArgs


class AppLogger:
    def __init__(self, log_path: str | Path = "data/app.log") -> None:
        self.logs: list[str] = []
        self.log_path = Path(log_path)
        if self.log_path.parent != Path("."):
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_args: IncidentEventArgs) -> None:
        log_line = (
            f"[{event_args.created_at:%Y-%m-%d %H:%M:%S}] "
            f"{event_args.event_name}: {event_args.message}"
        )
        self._write_log(log_line)

    def log_critical_incident(self, event_args: IncidentEventArgs) -> None:
        log_line = f"CRITICAL: {event_args.incident.short_info()} needs immediate reaction."
        self._write_log(log_line)

    def _write_log(self, log_line: str) -> None:
        self.logs.append(log_line)
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(f"{log_line}\n")
        print(log_line)
