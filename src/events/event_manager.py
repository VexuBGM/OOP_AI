from collections import defaultdict
from collections.abc import Callable

from src.models.event_args import IncidentEventArgs


EventCallback = Callable[[IncidentEventArgs], None]


class EventManager:
    def __init__(self) -> None:
        self._listeners: dict[str, list[EventCallback]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: EventCallback) -> None:
        self._listeners[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: EventCallback) -> None:
        if callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    def notify(self, event_name: str, event_args: IncidentEventArgs) -> None:
        for callback in self._listeners[event_name]:
            callback(event_args)
