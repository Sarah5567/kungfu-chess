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
        self.on_enemy_move_callback = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        msg = await self.websocket.recv()
        data = json.loads(msg)
        self.color = data.get("color")
        print(f"[Client] Connected as {self.color}")
        asyncio.create_task(self.listen_for_moves())

    async def listen_for_moves(self):
        try:
            last_sequence = -1
            async for msg in self.websocket:
                try:
                    data = json.loads(msg)
                    
                    # Check if this is a confirmation message
                    if data.get('type') == 'confirm':
                        print(f"[Client] Move {data['sequence']} confirmed by server")
                        continue
                        
                    # Ensure we process moves in sequence
                    if 'sequence' in data:
                        if data['sequence'] <= last_sequence:
                            print(f"[Client] Ignoring duplicate/old move {data['sequence']}")
                            continue
                        last_sequence = data['sequence']
                    
                    print(f"[Client] Received enemy move: {data}")
                    if self.on_enemy_move_callback:
                        await self.on_enemy_move_callback(data)
                        print(f"[Client] Processed move {data.get('sequence', 'unknown')}")
                except json.JSONDecodeError:
                    print("[Client] Received invalid message format")
                except Exception as e:
                    print(f"[Client] Error processing move: {e}")
        except websockets.ConnectionClosed:
            print("[Client] Connection closed.")

    async def send_move(self, move_dict):
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(move_dict))
                print(f"[Client] Sent move: {move_dict}")
                # Wait a short time to ensure the move is processed
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"[Client] Error sending move: {e}")
                # Try to resend the move
                try:
                    await asyncio.sleep(0.5)  # Wait before retrying
                    await self.websocket.send(json.dumps(move_dict))
                    print(f"[Client] Move resent successfully")
                except Exception as e:
                    print(f"[Client] Failed to resend move: {e}")

    def set_on_enemy_move_callback(self, callback):
        """Sets the callback function to handle enemy moves."""
        self.on_enemy_move_callback = callback


def run_game_sync(game):
    """Run the game in synchronous mode"""
    game.run()


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
            
        # Check if this is really an enemy piece
        if piece.get_id()[1].lower() == client.color.lower():
            print("Error: received move for our own piece (ignored).")
            return
            
        print(f"Enemy moved {piece.get_id()} from {source} to {dest}")
        
        # Add command to queue instead of moving directly
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
    
    # Run the game in a separate thread to allow async operations
    import threading
    game_thread = threading.Thread(target=run_game_sync, args=(game,), daemon=True)
    game_thread.start()
    
    # Keep the async event loop running
    try:
        while game_thread.is_alive():
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("Game interrupted")
        game._running = False


if __name__ == "__main__":
    asyncio.run(main())