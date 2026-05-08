from src.models.event_args import IncidentEventArgs


class AppLogger:
    def __init__(self) -> None:
        self.logs: list[str] = []

    def log_event(self, event_args: IncidentEventArgs) -> None:
        log_line = (
            f"[{event_args.created_at:%Y-%m-%d %H:%M:%S}] "
            f"{event_args.event_name}: {event_args.message}"
        )
        self.logs.append(log_line)
        print(log_line)

    def log_critical_incident(self, event_args: IncidentEventArgs) -> None:
        log_line = f"CRITICAL: {event_args.incident.short_info()} needs immediate reaction."
        self.logs.append(log_line)
        print(log_line)
