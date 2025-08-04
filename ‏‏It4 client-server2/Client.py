import asyncio
import websockets
import json
from pathlib import Path
from Board import Board
from Img import Img
from Screen import Screen
from Game import Game
class Client:
    def __init__(self, uri, game):
        self.uri = uri
        self.websocket = None
        self.color = None
        self.game = game
        self.on_enemy_move = None
    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        msg = await self.websocket.recv()
        data = json.loads(msg)
        self.color = data.get("color")
        print(f"[Client] Connected as {self.color}")
        asyncio.create_task(self.listen_for_moves())
    async def listen_for_moves(self):
        try:
            async for msg in self.websocket:
                data = json.loads(msg)
                print(f"[Client] Received enemy move: {data}")
                if self.on_enemy_move:
                    await self.on_enemy_move(data)  # Pass data directly to the callback
        except websockets.ConnectionClosed:
            print("[Client] Connection closed.")

    async def send_move(self, move_dict):
        if self.websocket:
            await self.websocket.send(json.dumps(move_dict))
            print(f"[Client] Sent move: {move_dict}")

    def set_on_enemy_move_callback(self, callback):
        """Sets the callback function to handle enemy moves."""
        self.on_enemy_move = callback

    async def on_enemy_move(self, move):
        source = tuple(move["from"])
        dest = tuple(move["to"])
        piece = self.game.pos_to_piece.get(source)
        if piece is None:
            print("Enemy move from empty cell.")
            return

        if piece.get_id()[1].lower() == self.color.lower():
            print("Error: received move for our own piece (ignored).")
            return

        print(f"Enemy moved {piece.get_id()} from {source} to {dest}")
        piece.set_pos(dest)  # Update the piece's position directly
        self.game._update_position_mapping()

        from Command import Command
        from enums.StatesNames import StatesNames
        move_type = StatesNames.JUMP if source == dest else StatesNames.MOVE
        cmd = Command(
            timestamp=self.game.game_time_ms(),
            piece_id=piece.get_id(),
            type=move_type,
            params=[self.game.board.cell_to_algebraic(source), self.game.board.cell_to_algebraic(dest)]
        )
        self.game.user_input_queue.put(cmd)
        print("Enemy move command queued.")
async def main():
    base_path = Path(__file__).resolve().parent
    pieces_root = base_path.parent / "PIECES"
    placement_csv = base_path / "board.csv"
    sounds_root = base_path.parent / "sounds"
    board = Board(
        cell_H_pix=80,
        cell_W_pix=80,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=Img().read(str(base_path.parent / "board.png"), size=(640, 640))
    )
    screen = Screen(['time', 'source', 'destination'], screen_size=(780, 1600), bg_color=(255, 255, 255))
    game = Game(screen, board, pieces_root, placement_csv, sounds_root)
    client = Client("ws://localhost:8765", game)
    await client.connect()
    game.set_client(client)  # Pass client to the game for communication
    async def on_enemy_move(move):
        source = tuple(move["from"])
        dest = tuple(move["to"])
        piece = game.pos_to_piece.get(source)
        if piece is None:
            print("Enemy move from empty cell.")
            return
        # במקרה של מהלך היריב, צבע הפיסקה אמור להיות ההפך משלנו
        if piece.get_id()[1].lower() == client.color.lower():
            print("Error: received move for our own piece (ignored).")
            return
        print(f"Enemy moved {piece.get_id()} from {source} to {dest}")
        # הוספת הפקודה ל-queue - לא לזוז ישירות
        from Command import Command
        from enums.StatesNames import StatesNames
        move_type = StatesNames.JUMP if source == dest else StatesNames.MOVE
        cmd = Command(
            timestamp=game.game_time_ms(),
            piece_id=piece.get_id(),
            type=move_type,
            params=[game.board.cell_to_algebraic(source), game.board.cell_to_algebraic(dest)]
        )
        game.user_input_queue.put(cmd)
        print("Enemy move command queued")
    client.set_on_enemy_move_callback(on_enemy_move)
    # הפעלת המשחק בסריקה של הקלט וציור
    game.run()
if __name__ == "__main__":
    asyncio.run(main())
