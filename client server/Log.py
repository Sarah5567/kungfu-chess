from typing import Any
from EventBus import Event
from datetime import datetime
class Log:
    def __init__(self):
        self.log: list[dict[str, Any]] = []

    def update_log(self, event: Event):
        event_time = event.data.get('time')
        if isinstance(event_time, (int, float)):
            # Convert milliseconds to HH:MM:SS format
            seconds = event_time / 1000  # Convert ms to seconds
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            seconds = int(seconds % 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            print("Invalid time format in event data")
            time_str = "00:00:00"

        activity = {
            'time': time_str,
            'source': event.data['source'],
            'destination': event.data['destination']
        }
        self.log.append(activity)