from typing import Any
from EventBus import Event

class Log:
    white_log: list[dict[str, Any]] = []
    black_log: list[dict[str, Any]] = []

    @staticmethod
    def update_log(event: Event):
        activity = {
            'time': event.data['time'],
            'source': event.data['source'],
            'destination': event.data['destination']
        }
        if event.data['player'] == 'B':
            Log.black_log.append(activity)
            print(f'black player:\n time: {activity['time']} \nsource: {activity['source']} \ndestination: {activity['destination']}')
        else:
            Log.white_log.append(activity)
            print(f'white player:\n time: {activity['time']} \nsource: {activity['source']} \ndestination: {activity['destination']}')
