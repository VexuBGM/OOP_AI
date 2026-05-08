from src.models.event_args import IncidentEventArgs


class NotificationService:
    def __init__(self) -> None:
        self.notifications: list[str] = []

    def notify_support_team(self, event_args: IncidentEventArgs) -> None:
        text = (
            f"Notify support team: {event_args.incident.title} "
            f"is {event_args.incident.priority} priority."
        )
        self.notifications.append(text)
        print(text)
