import asyncio
from pathlib import Path

import websockets
import json
from websockets.legacy.server import WebSocketServerProtocol, serve
from game_logic.enums.EventsNames import EventsNames
from game_logic.EventBus import event_bus
from game_logic.Board import Board
from game_logic.Game import Game

PORT = 6789

connected_players = set()
player_roles: dict[WebSocketServerProtocol, str] = {}


def create_board():
    return Board(
        cell_H_pix=80,
        cell_W_pix=80,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
    )


board = create_board()

base_path = Path(__file__).resolve().parent.parent
pieces_root = base_path.parent / "PIECES"
placement_csv = base_path / "board.csv"

game = Game(board, pieces_root=pieces_root, placement_csv=placement_csv)  # Fill in paths appropriately


# Publish player commands to the Game's input queue
def publish_input_event(event_type, data):
    event_bus.publish(event_type, data)


# Broadcast board updates to all connected clients
async def handle_board_update(event_data):
    await notify_all(json.dumps({
        "type": EventsNames.BOARD_UPDATE,
        "data": event_data
    }, default=str))


# Broadcast victory message
async def handle_victory(event_data):
    await notify_all(json.dumps({
        "type": EventsNames.VICTORY,
        "data": event_data
    }, default=str))


async def notify_all(message: str):
    if connected_players:
        await asyncio.gather(*(player.send(message) for player in connected_players))


async def handle_connection(websocket: WebSocketServerProtocol):
    if len(connected_players) >= 2:
        await websocket.send(json.dumps({
            "type": "ERROR",
            "data": {"message": "Game is full"}
        }))
        await websocket.close()
        return

    used_roles = set(player_roles.values())
    if "white" not in used_roles:
        role = "white"
    elif "black" not in used_roles:
        role = "black"
    else:
        await websocket.send(json.dumps({
            "type": "ERROR",
            "data": {"message": "Both roles are taken"}
        }))
        await websocket.close()
        return

    player_roles[websocket] = role
    connected_players.add(websocket)

    print(f"Player connected as {role}")
    await websocket.send(json.dumps({
        "type": "ROLE",
        "data": {"role": role}
    }))

    # Send initial piece state to the client
    await websocket.send(json.dumps({
        "type": EventsNames.INIT,
        "data": {'board_state': game.get_board_state(),
                 'cell_H_pix': board.cell_H_pix,
                 'cell_W_pix': board.cell_W_pix,
                 'cell_H_m': board.cell_H_m,
                 'cell_W_m': board.cell_W_m,
                 'W_cells': board.W_cells,
                 'H_cells': board.H_cells}
    }, default=str))

    try:
        async for message in websocket:
            msg = json.loads(message)
            msg_type = msg.get("type")
            raw_params = msg.get("params", {})
            publish_input_event(msg_type, raw_params)

    except websockets.ConnectionClosed:
        print(f"Player {player_roles[websocket]} disconnected")
    finally:
        connected_players.remove(websocket)
        del player_roles[websocket]


async def main():
    # Subscribe to Game output events
    event_bus.subscribe(EventsNames.BOARD_UPDATE, lambda event: asyncio.create_task(handle_board_update(event.data)))
    event_bus.subscribe(EventsNames.VICTORY, lambda event: asyncio.create_task(handle_victory(event.data)))

    # Start WebSocket server properly using async context
    async with serve(handle_connection, "localhost", PORT):
        print(f"WebSocket server started on port {PORT}")
        await asyncio.to_thread(game.run)


if __name__ == "__main__":
    asyncio.run(main())
