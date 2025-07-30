import asyncio
import websockets
import json
from pathlib import Path
from client.UI.Board import Board
from client.UI.EventBus import Event, event_bus
from client.UI.Img import Img
from client.UI.Screen import Screen
from client.UI.Game import Game
from client.UI.enums.EventsNames import EventsNames

async def connect_and_start():
    base_path = Path(__file__).resolve().parent.parent
    pieces_root = base_path.parent / "PIECES"
    placement_csv = base_path / "board.csv"
    sounds_root = base_path.parent / "sounds"
    uri = "ws://localhost:6789"

    try:
        async with websockets.connect(uri) as websocket:
            # קבלת תפקיד
            msg = await websocket.recv()
            data = json.loads(msg)

            if data.get("type") == "ROLE":
                role = data["data"]["role"]
                print(f"Assigned role: {role}")

                board_container = {}
                board_state_container = {}

                def handle_init(event: Event):
                    board_data = event.data
                    board_state_container["board_state"] = board_data['board_state']

                    board = Board(
                        cell_H_pix=board_data['cell_H_pix'],
                        cell_W_pix=board_data['cell_W_pix'],
                        cell_H_m=board_data['cell_H_m'],
                        cell_W_m=board_data['cell_W_m'],
                        W_cells=board_data['W_cells'],
                        H_cells=board_data['H_cells'],
                        img=Img().read("../../board.png", size=(640, 640))
                    )
                    board_container["board"] = board

                event_bus.subscribe(EventsNames.INIT, handle_init)
                event_bus.subscribe(EventsNames.SEND_REQUEST, lambda event: _send_request_to_server(event, websocket))

                listen_task = asyncio.create_task(listen_to_server(websocket))

                # מחכים שה־INIT יגיע מהשרת
                while "board" not in board_container or "board_state" not in board_state_container:
                    await asyncio.sleep(0.05)

                board = board_container["board"]
                board_state = board_state_container["board_state"]

                screen = Screen(['time', 'source', 'destination'], screen_size=(780, 1600), bg_color=(255, 255, 255))
                game = Game(screen, board, pieces_root, placement_csv, sounds_root, websocket, role, board_state)

                await asyncio.gather(
                    listen_task,
                    asyncio.to_thread(game.run)  # הפעלת game.run כמשימה נפרדת
                )

            elif data.get("type") == "ERROR":
                print("Server error:", data["data"]["message"])
            else:
                print("Unexpected message from server:", data)

    except ConnectionRefusedError:
        print("Could not connect to server.")
    except websockets.ConnectionClosed:
        print("Connection closed by server.")

def _send_request_to_server(event: Event, websocket):
    message = {
        "type": event.name,
        "params": event.data
    }
    asyncio.create_task(websocket.send(json.dumps(message)))

async def listen_to_server(websocket):
    while True:
        try:
            msg = await websocket.recv()
            data = json.loads(msg)
            msg_type = data.get("type")

            if msg_type:
                event = Event(name=msg_type, data=data["data"])
                event_bus.publish(msg_type, event)
            else:
                print("Unknown message format:", data)

        except websockets.ConnectionClosed:
            print("Server closed the connection.")
            break

if __name__ == "__main__":
    asyncio.run(connect_and_start())
