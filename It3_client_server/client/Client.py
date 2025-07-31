import asyncio
import websockets
import json
from pathlib import Path
from client.UI.Board import Board
from client.UI.EventBus import Event, event_bus
from client.UI.Img import Img
from client.UI.Screen import Screen
from client.UI.Game import Game


class GameState:
    def __init__(self):
        self.board = None
        self.board_state = None
        self.role = None
        self.init_received = False


async def connect_and_start():
    base_path = Path(__file__).resolve().parent.parent
    pieces_root = base_path.parent / "PIECES"
    placement_csv = base_path / "board.csv"
    sounds_root = base_path.parent / "sounds"
    uri = "ws://localhost:6789"

    game_state = GameState()

    def handle_init(event: Event):
        try:
            board_data = event.data
            game_state.board_state = board_data['board_state']

            game_board = Board(
                cell_H_pix=board_data['cell_H_pix'],
                cell_W_pix=board_data['cell_W_pix'],
                cell_H_m=board_data['cell_H_m'],
                cell_W_m=board_data['cell_W_m'],
                W_cells=board_data['W_cells'],
                H_cells=board_data['H_cells'],
                img=Img().read("../../board.png", size=(640, 640))
            )
            game_state.board = game_board
            game_state.init_received = True
            print('INIT message received and processed!')
        except Exception as e:
            print(f"Error handling INIT: {e}")

    def handle_role(event: Event):
        game_state.role = event.data["role"]
        print(f"Role assigned: {game_state.role}")

    # Subscribe to events before connecting
    event_bus.subscribe("init", handle_init)
    event_bus.subscribe("ROLE", handle_role)

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to server")

            # Subscribe to send request event
            event_bus.subscribe('SEND_REQUEST',
                                lambda event: asyncio.create_task(_send_request_to_server(event, websocket)))

            # Start listening task
            listen_task = asyncio.create_task(listen_to_server(websocket))

            # Wait for both role and init to be received
            timeout_counter = 0
            max_timeout = 100  # 5 seconds
            while (not game_state.role or not game_state.init_received) and timeout_counter < max_timeout:
                await asyncio.sleep(0.05)
                timeout_counter += 1

            if timeout_counter >= max_timeout:
                print("Timeout waiting for server initialization")
                return

            if not game_state.board or not game_state.board_state or not game_state.role:
                print("Failed to receive complete initialization data")
                return

            print(f"Starting game as {game_state.role}")

            # Create game components
            screen = Screen(['time', 'source', 'destination'], screen_size=(780, 1600), bg_color=(255, 255, 255))
            game = Game(screen, game_state.board, pieces_root, placement_csv, sounds_root, websocket, game_state.role,
                        game_state.board_state)

            # Run the game in a separate thread to avoid blocking the event loop
            game_task = asyncio.create_task(asyncio.to_thread(game.run))

            await asyncio.gather(
                listen_task,
                game_task,
                return_exceptions=True
            )

    except ConnectionRefusedError:
        print("Could not connect to server. Make sure the server is running.")
    except websockets.ConnectionClosed:
        print("Connection closed by server.")
    except Exception as e:
        print(f"Client error: {e}")


async def _send_request_to_server(event: Event, websocket):
    try:
        message = {
            "type": event.name,
            "params": event.data
        }
        await websocket.send(json.dumps(message))
    except websockets.ConnectionClosed:
        print("Cannot send message - connection is closed")
    except Exception as e:
        print(f"Error sending message to server: {e}")


async def listen_to_server(websocket):
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                msg_data = data.get("data", {})

                if msg_type:
                    event = Event(name=msg_type, data=msg_data)
                    event_bus.publish(msg_type, event)
                    print(f"Received message: {msg_type}")
                else:
                    print("Unknown message format:", data)

            except json.JSONDecodeError as e:
                print(f"Invalid JSON received: {e}")
            except Exception as e:
                print(f"Error processing server message: {e}")

    except websockets.ConnectionClosed:
        print("Server closed the connection.")
    except Exception as e:
        print(f"Error in listen_to_server: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(connect_and_start())
    except KeyboardInterrupt:
        print("Client interrupted by user")
    except Exception as e:
        print(f"Client startup error: {e}")