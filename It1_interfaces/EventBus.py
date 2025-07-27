from typing import Callable, Dict, List
class Event:
    def __init__(self, name : str, data: dict):
        self.name = name
        self.data = data

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, topic: str, callback: Callable[[Event], None]) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[Event], None]) -> None:
        if topic in self._subscribers:
            self._subscribers[topic].remove(callback)

    def publish(self, topic: str, data: dict) -> None:
        if topic in self._subscribers:
            event = Event(topic, data)
            for callback in self._subscribers[topic]:
                callback(event)

event_bus = EventBus()