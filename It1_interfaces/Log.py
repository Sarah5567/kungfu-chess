from typing import Any
from EventBus import Event
from datetime import datetime
class Log:
    def __init__(self):
        self.log: list[dict[str, Any]] = []

    def update_log(self, event: Event):
        event_time = event.data.get('time')
        if isinstance(event_time, str):
            try:
                event_time = datetime.fromisoformat(event_time)
            except ValueError:
                print("Invalid time format in event data. Using current time.")
                event_time = datetime.now()
        else:
            event_time = datetime.now()
        activity = {
            'time': event_time.strftime('%H:%M:%S'),  # Format as HH:MM:SS
            'source': event.data['source'],
            'destination': event.data['destination']
        }
        self.log.append(activity)