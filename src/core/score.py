from src.input.event_bus import Event

class Score:
    _piece_score = {
        'P': 1,
        'B': 3,
        'N': 3,
        'R': 5,
        'Q': 9,
        'K': 0
    }
    def __init__(self):
        self.score = 0

    def update_score(self, event: Event):
        captured_piece_type = event.data['captured_piece'][0]
        self.score += Score._piece_score[captured_piece_type]
        print(f'black updated score {self.score}')