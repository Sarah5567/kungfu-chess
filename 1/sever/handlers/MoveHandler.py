class MoveHandler:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle(self, data):
        from_pos = tuple(data.get("from"))
        to_pos = tuple(data.get("to"))

        # בדיקה ויישום הלוגיקה
        success = self.game_state.move_piece(from_pos, to_pos)

        if success:
            return {
                "type": "MOVE_CONFIRMED",
                "data": {
                    "from": from_pos,
                    "to": to_pos,
                    "board_state": self.game_state.get_board_state()
                }
            }
        else:
            return {
                "type": "INVALID_MOVE",
                "data": {
                    "message": "Illegal move"
                }
            }
