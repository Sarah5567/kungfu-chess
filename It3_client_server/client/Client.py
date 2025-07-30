import asyncio
import websockets
import json
from pathlib import Path
from shared.Board import Board
from shared.EventBus import Event, event_bus
from shared.Img import Img
from Screen import Screen
from Game import Game
from shared.enums.EventsNames import EventsNames


def _send_request_to_server(event: Event, websocket):
    data = event.data
    asyncio.create_task(websocket.send(json.dumps(data)))

async def listen_to_server(websocket):
    while True:
        try:
            msg = await websocket.recv()
            data = json.loads(msg)
            event = Event(name=EventsNames.GET_RESPONSE, data=data)
            event_bus.publish(EventsNames.GET_RESPONSE, event)
        except websockets.ConnectionClosed:
            print("Server closed the connection.")
            break

async def connect_and_start():
    base_path = Path(__file__).resolve().parent.parent
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
        img=Img().read("../../board.png", size=(640, 640))
    )

    screen = Screen(['time', 'source', 'destination'], screen_size=(780, 1600), bg_color=(255, 255, 255))

    uri = "ws://localhost:6789"

    try:
        async with websockets.connect(uri) as websocket:

            msg = await websocket.recv()
            data = json.loads(msg)

            if data.get("type") == "ROLE":
                role = data["data"]["role"]
                print(f"Assigned role: {role}")
                game = Game(screen, board, pieces_root, placement_csv, sounds_root, websocket, role)
                event_bus.subscribe(EventsNames.SEND_REQUEST, lambda event: _send_request_to_server(event, websocket))
                await asyncio.gather(
                    listen_to_server(websocket),
                    game.run()
                )
            elif data.get("type") == "ERROR":
                print("Server error:", data["data"]["message"])
            else:
                print("Unexpected message from server:", data)

    except ConnectionRefusedError:
        print("Could not connect to server.")
    except websockets.ConnectionClosed:
        print("Connection closed by server.")

if __name__ == "__main__":
    asyncio.run(connect_and_start())
