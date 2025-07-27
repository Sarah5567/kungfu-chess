from urllib3.util.util import to_str

from EventBus import Event

class Score:
    piece_score = {
        'P': 1,
        'B': 3,
        'K': 3,
        'R': 5,
        'Q': 9,
    }
    score_white = 0
    score_black = 0

    @staticmethod
    def update_score(event: Event):
        captured_piece_type = event.data['captured_piece'][0]
        if event.data['capture_piece'][1] == 'B':
            Score.score_black += Score.piece_score[captured_piece_type]
            print(f'black updated score {Score.score_black}')
        else:
            Score.score_white += Score.piece_score[captured_piece_type]
            print(f'white updated score {Score.score_white}')

