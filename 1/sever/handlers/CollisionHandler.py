class CollisionHandler:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle(self, data):
        # הדוגמה מדגימה בלבד
        result = self.game_state.detect_collision(data)

        return {
            "type": "COLLISION_RESULT",
            "data": result
        }
