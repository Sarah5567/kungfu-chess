from typing import Callable, Dict, List

from enums.EventsNames import EventsNames


class Event:
    def __init__(self, name : EventsNames, data: dict):
        self.name = name
        self.data = data

class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventsNames, List[Callable[[Event], None]]] = {}

    def subscribe(self, topic: EventsNames, callback: Callable[[Event], None]) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    def unsubscribe(self, topic: EventsNames, callback: Callable[[Event], None]) -> None:
        if topic in self._subscribers:
            self._subscribers[topic].remove(callback)

    def publish(self, topic: EventsNames, data: dict) -> None:
        if topic in self._subscribers:
            event = Event(topic, data)
            for callback in self._subscribers[topic]:
                callback(event)

event_bus = EventBus()