from typing import Callable, Dict, List, Any
class Event:
    def __init__(self, name : str, data: dict):
        self.name = name
        self.data = data

class EventBus:
    subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    @staticmethod
    def subscribe(topic: str, callback: Callable[[Event], None]) -> None:
        if topic not in EventBus.subscribers:
            EventBus.subscribers[topic] = []
        EventBus.subscribers[topic].append(callback)

    @staticmethod
    def unsubscribe(topic: str, callback: Callable[[Event], None]) -> None:
        if topic in EventBus.subscribers:
            EventBus.subscribers[topic].remove(callback)

    @staticmethod
    def publish(topic: str, data: dict) -> None:
        if topic in EventBus.subscribers:
            event = Event(topic, data)
            for callback in EventBus.subscribers[topic]:
                callback(event)

