from typing import Any
from EventBus import Event

class Log:
    def __init__(self):
        self.log: list[dict[str, Any]] = []

    def update_log(self, event: Event):
        activity = {
            'time': event.data['time'],
            'source': event.data['source'],
            'destination': event.data['destination']
        }
        if not len(self.log):
            print('list is empty. If it is not the first time, something went wrong')
        self.log.append(activity)
        print(f'log activity {self.log[-1]}')